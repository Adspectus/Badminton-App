#!/usr/bin/perl

use constant { TRUE => 1, FALSE => 0, BASE => $ENV{'VIRTUAL_ROOT'} };
use lib '/srv/www/perl-lib',BASE . '/perl-lib';
use open qw( :encoding(UTF-8) :std );
use strict;
use utf8;
use warnings;
use Badminton::DB;
use Badminton::Functions qw(:all);
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use CGI::Session;
use CGI::Session::Auth::DBI;
use Config::Merge;
use Data::Dumper;
use POSIX qw(locale_h ceil);
use Text::Markdown::Discount;
use Time::Piece;
use Time::Seconds;
use WebSite::Template;
use WebSite::Framework::Bootstrap;

$Data::Dumper::Indent = 1;
$Data::Dumper::Purity = 0;

setlocale(LC_ALL, "de_DE.UTF-8");

my $Config = Config::Merge->new('path' => BASE . '/config','is_local' => qr/local/i);


###############################################################################
#
# Main Settings
#
###############################################################################

my $CGI           = CGI->new();
my $Session       = CGI::Session->new(undef, $CGI, {Directory=>'/tmp'});


###############################################################################
#
# Exit if in Maintenance Mode
#
###############################################################################

if (-e BASE . '/.maintenance') {
  my $Template = WebSite::Template->new({'TemplatePath' => BASE . '/htdocs/lib/templates','TemplateFile' => 'bootstrap-navbar_basic.template'});
  my $Content  = $CGI->h1('Sorry...').$CGI->p('Die Site ist wegen Systemarbeiten derzeit offline.');
  $Template->setVar('Content',$CGI->div({-class => 'jumbotron'},$Content));
  print $Session->header(-charset => 'UTF-8');
  print $Template->print();
  exit;
}


###############################################################################
#
# Browser Check: Exit if not compatible
#
###############################################################################

my $UA = $CGI->user_agent();

if ($UA =~ /Mozilla\/4/ or $UA =~ /bot/i) {
  my $Template = WebSite::Template->new({'TemplatePath' => BASE . '/htdocs/lib/templates','TemplateFile' => 'bootstrap-navbar_basic.template'});
  my $Content  = $CGI->h1('Sorry...').$CGI->p('Du benutzt keinen unterstützten Browser.');
  $Template->setVar('Content',$CGI->div({-class => 'jumbotron'},$Content));
  print $Session->header(-charset => 'UTF-8');
  print $Template->print();
  exit;
}


###############################################################################
#
# Authentication: Show Logonform and exit if login failed
#
###############################################################################

my $DB    = Badminton::DB->new({'Host' => $Config->('DB.Host'),'Database' => $Config->('DB.Database'),'DB_User' => $Config->('DB.User'),'DB_Pass' => $Config->('DB.Password')});
my $Auth  = CGI::Session::Auth::DBI->new({CGI => $CGI,Session => $Session,LoginVarPrefix => $Config->('UI.LoginVarPrefix'),DBHandle => $DB->get('Handle'),'EncryptPW' => 1,'PasswordField' => 'password'});

$Auth->authenticate();

my $NavBars = NavBars->new({'Brand' => $CGI->a({-class => 'navbar-brand-logo',-href => '/'},$CGI->img({-alt => $Config->('UI.Title'),-src => '/lib/images/Badminton-Logo-64.png',-height => 48})).$CGI->p({-class => 'h3 navbar-text'},$Config->('UI.Title'))});

unless ($Auth->loggedIn) {
  my $Template = WebSite::Template->new({'TemplatePath' => BASE . '/htdocs/lib/templates','TemplateFile' => 'bootstrap-navbar_basic.template'});
  $Template->setVar('Title',$Config->('UI.Title'));
  $Template->setVar('NavBar',$NavBars->output('Title'));
  my $Button = &HTML::Button({-id => 'Anmelden',-class => 'btn btn-primary btn-lg btn-block',-type => 'submit'},$CGI->span({-class => 'h2'},'Anmelden'));
  my $LogonForm = $CGI->start_form({-id => 'Anmelden',-class => 'form-horizontal',-method => 'POST',-novalidate => 'novalidate'}).$CGI->div({-class => 'form-group form-group-lg'},$CGI->label({-for => 'username',-class => 'sr-only control-label'},'Benutzername').$CGI->div({-class => 'col-sm-offset-3 col-sm-6'},$CGI->input({-type => 'EMail',-class => 'form-control',-id => 'username',-name => $Config->('UI.LoginVarPrefix').'username',-placeholder => 'Benutzername',-autofocus => 'autofocus'}))).$CGI->div({-class => 'form-group form-group-lg'},$CGI->label({-for => 'password',-class => 'sr-only control-label'},'Passwort').$CGI->div({-class => 'col-sm-offset-3 col-sm-6'},$CGI->input({-type => 'password',-class => 'form-control',-id => 'password',-name => $Config->('UI.LoginVarPrefix').'password',-placeholder => 'Passwort'}))).$CGI->div({-class => 'form-group form-group-lg'},$CGI->div({-class => 'col-sm-offset-3 col-sm-6'},$Button)).$CGI->end_form();
  $Template->setVar('Content',$CGI->div({-class => 'jumbotron'},$LogonForm));
  print $Session->header(-charset => 'UTF-8');
  print $Template->print();
  exit;
}

$CGI->delete($Config->('UI.LoginVarPrefix').'username',$Config->('UI.LoginVarPrefix').'password');


###############################################################################
#
# Authenticated!
#
###############################################################################

my $Players     = $DB->getPlayers()->{'Data'};
my $CurrentUser = $Players->{$Auth->profile('userid')};


###############################################################################
#
# Check for active user and exit if not active
#
###############################################################################

unless ($CurrentUser->{'Active'}) {
  my $Template = WebSite::Template->new({'TemplatePath' => BASE . '/htdocs/lib/templates','TemplateFile' => 'bootstrap-navbar_basic.template'});
  $Template->setVar('Title',$Config->('UI.Title'));
  $Template->setVar('NavBar',$NavBars->output('Title'));
  my $Content = $CGI->h1('Sorry...').$CGI->p('Du bist kein aktiver Teilnehmer. Wende Dich an einen Administrator.');
  $Template->setVar('Content',$CGI->div({-class => 'jumbotron'},$Content));
  print $Session->header(-charset => 'UTF-8');
  print $Template->print();
  exit;
}


###############################################################################
#
# Now, everything is ok, lets go and get some data
#
###############################################################################

chomp(my $VERSION        = `git describe`);
my ($TAG,$COMMITS)       = split(/-/,$VERSION,2);
my $AppConfig            = $DB->get('Config');
my $PlayTime             = '19:30';
my $TP_Now               = Time::Piece->new;
my $ThisYear             = $TP_Now->year; # &getDateFormatted('Year');
my $LastYear             = $ThisYear - 1;
my $Years                = { map { $_ => 1 } ($ThisYear,$LastYear) };
my $Holidays             = &getHolidays();

my $Participation        = $DB->getParticipationByUser({'UserID' => $Auth->profile('userid')})->{'Data'};
my $Contributions        = $DB->getContributions({'Year' => $ThisYear})->{'Data'};
my $NextMatchday         = $DB->getNextMatchday()->{'Data'};
my $TP_NextMatch         = Time::Piece->strptime($NextMatchday.' '.$PlayTime,"%Y-%m-%d %R");
my $DayBefore            = &getDayBefore($NextMatchday);
my $TP_Deadline          = $TP_NextMatch - $Config->('Settings.ParticipationDeadline');
my $NextMatchdays        = $DB->getNextMatchdays({'Limit' => $Config->('UI.NextMatchdays')})->{'Data'};
my $PastMatchdays        = $DB->getPastMatchdays()->{'Data'};
my $CourtsByDate         = $DB->getCourtsByDate({'Date' => $NextMatchday})->{'Data'};
my $ParticipationByDate  = $DB->getParticipationByDate({'Date' => $NextMatchday})->{'Data'};
my $Guests               = $DB->getGuests()->{'Data'};
my $ClosedMatchdays      = { map { $_ => $PastMatchdays->{$_} } grep { $PastMatchdays->{$_}->{'Closed'} == 1 and exists($Years->{substr($_,0,4)}) } keys(%{$PastMatchdays}) };
my $ClosedMatchdayByYear = {};
$ClosedMatchdayByYear->{substr($_,0,4)}->{$_} = $ClosedMatchdays->{$_} foreach (keys(%{$ClosedMatchdays}));
my $Holiday              = $Holidays->{$NextMatchday} || '';
my %PlayerNameByID       = map { $_ => $Players->{$_}->{'Lastname'}.', '.$Players->{$_}->{'Firstname'} } keys(%{$Players});
my %StatusByDate         = map { $_ => $Participation->{$_}->{'Status'} } ($NextMatchday,@{$NextMatchdays});
my %FormDefaults         = ('LabelClass' => 'col-md-2','Class' => 'col-md-4','HelpClass' => 'col-md-6');


#******************************************************************************
# Startseite
#******************************************************************************

my $Start = NavBar->new({'ID' => 'start','Order' => 0,'Title' => 'Startseite'});

#****************************************
# Abstimmung und Status
#****************************************

# Get Data
my $DateString          = $CGI->p({-class => 'h1 text-center visible-xs-block'},&getDateFormatted('Short',$NextMatchday).$CGI->br.$CGI->small($Holiday)) . $CGI->p({-class => 'h1 text-center hidden-xs'},&getDateFormatted('Long',$NextMatchday).$CGI->br.$CGI->small($Holiday));
my $Zusagen             = &HTML::Button({-id => 'Zusagen',-type => 'button',-class => 'btn btn-success btn-lg btn-block'},$CGI->span({-class => 'h2'},'Zusagen'));
#my $Zugesagt           = &HTML::Button({-type => 'button',-class => 'btn btn-success btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Du hast zugesagt'));
my $Zugesagt            = $CGI->span({-class => 'h2 text-success'},'Du hast zugesagt');
my $Absagen             = &HTML::Button({-id => 'Absagen',-type => 'button',-class => 'btn btn-danger btn-lg btn-block'},$CGI->span({-class => 'h2'},'Absagen'));
#my $Abgesagt           = &HTML::Button({-type => 'button',-class => 'btn btn-danger btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Du hast abgesagt'));
my $Abgesagt            = $CGI->span({-class => 'h2 text-danger'},'Du hast abgesagt');
my @Zusagen             = map { $CGI->span({-class => 'h3'},$Players->{$_}->{'Firstname'}.'&nbsp;'.$Players->{$_}->{'Lastname'}.($ParticipationByDate->{$_}->{'OnTime'} ? '' : '&nbsp;'.$CGI->small(&Helpers::Icon('time','red')))) } sort { $Players->{$a}->{'SortID'} <=> $Players->{$b}->{'SortID'} } @{&getParticipants($ParticipationByDate)};
my @Guests              = map { $CGI->span({-class => 'h3'},$Guests->{$_}->{'Firstname'}.'&nbsp;'.$Guests->{$_}->{'Lastname'}.'&nbsp;(Gast)') } sort { $Guests->{$a}->{'Lastname'} cmp $Guests->{$b}->{'Lastname'} } grep { $Guests->{$_}->{'Date'} eq $NextMatchday } keys(%{$Guests});
push(@Zusagen,@Guests);
my $ZusagenString       = scalar(@Zusagen).' Teilnehmer';
$ZusagenString          = 'Keine Teilnehmer' unless (scalar(@Zusagen));
$ZusagenString          = '1 Teilnehmer' if (scalar(@Zusagen) eq '1');
my $ZusagenListe        = Modal->new({'ID' => 'ZusagenListe','Header' => $CGI->span({-class => 'h3'},$ZusagenString),'Body' => join($CGI->br,@Zusagen),'Footer' => 'OK','ContentClass' => 'modal-content-success','Size' => 'small'});
my $ZusagenStringExt    = $ZusagenString.($CourtsByDate->[1] ? '&nbsp;&ndash;&nbsp;'.$CourtsByDate->[0].'&nbsp;Spielzeiten' : '');
my $ZusagenButton       = '';
$ZusagenButton          = &HTML::Button({-data_target => '#ZusagenListe',-data_toggle => 'modal',-type => 'button',-class => 'btn btn-lg btn-info btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h3'},$ZusagenStringExt)) unless (scalar(@Zusagen));
$ZusagenButton          = &HTML::Button({-data_target => '#ZusagenListe',-data_toggle => 'modal',-type => 'button',-class => 'btn btn-lg btn-info btn-block'},$CGI->span({-class => 'h3'},$ZusagenStringExt)) if (scalar(@Zusagen));

# Set Content
if ($AppConfig->{'0'}->{$ThisYear}->{'Fee'}->{'Setting'} and ! $Contributions->{$Auth->profile('userid')}->{'FeeStatus'}) {
#unless ($Contributions->{$Auth->profile('userid')}->{'FeeStatus'}) {
  $Start->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 bg-danger text-center Large'},'Dein Eigenbeitrag '.$ThisYear.' ist fällig!')));
  $Start->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h2({-class => 'text-center'},'Nächster Spieltag') . $DateString)));
}
else {
  $Start->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h2({-class => 'text-center'},'Nächster Spieltag') . $DateString)));
}
$Start->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$Start->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 col-sm-offset-3 col-md-offset-4 text-center'},$ZusagenButton)));
$Start->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$Start->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$Start->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 col-sm-offset-3 col-md-offset-4 text-center'},$StatusByDate{$NextMatchday} == 1 ? $Zugesagt : $Abgesagt)));
$Start->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$Start->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 col-sm-offset-3 col-md-offset-4 text-center'},$StatusByDate{$NextMatchday} == 1 ? $Absagen : $Zusagen)));
$Start->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));

if ($TP_Now->epoch < $TP_Deadline->epoch - $TP_Deadline->localtime->tzoffset) {
  $Start->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p({-class => 'text-center'},'Rechtzeitig '.($StatusByDate{$NextMatchday} == 1 ? 'ab' : 'zu').'sagen bis: '.&getDateFormatted('AbbrLong+Time',$TP_Deadline).' Uhr!'))));
}
else {
  $Start->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p({-class => 'text-center'},'Deine '.($StatusByDate{$NextMatchday} == 1 ? 'Ab' : 'Zu').'sage wird zu spät sein!'))));
}
$Start->appendPane($ZusagenListe->output());

$NavBars->append($Start);

my $NavOrder = 0;

#****************************************
# Meine Daten
#****************************************

my $PersData    = NavBar->new({'ID' => 'persdata','Order' => ++$NavOrder,'Title' => 'Meine Daten'});

# Create Forms
my $PD_Save   = &HTML::Button({-id => 'PD_Save',-type => 'button',-class => 'btn btn-primary btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Speichern'));
my $PD_Cancel = &HTML::Button({-id => 'PD_Cancel',-type => 'button',-class => 'btn btn-info btn-lg btn-block'},$CGI->span({-class => 'h2'},'Verwerfen'));
my $PW_Save   = &HTML::Button({-id => 'PW_Save',-type => 'button',-class => 'btn btn-primary btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Speichern'));
my $PW_Cancel = &HTML::Button({-id => 'PW_Cancel',-type => 'button',-class => 'btn btn-info btn-lg btn-block'},$CGI->span({-class => 'h2'},'Verwerfen'));

my $PDForm = $CGI->start_form({-id => 'PersonalData',-class => 'form-horizontal',-action => ''});
$PDForm .= Element->new({'ID' => 'PD_Vorname','Name' => 'Vorname','Value' => $CurrentUser->{'Firstname'},'Disabled' => TRUE,%FormDefaults})->output();
$PDForm .= Element->new({'ID' => 'PD_Nachname','Name' => 'Nachname','Value' => $CurrentUser->{'Lastname'},'Disabled' => TRUE,%FormDefaults})->output();
$PDForm .= Element->new({'ID' => 'PD_Benutzername','Name' => 'Benutzername','Value' => $Auth->profile('username'),%FormDefaults})->output();
$PDForm .= Element->new({'ID' => 'PD_EMail','Type' => 'EMail','Name' => 'EMail','Label' => 'E-Mail-Adresse','Value' => $CurrentUser->{'EMail'},%FormDefaults})->output();
$PDForm .= $CGI->div({-id => 'PD_PhoneNumber',-class => 'form-group'},$CGI->label({-for => 'PD_PhoneNumber',-class => 'col-md-2 control-label'},'Telefon').$CGI->div({-class => 'col-md-2'},$CGI->input({-type => 'text',-id => 'PD_PhoneNumber_GC',-name => 'Telefon_GC',-class => 'form-control',-placeholder => 'Vorwahl',-value => ($CurrentUser->{'GeoCode'} ? '0'.$CurrentUser->{'GeoCode'} : '')})).$CGI->div({-class => 'col-md-2'},$CGI->input({-type => 'text',-id => 'PD_PhoneNumber_SC',-name => 'Telefon_SC',-class => 'form-control',-placeholder => 'Rufnummer',-value => $CurrentUser->{'SubscriberCode'}})).$CGI->div({-id => 'PD_PhoneNumber_Help',-class => 'col-md-6 help-block',-name => 'Telefon_Help'},''));
$PDForm .= Element->new({'ID' => 'PD_Geburtstag','Name' => 'Geburtstag','Value' => defined($CurrentUser->{'Birthday'}) ? &getDateFormatted('Tiny',$CurrentUser->{'Birthday'}) : '',%FormDefaults})->output();
$PDForm .= Element->new({'ID' => 'PD_Default_Status','Type' => 'Checkbox','Name' => 'Default_Status','Label' => 'Teilnahmestatus','Checked' => $CurrentUser->{'Default_Status'},%FormDefaults})->output();
$PDForm .= Element->new({'ID' => 'PD_UserID','Type' => 'Hidden','Name' => 'UserID','Value' => $Auth->profile('userid')})->output();
$PDForm .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 col-md-offset-2 text-center'},$PD_Save).$CGI->div({-class => 'col-xs-12 visible-xs-block'},'&nbsp;') . $CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 text-center'},$PD_Cancel));
$PDForm .= $CGI->end_form();

my $PW_Form = $CGI->start_form({-id => 'ChangePassword',-class => 'form-horizontal',-action => ''});
$PW_Form .= Element->new({'ID' => 'PW_Passwort','Type' => 'Password','Name' => 'Passwort','Label' => 'Neues Passwort',%FormDefaults})->output();
$PW_Form .= Element->new({'ID' => 'PW_Passwort2','Type' => 'Password','Name' => 'Passwort2','Label' => 'Passwort wiederholen','Disabled' => TRUE,%FormDefaults})->output();
$PW_Form .= Element->new({'ID' => 'PW_UserID','Type' => 'Hidden','Name' => 'UserID','Value' => $Auth->profile('userid')})->output();
$PW_Form .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 col-md-offset-2 text-center'},$PW_Save).$CGI->div({-class => 'col-xs-12 visible-xs-block'},'&nbsp;') . $CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 text-center'},$PW_Cancel));
$PW_Form .= $CGI->end_form();

# Set Content
$PersData->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-10 col-md-offset-2'},$CGI->h1('Meine Daten'))));
$PersData->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$PersData->appendPane($PDForm);
$PersData->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$PersData->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$PersData->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-10 col-md-offset-2'},$CGI->h2('Passwort ändern'))));
$PersData->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$PersData->appendPane($PW_Form);
$PersData->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));

$NavBars->append($PersData);


#****************************************
# Meine Teilnahme
#****************************************

my $MyParticipation = Dropdown->new({'ID' => 'userparticipation','Title' => 'Teilnahme'});
my $MyParticipOrder = 0;

#****************************************
# Bisherige Teilnahme
#****************************************

my $PastPart   = Dropdown::Element->new({'ID' => 'pastpart','Order' => ++$MyParticipOrder,'Title' => 'Bisherige Teilnahme'});


# Get Data
my $PastParticipation = {};
foreach my $date (keys(%{$Participation})) {
  next unless ($Participation->{$date}->{'Final'});
  my $year = substr($date,0,4);
  $PastParticipation->{$year}->{'CountTeilnahme'}++ if ($Participation->{$date}->{'Status'} == 1);
  $PastParticipation->{$year}->{'CountTeilnahmeOffTime'}++ if ($Participation->{$date}->{'Status'} == 1 and $Participation->{$date}->{'OnTime'} == 0);
  $PastParticipation->{$year}->{'CountAbsage'}++ if ($Participation->{$date}->{'Status'} == 0);
  $PastParticipation->{$year}->{'CountAbsageOffTime'}++ if ($Participation->{$date}->{'Status'} == 0 and $Participation->{$date}->{'OnTime'} == 0);
}

my $PP_Content = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},$CGI->h2('Es gibt keine abgeschlossenen Spieltage.')));
my @PP_Content = ();
my $PP_i = 0;
foreach my $year (reverse(sort(keys(%{$ClosedMatchdayByYear})))) {
  $PastParticipation->{$year}->{'CountTeilnahme'} = 0 unless (defined($PastParticipation->{$year}->{'CountTeilnahme'}));
  $PastParticipation->{$year}->{'CountTeilnahmeOffTime'} = 0 unless (defined($PastParticipation->{$year}->{'CountTeilnahmeOffTime'}));
  $PastParticipation->{$year}->{'CountAbsage'} = 0 unless (defined($PastParticipation->{$year}->{'CountAbsage'}));
  $PastParticipation->{$year}->{'CountAbsageOffTime'} = 0 unless (defined($PastParticipation->{$year}->{'CountAbsageOffTime'}));

  $PP_Content[$PP_i]  = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},$CGI->h2($year . ':&nbsp;' . scalar(keys(%{$ClosedMatchdayByYear->{$year}})).' Spieltag'.(scalar(keys(%{$ClosedMatchdayByYear->{$year}})) == 1 ? '' : 'e'))));
#  $PP_Content[$PP_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},$CGI->h3(scalar(keys(%{$ClosedMatchdayByYear->{$year}})).' Spieltage')));

  unless ($PastParticipation->{$year}->{'CountTeilnahme'} + $PastParticipation->{$year}->{'CountAbsageOffTime'}) {
    $PP_Content[$PP_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},&HTML::large({},'Du hast nie teilgenommen oder abgesagt.')));
    $PP_Content[$PP_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    $PP_i++;
    next;
  }
  $PP_Content[$PP_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},&HTML::large({},'Du hast '.($PastParticipation->{$year}->{'CountTeilnahme'} > 0 ? $PastParticipation->{$year}->{'CountTeilnahme'}.' mal' : 'nie').' teilgenommen und '.(($PastParticipation->{$year}->{'CountTeilnahmeOffTime'} + $PastParticipation->{$year}->{'CountAbsageOffTime'}) > 0 ? ($PastParticipation->{$year}->{'CountTeilnahmeOffTime'} + $PastParticipation->{$year}->{'CountAbsageOffTime'}).' mal' : 'nie').' zu spät zu- oder abgesagt.')));
  $PP_Content[$PP_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));

  my @Rows;
  foreach my $date (reverse(sort(keys(%{$ClosedMatchdayByYear->{$year}})))) {
    my $Status = (exists($Participation->{$date}->{'Status'}) && $Participation->{$date}->{'Status'} == 1) ? &Helpers::Icon('ok','green') : &Helpers::Icon('remove','black');
    my $OffTimeTitle = 'Deine '.($Participation->{$date}->{'Status'} ? 'Zusage' : 'Absage').' kam zu spät.';
    my $OffTimeWarning = $Participation->{$date}->{'OnTime'} ? '' : $CGI->span({-data_toggle => 'tooltip',-data_placement => 'left',-title => $OffTimeTitle},&Helpers::Icon('time','red'));
    push(@Rows,$CGI->Tr($CGI->td($CGI->span({-class => 'large visible-xs-inline'},&getDateFormatted('Tiny',$date)) . $CGI->span({-class => 'h3 hidden-xs'},&getDateFormatted('Medium',$date))),$CGI->td({-align => 'right'},$CGI->table($CGI->Tr($CGI->td({-width => '30px',-align => 'right'},[$CGI->span({-class => 'large visible-xs-inline'},$Status).$CGI->span({-class => 'h3 hidden-xs'},$Status),'&nbsp;',$CGI->span({-class => 'large visible-xs-inline'},$OffTimeWarning).$CGI->span({-class => 'h3 hidden-xs'},$OffTimeWarning)]))))));
  }
  $PP_Content[$PP_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},$CGI->table({-class => 'table'},$CGI->thead($CGI->Tr($CGI->th('&nbsp;'),$CGI->th('&nbsp;'))),$CGI->tbody(@Rows,$CGI->Tr($CGI->td(['&nbsp;','&nbsp;']))))));

  $PP_Content[$PP_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
  $PP_i++;
}
$PP_Content = join('',@PP_Content) if (scalar(@PP_Content));

# Set Content
$PastPart->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},$CGI->h1('Bisherige Teilnahme'))));
$PastPart->appendPane($PP_Content);

# Include Content
$MyParticipation->appendElement($PastPart);


#****************************************
# Zukünftige Teilnahme
#****************************************

my $FutPart   = Dropdown::Element->new({'ID' => 'futpart','Order' => ++$MyParticipOrder,'Title' => 'Zukünftige Teilnahme'});

# Get Data
my $Sum = 0;
my @FP_Rows;
foreach my $date (@{$NextMatchdays}) {
  my $DateString = $CGI->span({-class => 'large visible-xs-inline'},&getDateFormatted('Tiny',$date)) . $CGI->span({-class => 'h3 hidden-xs'},&getDateFormatted('Medium',$date));
  my $Holiday = $Holidays->{$date} || '';
  $StatusByDate{$date} = -1 unless (defined($StatusByDate{$date}));
  $Sum += $StatusByDate{$date};
  my $Switch = '';
  $Switch = $CGI->input({-type => 'checkbox',-name => 'Teilnahme_'.$date,-checked => 'true'}) if ($StatusByDate{$date} == 1 or ($StatusByDate{$date} == -1 and $CurrentUser->{'Default_Status'} == 1));
  $Switch = $CGI->input({-type => 'checkbox',-name => 'Teilnahme_'.$date}) if ($StatusByDate{$date} == 0 or ($StatusByDate{$date} == -1 and $CurrentUser->{'Default_Status'} == 0));
  push(@FP_Rows,$CGI->Tr($CGI->td($DateString.$CGI->br.$CGI->small($Holiday)),$CGI->td({-class => 'text-right'},$Switch)));
}

my $DefaultSwitch = '';
$DefaultSwitch = &HTML::Button({-id => 'FP_Defaults',-type => 'button',-class => 'btn btn-lg btn-primary',-disabled => 'disabled'},'Standardeinstellung wird verwendet') if ($Sum == -8);
$DefaultSwitch = &HTML::Button({-id => 'FP_Defaults',-type => 'button',-class => 'btn btn-lg btn-primary'},'Standardeinstellung verwenden') unless ($Sum == -8);
my $FP_Table   = $CGI->table({-class => 'table'},$CGI->tbody({-class => 'table-striped'},@FP_Rows,$CGI->Tr($CGI->td(''),$CGI->td(''))));

# Create Form
my $FP_Form = $CGI->start_form({-id => 'FutureParticipation',-action => ''}).$FP_Table.$CGI->end_form();

# Set Content
$FutPart->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h1('Zukünftige Teilnahme'))));
$FutPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$FutPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$FutPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$DefaultSwitch)));
$FutPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$FutPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$FutPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$FP_Form)));
$FutPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));


# Include Content
$MyParticipation->appendElement($FutPart);


#****************************************
# Protokoll
#****************************************

my $ActivityLog = Dropdown::Element->new({'ID' => 'activitylog','Order' => ++$MyParticipOrder,'Title' => 'Mein Protokoll'});

# Get Data
my $Log_Cols  = ['Datum','Von','Aktivität'];
my $Log_Table = $CGI->table({-id => 'ActivityLog',-class => 'table table-striped'},$CGI->thead($CGI->Tr($CGI->th($Log_Cols))),$CGI->tfoot($CGI->Tr($CGI->th($Log_Cols))));

# Set Content
$ActivityLog->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h1('Mein Protokoll'))));
$ActivityLog->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$ActivityLog->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->div({-class => 'table-responsive'},$Log_Table))));
$ActivityLog->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));

# Include Content
$MyParticipation->appendElement($ActivityLog);


$NavBars->append(NavBar->new({$MyParticipation->toNavBar(),'Order' => ++$NavOrder}));


#****************************************
# Gast anmelden
#****************************************

my $GuestPart = NavBar->new({'ID' => 'guestpart','Order' => ++$NavOrder,'Title' => 'Gäste'});

# Get Data
my @DateValues = ($NextMatchday,@{$NextMatchdays});
if ($Auth->isGroupMember('superadmin') or $Auth->isGroupMember('admin')) {
  unshift(@DateValues,grep { $PastMatchdays->{$_}->{'Closed'} == 0 } sort(keys(%{$PastMatchdays})));
}
my $DateLabels = { map { $_ => &getDateFormatted('AbbrLong',$_) } @DateValues };
my @ActivePlayerValues = sort { $Players->{$a}->{'SortID'} <=> $Players->{$b}->{'SortID'} } grep { $Players->{$_}->{'Active'} == 1 } keys(%{$Players});

# Create Form
my $GuestForm = $CGI->start_form({-id => 'Guests',-class => 'form-horizontal',-action => ''});
$GuestForm .= Element->new({'ID' => 'Guest_Date','Type' => 'ScrollingList','Name' => 'Date','Label' => 'Datum','Values' => [@DateValues],'Labels' => $DateLabels,'Default' => [$NextMatchday],%FormDefaults})->output();
$GuestForm .= $CGI->div({-id => 'Guest_Vorname',-class => 'form-group'},$CGI->label({-for => 'Guest_Vorname',-class => 'col-md-2 control-label'},'Vorname').$CGI->div({-class => 'col-md-4'},$CGI->input({-type => 'text',-id => 'Guest_VorName',-class => 'form-control',-name => 'Vorname',-placeholder => 'Vorname des Gastes'})).$CGI->div({-id => 'Guest_Vorname_Help',-class => 'col-md-6 help-block',-name => 'Vorname_Help'},''));
$GuestForm .= $CGI->div({-id => 'Guest_Nachname',-class => 'form-group'},$CGI->label({-for => 'Guest_Nachname',-class => 'col-md-2 control-label'},'Nachname').$CGI->div({-class => 'col-md-4'},$CGI->input({-type => 'text',-id => 'Guest_Nachname',-class => 'form-control',-name => 'Nachname',-placeholder => 'Nachname des Gastes'})).$CGI->div({-id => 'Guest_Nachname_Help',-class => 'col-md-6 help-block',-name => 'Nachname_Help'},''));
if ($Auth->isGroupMember('superadmin') or $Auth->isGroupMember('admin')) {
  $GuestForm .= Element->new({'ID' => 'Guest_Host','Type' => 'ScrollingList','Name' => 'Host','Label' => 'Gast von','Values' => [@ActivePlayerValues],'Labels' => { %PlayerNameByID },'Default' => [$Auth->profile('userid')],%FormDefaults})->output();
}
$GuestForm .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 col-md-offset-2 text-center'},&HTML::Button({-id => 'Guest_Save',-type => 'button',-class => 'btn btn-primary btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Speichern'))).$CGI->div({-class => 'col-xs-12 visible-xs-block'},'&nbsp;') . $CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 text-center'},&HTML::Button({-id => 'Guest_Cancel',-type => 'button',-class => 'btn btn-info btn-lg btn-block'},$CGI->span({-class => 'h2'},'Verwerfen'))));
$GuestForm .= $CGI->end_form();

# Set Content
$GuestPart->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h1('Gäste'))));
my $Intro = 'Hier kannst Du einen oder mehrere Gäste für einen Spieltag anmelden oder wieder löschen. ';
if ($Auth->isGroupMember('superadmin') or $Auth->isGroupMember('admin')) {
  $Intro .= 'Der Gastbeitrag beträgt '.$AppConfig->{'0'}->{$ThisYear}->{'GuestContribution'}->{'Setting'}.' €, mit denen der ausgewählte Teilnehmer belastet wird.';
}
else {
  $Intro .= 'Du kannst nur die Gäste löschen, die auf Deinen Namen angemeldet sind. Der Gastbeitrag beträgt '.$AppConfig->{'0'}->{$ThisYear}->{'GuestContribution'}->{'Setting'}.' €, die auf Deinen Namen belastet werden.';
}
$GuestPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p($Intro))));
$GuestPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$GuestPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h3('Gast anmelden:'))));
$GuestPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$GuestPart->appendPane($GuestForm);
$GuestPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$GuestPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));


foreach my $date ($NextMatchday,@{$NextMatchdays}) {
  my @Guests = grep { $Guests->{$_}->{'Date'} eq $date } keys(%{$Guests});
  next unless (scalar(@Guests));
  $GuestPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h3('Gäste am '.&getDateFormatted('Simple',$date).':'))));
  $GuestPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
  my $i = 0;
  foreach my $guest (@Guests) {
    $i++;
    my $Button = '';
    my $Host = '';
    if ($Guests->{$guest}->{'UserID'} == $Auth->profile('userid') or ($Auth->isGroupMember('superadmin') or $Auth->isGroupMember('admin'))) {
      $Button = &HTML::Button({-id => 'DelGuest_'.$guest,-class => 'btn btn-danger',-type => 'button',-data_date => $date,-data_guest => $guest},&Helpers::Icon('trash','white'));
    }
    unless ($Guests->{$guest}->{'UserID'} == $Auth->profile('userid')) {
      $Host = '(Gast von '.$Players->{$Guests->{$guest}->{'UserID'}}->{'Firstname'}.'&nbsp;'.$Players->{$Guests->{$guest}->{'UserID'}}->{'Lastname'}.')';
    }
    $GuestPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'large col-xs-9 col-sm-3'},$Guests->{$guest}->{'Firstname'}.'&nbsp;'.$Guests->{$guest}->{'Lastname'}).$CGI->div({-class => 'large col-xs-3 visible-xs-block text-right'},$Button).$CGI->div({-class => 'large col-xs-12 col-sm-6'},$Host).$CGI->div({-class => 'large hidden-xs col-sm-3 text-right'},$Button)));
    $GuestPart->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->hr()))) if (scalar(@Guests) > $i);
  }
}


# Include Content
$NavBars->append($GuestPart);


#******************************************************************************
#
# Tab: Hilfe
#
#******************************************************************************

my $HelpOrder = 0;

my $Help = Dropdown->new({'ID' => 'help','Title' => 'Hilfe'});


#****************************************
# Hilfetext
#****************************************

my $HelpText = Dropdown::Element->new({'ID' => 'helptext','Order' => ++$HelpOrder,'Title' => 'Allgemeine Hilfe'});

# Get Data
my $HelpContent = '';
if (open(FILE,BASE . '/htdocs/lib/md/hilfe.md')) {
  $HelpContent = do { local $/; <FILE> };
  close FILE;
}

# Replace Placeholders
my $Organisation = $Config->('UI.Organisation');
$HelpContent =~ s/<!--\s+Organisation\s+-->/$Organisation/g;
my $AppMail = $Config->('Email.FromMail');
$HelpContent =~ s/<!--\s+AppMail\s+-->/<$AppMail>/g;
my $Admins = join(" oder ",map { $Players->{$_}->{'Firstname'}.' '.$Players->{$_}->{'Lastname'}.' (<'.$Players->{$_}->{'EMail'}.'>)' } @{$DB->getAdmins()->{'Data'}});
$HelpContent =~ s/<!--\s+Admins\s+-->/$Admins/g;

# Set Content
$HelpText->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},Text::Markdown::Discount::markdown($HelpContent))));

# Include Content
$Help->appendElement($HelpText);


#****************************************
# Teilnehmerübersicht
#****************************************

my $ListPlayer = Dropdown::Element->new({'ID' => 'listplayer','Order' => ++$HelpOrder,'Title' => 'Teilnehmerübersicht'});

# Get Data
my $LP_Cols  = ['','Name','Status','Benutzername','E-Mail','Telefon'];
my $LP_Table = $CGI->table({-id => 'ListPlayers',-class => 'table table-striped'},$CGI->thead($CGI->Tr($CGI->th($LP_Cols))));

# Set Content
$ListPlayer->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h1('Teilnehmerübersicht'))));
$ListPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p('Diese Übersicht zeigt dir alle Teilnehmer (aktive und passive) der Badmintongruppe. Du kannst die Liste kopieren, drucken oder als PDF abspeichern. Über den Filter kannst Du die Anzeige einschränken.'))));
$ListPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$ListPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->div({-class => 'table-responsive'},$LP_Table))));
$ListPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));

# Include Content
$Help->appendElement($ListPlayer);


#****************************************
# Trennlinie
#****************************************

$Help->appendElement(Dropdown::Element->new({'ID' => 'divider'.$HelpOrder,'Order' => ++$HelpOrder}));


#****************************************
# Information
#****************************************

$Help->appendElement(Dropdown::Element->new({'ID' => 'nolink'.$HelpOrder,'Order' => ++$HelpOrder,'Title' => 'Version '.$VERSION}));


#****************************************
# Hilfe-Dropdown zur NavBar
#****************************************

$NavBars->append(NavBar->new({$Help->toNavBar(),'Order' => ++$NavOrder}));


#******************************************************************************
#
# Tab: Administration
#
#******************************************************************************

if ($Auth->isGroupMember('superadmin') or $Auth->isGroupMember('admin')) {

  my $AdminOrder     = 0;
  my $ActivePlayers  = { map { $_ => $Players->{$_} } grep { $Players->{$_}->{'Active'} == 1 } keys(%{$Players}) };

  my $PastCourts = {};
  foreach my $date (keys(%{$ClosedMatchdays})) {
    my $year = substr($date,0,4);
    $PastCourts->{$year} += $ClosedMatchdays->{$date}->{'Courts'};
  }

  my $Birthdays      = {};
  foreach my $id (keys(%{$ActivePlayers})) {
    next unless (defined($ActivePlayers->{$id}->{'Birthday'}));
    next if ($id == $Auth->profile('userid'));
    push(@{$Birthdays->{substr($ActivePlayers->{$id}->{'Birthday'},5,5)}},$ActivePlayers->{$id}->{'Firstname'}.' '.$ActivePlayers->{$id}->{'Lastname'});
  }

  my $Administration  = Dropdown->new({'ID' => 'admin','Title' => 'Verwaltung'});


#****************************************
# Spielzeiten festlegen
#****************************************

  my $SetCourts = Dropdown::Element->new({'ID' => 'setcourts','Order' => ++$AdminOrder,'Title' => 'Spielzeiten festlegen'});

# Get Data
  my $NextMatchdayCourts = $CourtsByDate->[0];
  my $CourtsSuggestion   = &getCourtsFromPlayers(scalar(@Zusagen));

# Create Form
  my $SC_Buttons       = join("",map { $CGI->label({-name => 'CourtsSet',-data_date => $NextMatchday,-class => 'btn '.($_ == $NextMatchdayCourts ? 'btn-primary active' : ($_ == $CourtsSuggestion ? 'btn-success' : 'btn-default'))},($NextMatchdayCourts == $_ ? $CGI->input({-type => 'radio',-name => 'CourtsSet',-value => $_,-autocomplete => 'off',-checked => 'true'},$_) : $CGI->input({-type => 'radio',-name => 'CourtsSet',-value => $_,-autocomplete => 'off'},$_))) } (1..15));
  my $SC_ScrollingList = $CGI->scrolling_list(-name => 'CourtsSetScroll',-class => 'form-control',-values => [1..15],-size => 1,-default => [$NextMatchdayCourts],-labels => {$CourtsSuggestion => $CourtsSuggestion.' - Empfehlung'});
  my $SC_Form          = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-2'},$CGI->h4('Spielzeiten:')).$CGI->div({-class => 'text-right hidden-xs col-sm-10'},$CGI->div({-class => 'btn-group',-data_toggle => 'buttons'},$SC_Buttons)).$CGI->div({-class => 'text-right visible-xs-block col-xs-offset-4 col-xs-6'},$SC_ScrollingList));
  my $SC_Save          = &HTML::Button({-id => 'SC_Save',-name => 'SC_Save',-data_date => $NextMatchday,-type => 'button',-class => 'btn btn-primary btn-lg btn-block'},$CGI->span({-class => 'h2'},'Speichern'));
  my $SC_Cancel        = &HTML::Button({-id => 'SC_Cancel',-name => 'SC_Cancel',-data_date => $NextMatchday,-type => 'button',-class => 'btn btn-info btn-lg btn-block'},$CGI->span({-class => 'h2'},'Verwerfen'));

# Set Content
  $SetCourts->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h1('Spielzeiten festlegen'))));
  $SetCourts->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p('Hier legst Du die gebuchten Plätze für den <b>nächsten</b> Spieltag fest.'))));
  $SetCourts->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h3(&getDateFormatted('Medium',$NextMatchday)))));
  $SetCourts->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p($ZusagenString.'&nbsp;&ndash;&nbsp;Empfehlung: '.$CourtsSuggestion.' Spielzeiten '))));
  $SetCourts->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
  $SetCourts->appendPane($CGI->start_form({-id => 'SetCourts_'.$NextMatchday,-action => ''}).$SC_Form.$CGI->end_form());
  $SetCourts->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 hidden-xs'},'&nbsp;')));
  $SetCourts->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p({-id => 'SetCourtsExplanation',-class => 'text-right hidden-xs'},'&nbsp;').$CGI->p({-id => 'SetCourtsExplanationXS',-class => 'text-right visible-xs-block'},'&nbsp;'))));
#  $SetCourts->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p({-id => 'SetCourtsExplanation'},'&nbsp;'))));
  $SetCourts->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
  $SetCourts->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 col-md-offset-2 text-center'},$SC_Save).$CGI->div({-class => 'col-xs-12 visible-xs-block'},'&nbsp;') . $CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 text-center'},$SC_Cancel)));


# Include Content
  $Administration->appendElement($SetCourts);


#****************************************
# Trennlinie
#****************************************

  $Administration->appendElement(Dropdown::Element->new({'ID' => 'divider'.$AdminOrder,'Order' => ++$AdminOrder}));


#****************************************
# Spieltag abschließen
#****************************************

  my $CloseMatchday   = Dropdown::Element->new({'ID' => 'closeday','Order' => ++$AdminOrder,'Title' => 'Spieltag abschließen'});

# Get Data
  my $OpenMatchdays = { map { $_ => $PastMatchdays->{$_} } grep { $PastMatchdays->{$_}->{'Closed'} == 0 } keys(%{$PastMatchdays}) };

  my $CM_Content = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h3('Es gibt keinen offenen Spieltag.')));

  my @CM_Content = ();
  my $CM_i = 0;
  foreach my $date (sort(keys(%{$OpenMatchdays}))) {
    my $Buttons = join("",map { $CGI->label({-name => 'Courts',-data_date => $date,-class => 'btn '.($OpenMatchdays->{$date}->{'Courts'} == $_ ? 'btn-primary active' : 'btn-default')},($OpenMatchdays->{$date}->{'Courts'} == $_ ? $CGI->input({-type => 'radio',-name => 'Courts',-value => $_,-autocomplete => 'off',-checked => 'true'},$_) : $CGI->input({-type => 'radio',-name => 'Courts',-value => $_,-autocomplete => 'off'},$_))) } (1..15));
    my $ScrollingList = $CGI->scrolling_list(-name => 'CourtsScroll',-class => 'form-control',-values => [1..15],-size => 1,-default => [$OpenMatchdays->{$date}->{'Courts'}]);
    my $CM_Form = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-3'},$CGI->span({-class => 'large visible-xs-inline'},'Spielzeiten:').$CGI->span({-class => 'h3 hidden-xs'},'Spielzeiten:')).$CGI->div({-class => 'text-right hidden-xs col-sm-9'},$CGI->div({-class => 'btn-group',-data_toggle => 'buttons'},$Buttons)).$CGI->div({-class => 'text-right visible-xs-block col-xs-offset-3 col-xs-6'},$ScrollingList));
    $CM_Form .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    $CM_Form .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));

    my $ParticipationByDate = $DB->getParticipationByDate({'Date' => $date})->{'Data'};

    my @Rows = ();
    foreach my $userid (sort { $Players->{$a}->{'SortID'} <=> $Players->{$b}->{'SortID'} } grep { $ParticipationByDate->{$_}->{'Status'} > -1 } keys(%{$ParticipationByDate})) {
      my $Name = $CGI->span({-class => 'large visible-xs-inline'},$Players->{$userid}->{'Firstname'}.'&nbsp;'.$Players->{$userid}->{'Lastname'}) . $CGI->span({-class => 'h3 hidden-xs'},$Players->{$userid}->{'Firstname'}.'&nbsp;'.$Players->{$userid}->{'Lastname'});
      my $Switch = '';
      $Switch = $CGI->input({-type => 'checkbox',-name => 'Player_'.$userid,-data_date => $date,-data_player => $userid,-checked => 'true'}) if ($ParticipationByDate->{$userid}->{'Status'} == 1);
      $Switch = $CGI->input({-type => 'checkbox',-name => 'Player_'.$userid,-data_date => $date,-data_player => $userid}) if ($ParticipationByDate->{$userid}->{'Status'} == 0);
      push(@Rows,$CGI->Tr($CGI->td({-class => 'text-left'},$Name),$CGI->td({-class => 'text-right'},$Switch)));
    }

    my @Guests = grep { $Guests->{$_}->{'Date'} eq $date } keys(%{$Guests});

    foreach my $guest (@Guests) {
      my $Name = $CGI->span({-class => 'large visible-xs-inline'},$Guests->{$guest}->{'Firstname'}.'&nbsp;'.$Guests->{$guest}->{'Lastname'}.'&nbsp;(Gast)') . $CGI->span({-class => 'h3 hidden-xs'},$Guests->{$guest}->{'Firstname'}.'&nbsp;'.$Guests->{$guest}->{'Lastname'}.' (Gast von '.$Players->{$Guests->{$guest}->{'UserID'}}->{'Firstname'}.'&nbsp;'.$Players->{$Guests->{$guest}->{'UserID'}}->{'Lastname'}.')');
      my $Switch = '';
      $Switch = $CGI->input({-type => 'checkbox',-name => 'Guest_'.$guest,-data_date => $date,-checked => 'true'});
      push(@Rows,$CGI->Tr($CGI->td({-class => 'text-left'},$Name),$CGI->td({-class => 'text-right'},$Switch)));
    }

    $CM_Form .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->table({-class => 'table'},$CGI->tbody({-class => 'table-striped'},@Rows,$CGI->Tr($CGI->td(''),$CGI->td(''))))));
    my $CM_Save   = &HTML::Button({-id => 'CM_Save_'.$date,-name => 'CM_Save',-data_date => $date,-type => 'button',-class => 'btn btn-primary btn-lg btn-block'},$CGI->span({-class => 'h2'},'Speichern'));
    my $CM_Cancel = &HTML::Button({-id => 'CM_Cancel_'.$date,-name => 'CM_Cancel',-data_date => $date,-type => 'button',-class => 'btn btn-info btn-lg btn-block'},$CGI->span({-class => 'h2'},'Verwerfen'));

    $CM_Content[$CM_i] = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h3(&getDateFormatted('Medium',$date))));
    $CM_Content[$CM_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    $CM_Content[$CM_i] .= $CGI->start_form({-id => 'CloseMatchday_'.$date,-action => ''}).$CM_Form.$CGI->end_form();
    $CM_Content[$CM_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    $CM_Content[$CM_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 col-md-offset-2 text-center'},$CM_Save).$CGI->div({-class => 'col-xs-12 visible-xs-block'},'&nbsp;') . $CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 text-center'},$CM_Cancel));
    $CM_Content[$CM_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    $CM_Content[$CM_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    $CM_i++;
  }
  $CM_Content = join('',@CM_Content) if (scalar(@CM_Content));

# Set Content
  $CloseMatchday->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h1('Spieltag abschließen'))));
  $CloseMatchday->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p('Hier kannst Du offene Spieltage abschließen. Ein Spieltag ist offen, wenn die Abstimmung für die Teilnehmer beendet wurde (Donnerstags um 19:30 Uhr). Als Admin musst Du dann angeben, wieviele Spielzeiten gebucht waren und wer tatsächlich teilgenommen hat. Nicht vorangemeldete Gäste können im Menü &lt;Gäste&gt; hinzugefügt werden. Nur abgeschlossene Spieltage erscheinen in der Statistik.'))));
  $CloseMatchday->appendPane($CM_Content);

# Include Content
  $Administration->appendElement($CloseMatchday);


#****************************************
# Bisherige Spieltage
#****************************************

  my $PastMatchday = Dropdown::Element->new({'ID' => 'pastdays','Order' => ++$AdminOrder,'Title' => 'Bisherige Spieltage'});

# Get Data
  my $PM_Content = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},$CGI->h2('Es gibt keine abgeschlossenen Spieltage.')));
  my @PM_Content = ();
  my $PM_i = 0;

  foreach my $year (reverse(sort(keys(%{$ClosedMatchdayByYear})))) {
    $PM_Content[$PM_i]  = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},$CGI->h2($year)));
    $PM_Content[$PM_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},$CGI->h3(scalar(keys(%{$ClosedMatchdayByYear->{$year}})).' Spieltag'.(scalar(keys(%{$ClosedMatchdayByYear->{$year}})) == 1 ? '' : 'e').' &mdash; '.$PastCourts->{$year}.' Court'.($PastCourts->{$year} == 1 ? '' : 's'))));
    $PM_Content[$PM_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));

    my $PM_Accordion = Accordion->new();
    my $PM_Panel = [];
    my $p = 0;
    foreach my $date (reverse(sort(keys(%{$ClosedMatchdayByYear->{$year}})))) {
      my $DateString = $CGI->span({-class => 'large visible-xs-inline'},&getDateFormatted('Tiny',$date)) . $CGI->span({-class => 'h3 hidden-xs'},&getDateFormatted('Medium',$date));
      my $ParticipationByDate = $DB->getParticipationByDate({'Date' => $date})->{'Data'};
      my @Zusagen = map { $CGI->span({-class => 'h3'},$Players->{$_}->{'Firstname'}.'&nbsp;'.$Players->{$_}->{'Lastname'}.($ParticipationByDate->{$_}->{'OnTime'} ? '' : '&nbsp;'.$CGI->small(&Helpers::Icon('time','red')))) } sort { $Players->{$a}->{'SortID'} <=> $Players->{$b}->{'SortID'} } @{&getParticipants($ParticipationByDate)};
      my @Absagen = map { $CGI->span({-class => 'h3'},$Players->{$_}->{'Firstname'}.'&nbsp;'.$Players->{$_}->{'Lastname'}.($ParticipationByDate->{$_}->{'OnTime'} ? '' : '&nbsp;'.$CGI->small(&Helpers::Icon('time','red')))) } sort { $Players->{$a}->{'SortID'} <=> $Players->{$b}->{'SortID'} } @{&getNonParticipants($ParticipationByDate)};
      my @Passive = map { $CGI->span({-class => 'h3'},$Players->{$_}->{'Firstname'}.'&nbsp;'.$Players->{$_}->{'Lastname'}) } sort { $Players->{$a}->{'SortID'} <=> $Players->{$b}->{'SortID'} } @{&getPassive($ParticipationByDate)};
      my @Guests  = grep { $Guests->{$_}->{'Date'} eq $date } keys(%{$Guests});
      my $CountZusagen = scalar(@Zusagen) ? scalar(@Zusagen) : 'Keine';
      my $CountAbsagen = scalar(@Absagen) ? scalar(@Absagen) : 'Keine';
      my $CountPassive = scalar(@Passive) ? scalar(@Passive) : 'Keine';
      my $CountGuests  = scalar(@Guests) ? scalar(@Guests) : 'Keine';
      my $CountPlayer  = scalar(@Zusagen) + scalar(@Guests) ? scalar(@Zusagen) + scalar(@Guests) : 'Keine';

      my $ZusagenContent = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-6 text-left'},join($CGI->br,@Zusagen[0..(ceil(scalar(@Zusagen)/2)-1)])).$CGI->div({-class => 'col-xs-12 col-md-6 text-left'},join($CGI->br,@Zusagen[(ceil(scalar(@Zusagen)/2))..$#Zusagen])));
      my $AbsagenContent = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-6 text-left'},join($CGI->br,@Absagen[0..(ceil(scalar(@Absagen)/2)-1)])).$CGI->div({-class => 'col-xs-12 col-md-6 text-left'},join($CGI->br,@Absagen[(ceil(scalar(@Absagen)/2))..$#Absagen])));
      my $PassiveContent = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-6 text-left'},join($CGI->br,@Passive[0..(ceil(scalar(@Passive)/2)-1)])).$CGI->div({-class => 'col-xs-12 col-md-6 text-left'},join($CGI->br,@Passive[(ceil(scalar(@Passive)/2))..$#Passive])));
      my $GuestContent = '';
      $GuestContent = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 text-left'},$CGI->span({-class => 'h3'},join($CGI->br,map { $Guests->{$_}->{'Firstname'}.'&nbsp;'.$Guests->{$_}->{'Lastname'}.'&nbsp;(Gast von '.$Players->{$Guests->{$_}->{'UserID'}}->{'Firstname'}.'&nbsp;'.$Players->{$Guests->{$_}->{'UserID'}}->{'Lastname'}.')'} @Guests))))if (scalar(@Guests));
      my $Zusagen = Panel->new({'ID' => 'ZusagenListe','Head' => $CGI->span({-class => 'h4'},'Anwesende Teilnehmer'),'Content' => $ZusagenContent,'Solo' => TRUE,'PanelClass' => 'panel-success','HeaderClass' => 'text-center'});
      my $Absagen = Panel->new({'ID' => 'AbsagenListe','Head' => $CGI->span({-class => 'h4'},'Abwesende Teilnehmer'),'Content' => $AbsagenContent,'Solo' => TRUE,'PanelClass' => 'panel-danger','HeaderClass' => 'text-center'});
      my $Passive = Panel->new({'ID' => 'PassiveListe','Head' => $CGI->span({-class => 'h4'},'Passive Teilnehmer'),'Content' => $PassiveContent,'Solo' => TRUE,'PanelClass' => 'panel-warning','HeaderClass' => 'text-center'});
      my $Guests  = Panel->new({'ID' => 'GaesteListe','Head' => $CGI->span({-class => 'h4'},'Anwesende Gäste'),'Content' => $GuestContent,'Solo' => TRUE,'PanelClass' => 'panel-info','HeaderClass' => 'text-center'});

      my $StatString = $CGI->span({-class => 'large visible-xs-inline'},$CountPlayer.' '.&Helpers::Icon('user','black').' &ndash; '.$PastMatchdays->{$date}->{'Courts'}.' '.&Helpers::Icon('film','black')) . $CGI->span({-class => 'h3 hidden-xs'},$CountPlayer.' Teilnehmer &ndash; '.$PastMatchdays->{$date}->{'Courts'}.' Courts');

      $PM_Panel->[$p] = Panel->new({'ID' => 'PM_'.$date,'HeaderClass' => '','HeaderTextClass' => 'h3','Head' => $DateString,'SubHead' => $StatString,'Footer' => &HTML::Button({-id => 'PM_ReopenMatchday_'.$date,-type => 'button',-class => 'btn btn-primary'},'Spieltag zum Bearbeiten wiedereröffnen'),'FooterClass' => 'text-center'});
      $PM_Panel->[$p]->appendContent($Zusagen->output()) if (scalar(@Zusagen));
      $PM_Panel->[$p]->appendContent($Guests->output()) if (scalar(@Guests));
      $PM_Panel->[$p]->appendContent($Absagen->output()) if (scalar(@Absagen));
      $PM_Panel->[$p]->appendContent($Passive->output()) if (scalar(@Passive));

      $p++;
    }

    $PM_Accordion->set('Panels',$PM_Panel);
    $PM_Content[$PM_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},$PM_Accordion->output()));
    $PM_Content[$PM_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    $PM_i++;
  }
  $PM_Content = join('',@PM_Content) if (scalar(@PM_Content));

# Set Content
  $PastMatchday->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},$CGI->h1('Bisherige Spieltage'))));
  $PastMatchday->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2'},$CGI->p('Hier werden vergangene Spieltage aufgelistet, aber nur wenn der Spieltag abgeschlossen wurde. In der Titelzeile werden neben dem Datum die Anzahl der Teilnehmer und der gebuchten Spielzeiten angezeigt. Wenn Du auf das Datum klickst, werden die Details angezeigt, also Teilnehmer, Gäste etc. Am Fuß des Spieltages befindet sich ein Button, mit dem Du den Spieltag wieder öffnen kannst, um Spielzeiten oder Teilnehmer zu korrigieren.'))));

  $PastMatchday->appendPane($PM_Content);

# Include Content
  $Administration->appendElement($PastMatchday);


#****************************************
# Zukünftige Spieltage
#****************************************

  my $FutureMatchday  = Dropdown::Element->new({'ID' => 'futuredays','Order' => ++$AdminOrder,'Title' => 'Zukünftige Spieltage'});

# Get Data
  my $FutureMatchdays = $DB->getFutureMatchdays()->{'Data'};

  my @FM_Rows;
  foreach my $date (sort(keys(%{$FutureMatchdays}))) {
    my $DateString = $CGI->span({-class => 'large visible-xs-inline'},&getDateFormatted('Tiny',$date)) . $CGI->span({-class => 'h3 hidden-xs'},&getDateFormatted('Medium',$date));
    my $Holiday = $Holidays->{$date} || '';
    my $Switch = '';
    $Switch = $CGI->input({-type => 'checkbox',-name => 'Matchday_'.$date,-checked => 'true'}) if ($FutureMatchdays->{$date}->{'Status'} == 1);
    $Switch = $CGI->input({-type => 'checkbox',-name => 'Matchday_'.$date}) if ($FutureMatchdays->{$date}->{'Status'} == 0);
    my $Birthday = '';
    my $Day = substr($date,5,5);
    if (exists($Birthdays->{$Day})) {
      $Birthday = 'Geburtstag von '.join(' und ',@{$Birthdays->{$Day}});
      $Holiday .= $Holiday ? '&nbsp;&mdash;&nbsp;'.$Birthday : $Birthday;
    }
    push(@FM_Rows,$CGI->Tr($CGI->td($DateString.$CGI->br.$CGI->small($Holiday)),$CGI->td({-class => 'text-right'},$Switch)));
  }
  my $FM_Table  = $CGI->table({-class => 'table'},$CGI->tbody({-class => 'table-striped'},@FM_Rows,$CGI->Tr($CGI->td(''),$CGI->td(''))));

# Create Form
  my $FM_Form = $CGI->start_form({-id => 'FutureMatchdays',-action => ''}).$FM_Table.$CGI->end_form();

# Set Content
  $FutureMatchday->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h1('Zukünftige Spieltage'))));
  $FutureMatchday->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p(['Hier kannst Du einen kompletten Spieltag absagen, z.B. wenn der Donnerstag auf einen Feiertag fällt oder absehbar ist, dass niemand spielen wird. Der Spieltag erscheint dann nicht in der Abstimmung und auch nicht in der Statistik. Teilnehmer, die bereits zugesagt haben, erhalten eine Mail mit der Absage.','Außerdem kannst Du hier einen Spieltag aktivieren, zum Beispiel einen neu hinzugefügten Spieltag, oder wenn ein bereits abgesagter Spieltag doch stattfinden soll.']))));
  $FutureMatchday->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
  $FutureMatchday->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$FM_Form)));
  $FutureMatchday->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));

# Include Content
  $Administration->appendElement($FutureMatchday);


#****************************************
# Neuer Spieltag
#****************************************

  my $NewMatchday = Dropdown::Element->new({'ID' => 'newmatchday','Order' => ++$AdminOrder,'Title' => 'Neuer Spieltag'});

# Get Data
  my $DaylistStart = $TP_Now + ONE_DAY + ONE_DAY;
  my $DaylistEnd = $DaylistStart + ONE_MONTH + ONE_MONTH;
  my $Daylist = [];
  my $NextDay = $DaylistStart;
  until (&getDateFormatted('MySQL',$NextDay) eq &getDateFormatted('MySQL',$DaylistEnd)) {
    push(@{$Daylist},&getDateFormatted('MySQL',$NextDay)) unless (exists($FutureMatchdays->{&getDateFormatted('MySQL',$NextDay)}) or exists($Holidays->{&getDateFormatted('MySQL',$NextDay)}));
    $NextDay += ONE_DAY;
  }
  my $DayLabels = { '' => ' - Datum auswählen - ', map { $_ => &getDateFormatted('AbbrLong',$_) } @{$Daylist} };
  unshift(@{$Daylist},'');

# Create Form
  my $NewMatchdayForm = $CGI->start_form({-id => 'NewMatchday',-class => 'form-horizontal',-action => ''});
  $NewMatchdayForm .= Element->new({'ID' => 'NewMatchday_Date','Type' => 'ScrollingList','Name' => 'Date','Label' => 'Datum','Values' => $Daylist,'Labels' => $DayLabels,%FormDefaults})->output();
  $NewMatchdayForm .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 col-md-offset-2 text-center'},&HTML::Button({-id => 'NewMatchday_Save',-type => 'button',-class => 'btn btn-primary btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Speichern'))).$CGI->div({-class => 'col-xs-12 visible-xs-block'},'&nbsp;') . $CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 text-center'},&HTML::Button({-id => 'NewMatchday_Cancel',-type => 'button',-class => 'btn btn-info btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Verwerfen'))));
  $NewMatchdayForm .= $CGI->end_form();

# Set Content
  $NewMatchday->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h1('Neuer Spieltag'))));
  my $Intro = 'Hier kannst Du einen neuen Spieltag, der außer der Reihe - also nicht Donnerstags - stattfindet, festlegen. Es stehen nur Termine zur Auswahl, an denen nicht bereits ein Spieltag eingetragen ist und an denen kein Feiertag ist. Ein neu hinzugefügter Spieltag ist zunächst nicht aktiv. Du musst ihn im Menü "Verwaltung - Zukünftige Spieltage" aktivieren.';
  $NewMatchday->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p($Intro))));
  $NewMatchday->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
  $NewMatchday->appendPane($NewMatchdayForm);
  $NewMatchday->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
  $NewMatchday->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));

# Include Content
  $Administration->appendElement($NewMatchday);


#****************************************
# Trennlinie
#****************************************

  $Administration->appendElement(Dropdown::Element->new({'ID' => 'divider'.$AdminOrder,'Order' => ++$AdminOrder}));


#****************************************
# Neuer Teilnehmer
#****************************************

my $AddPlayer       = Dropdown::Element->new({'ID' => 'addplayer','Order' => ++$AdminOrder,'Title' => 'Neuer Teilnehmer'});

# Create Form
my $NPForm = $CGI->start_form({-id => 'NewPlayer',-class => 'form-horizontal',-action => ''});
$NPForm .= Element->new({'ID' => 'NP_Vorname','Name' => 'Vorname',%FormDefaults})->output();
$NPForm .= Element->new({'ID' => 'NP_Nachname','Name' => 'Nachname',%FormDefaults})->output();
$NPForm .= Element->new({'ID' => 'NP_Benutzername','Name' => 'Benutzername',%FormDefaults})->output();
$NPForm .= Element->new({'ID' => 'NP_EMail','Type' => 'EMail','Name' => 'EMail','Label' => 'E-Mail-Adresse',%FormDefaults})->output();

$NPForm .= $CGI->div({'ID' => 'NP_Save',-class => 'form-group'},$CGI->div({-class => 'col-xs-12 col-md-offset-2 col-md-4'},&HTML::Button({-id => 'NP_Save',-type => 'button',-class => 'btn btn-primary btn-block',-disabled => 'disabled'},&Helpers::HeaderText('Speichern'))));
$NPForm .= $CGI->div({'ID' => 'NP_Cancel',-class => 'form-group'},$CGI->div({-class => 'col-xs-12 col-md-offset-2 col-md-4'},&HTML::Button({-id => 'NP_Cancel',-type => 'button',-class => 'btn btn-info btn-block'},&Helpers::HeaderText('Verwerfen'))));
$NPForm .= $CGI->end_form();

# Set Content
$AddPlayer->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-10 col-md-offset-2'},$CGI->h1('Neuer Teilnehmer'))));
$AddPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-10 col-md-offset-2'},$CGI->p('Wenn Du einen neuen Teilnehmer anlegst, achte darauf, dass die E-Mail-Adresse richtig ist. An diese Adresse wird dem Teilnehmer der Benutzername und das Passwort (wird im Hintergrund automatisch generiert) gemailt. Neue Teilnehmer sind aktiv und ihr Standard-Teilnahmestatus ist "Absagen".'))));
$AddPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$AddPlayer->appendPane($NPForm);

# Include Content
$Administration->appendElement($AddPlayer);


#****************************************
# Teilnehmerdaten bearbeiten
#****************************************

my $EditPlayer      = Dropdown::Element->new({'ID' => 'editplayer','Order' => ++$AdminOrder,'Title' => 'Teilnehmerdaten bearbeiten'});

# Get Data
my %PlayerNameByID = map { $_ => $Players->{$_}->{'Lastname'}.', '.$Players->{$_}->{'Firstname'} } grep { $Players->{$_}->{'Excluded'} == 0 } keys(%{$Players});
my $PlayerValues   = [ '',sort { $Players->{$a}->{'SortID'} <=> $Players->{$b}->{'SortID'} } grep { $Players->{$_}->{'Excluded'} == 0 } keys(%{$Players}) ];
my $PlayerLabels   = { '' => ' - Teilnehmer auswählen - ',%PlayerNameByID };

# Create Form
my $EP_Save   = &HTML::Button({-id => 'EP_Save',-type => 'button',-class => 'btn btn-primary btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Speichern'));
my $EP_Cancel = &HTML::Button({-id => 'EP_Cancel',-type => 'button',-class => 'btn btn-info btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Verwerfen'));

my $SForm = $CGI->start_form({-id => 'EP_SelectPlayer',-class => 'form-horizontal',-action => ''});
$SForm .= Element->new({'ID' => 'SP_UserID','Type' => 'ScrollingList','Name' => 'UserID','Label' => 'Teilnehmer','Values' => $PlayerValues,'Labels' => $PlayerLabels,%FormDefaults})->output();
$SForm .= $CGI->end_form();

my $EPForm = $CGI->start_form({-id => 'EditPlayer',-class => 'form-horizontal',-action => ''});
$EPForm .= Element->new({'ID' => 'EP_Vorname','Name' => 'Vorname','Disabled' => TRUE,%FormDefaults})->output();
$EPForm .= Element->new({'ID' => 'EP_Nachname','Name' => 'Nachname','Disabled' => TRUE,%FormDefaults})->output();
$EPForm .= Element->new({'ID' => 'EP_Benutzername','Name' => 'Benutzername','Disabled' => TRUE,%FormDefaults})->output();
$EPForm .= Element->new({'ID' => 'EP_EMail','Type' => 'EMail','Name' => 'EMail','Label' => 'E-Mail-Adresse','Disabled' => TRUE,%FormDefaults})->output();
$EPForm .= Element->new({'ID' => 'EP_Fee','Name' => 'Fee','Label' => 'Eigenbeitrag '.$ThisYear,'Disabled' => TRUE,%FormDefaults})->output();
$EPForm .= Element->new({'ID' => 'EP_Aktiv','Type' => 'Checkbox','Name' => 'Aktiv','Disabled' => TRUE,%FormDefaults})->output();
$EPForm .= Element->new({'ID' => 'EP_Default_Status','Type' => 'Checkbox','Name' => 'Default_Status','Label' => 'Teilnahmestatus','Disabled' => TRUE,%FormDefaults})->output();
$EPForm .= Element->new({'ID' => 'EP_Passwort','Type' => 'Checkbox','Name' => 'Passwort','Label' => 'Passwort erneuern','Disabled' => TRUE,%FormDefaults})->output();
$EPForm .= Element->new({'ID' => 'EP_UserID','Type' => 'Hidden','Name' => 'UserID'})->output();

$EPForm .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 col-md-offset-2 text-center'},$EP_Save).$CGI->div({-class => 'col-xs-12 visible-xs-block'},'&nbsp;') . $CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 text-center'},$EP_Cancel));
$EPForm .= $CGI->end_form();

# Set Content
$EditPlayer->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-10 col-md-offset-2'},$CGI->h1('Teilnehmerdaten bearbeiten'))));
$EditPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-10 col-md-offset-2'},$CGI->p('Hier kannst Du die Daten eines Teilnehmers bearbeiten. Wenn Du einen Teilnehmer auf "Nicht Aktiv" stellst, kann dieser sich nicht mehr anmelden und an Abstimmungen zu Spieltagen teilnehmen. In der Statistik taucht dieser Spieler als "Passiv" auf. Hier kannst Du auch das Passwort zurücksetzen, falls der Teilnehmer es vergessen hat. Achte dabei auf die richtige E-Mail-Adresse, denn an diese Adresse erhält der Teilnehmer sein neues Passwort geschickt.'))));
$EditPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$EditPlayer->appendPane($SForm);
$EditPlayer->appendPane($EPForm);
$EditPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));

# Include Content
$Administration->appendElement($EditPlayer);


#****************************************
# Beitragsstatus pflegen
#****************************************

my $PlayerContrib      = Dropdown::Element->new({'ID' => 'playercontrib','Order' => ++$AdminOrder,'Title' => 'Beitragsstatus pflegen'});

# Get Data

# Create Form
my $PC_Save   = &HTML::Button({-id => 'PC_Save',-type => 'button',-class => 'btn btn-primary btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Speichern'));
my $PC_Cancel = &HTML::Button({-id => 'PC_Cancel',-type => 'button',-class => 'btn btn-info btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Verwerfen'));

my $PCSForm = $CGI->start_form({-id => 'PC_SelectPlayer',-class => 'form-horizontal',-action => ''});
$PCSForm .= Element->new({%FormDefaults,'ID' => 'PC_UserID','Type' => 'ScrollingList','Name' => 'UserID','Label' => 'Teilnehmer','Values' => $PlayerValues,'Labels' => $PlayerLabels})->output();
$PCSForm .= $CGI->end_form();

my $PCForm = $CGI->start_form({-id => 'PlayerContrib',-class => 'form-horizontal',-action => ''});
foreach my $year ($ThisYear,$LastYear) {
  $PCForm .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-offset-2 h2'},$year));
  $PCForm .= Element->new({'ID' => 'PC_Year','Type' => 'Hidden','Name' => 'Year','Value' => $year})->output();
  $PCForm .= $CGI->div({-class => 'form-group'},$CGI->label({-class => 'col-md-offset-2 col-md-3 h4'},'Eigenbeitrag:').$CGI->div({-class => 'col-md-1'},$CGI->p({-class => 'text-right h4'},$CGI->span({-id => 'Fee_'.$year},'').'&nbsp;€')).Element->new({%FormDefaults,'ID' => 'PC_FeeStatus_'.$year,'Type' => 'Checkbox','Name' => 'FeeStatus_'.$year,'Label' => 'Bezahlt?','Disabled' => TRUE})->raw());
  $PCForm .= $CGI->div({-class => 'form-group'},$CGI->label({-class => 'col-md-offset-2 col-md-3 h4'},'Zu späte Ab- und Zusagen:').$CGI->div({-class => 'col-md-1'},$CGI->p({-class => 'text-right h4'},$CGI->span({-id => 'Late_'.$year},'').'&nbsp;€')).Element->new({%FormDefaults,'ID' => 'PC_LateStatus_'.$year,'Type' => 'Checkbox','Name' => 'LateStatus_'.$year,'Label' => 'Bezahlt?','Disabled' => TRUE})->raw());
  $PCForm .= $CGI->div({-class => 'form-group'},$CGI->label({-class => 'col-md-offset-2 col-md-3 h4'},'Beitrag für Gäste:').$CGI->div({-class => 'col-md-1'},$CGI->p({-class => 'text-right h4'},$CGI->span({-id => 'Guests_'.$year},'').'&nbsp;€')).Element->new({%FormDefaults,'ID' => 'PC_GuestsStatus_'.$year,'Type' => 'Checkbox','Name' => 'GuestsStatus_'.$year,'Label' => 'Bezahlt?','Disabled' => TRUE})->raw());
  $PCForm .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'))
}
$PCForm .= Element->new({'ID' => 'PC_UserID','Type' => 'Hidden','Name' => 'UserID'})->output();
$PCForm .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 col-md-offset-2 text-center'},$PC_Save).$CGI->div({-class => 'col-xs-12 visible-xs-block'},'&nbsp;') . $CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 text-center'},$PC_Cancel));
$PCForm .= $CGI->end_form();

# Set Content
$PlayerContrib->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-10 col-md-offset-2'},$CGI->h1('Beitragsstatus pflegen'))));
$PlayerContrib->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-10 col-md-offset-2'},$CGI->p(''))));
$PlayerContrib->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$PlayerContrib->appendPane($PCSForm);
$PlayerContrib->appendPane($PCForm);
$PlayerContrib->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));

# Include Content
$Administration->appendElement($PlayerContrib);


#****************************************
# Für Teilnehmer abstimmen
#****************************************

my $PartPlayer      = Dropdown::Element->new({'ID' => 'partplayer','Order' => ++$AdminOrder,'Title' => 'Für Teilnehmer abstimmen'});

# Get Data
my $ActivePlayerValues   = [ '',sort { $Players->{$a}->{'SortID'} <=> $Players->{$b}->{'SortID'} } keys(%{$ActivePlayers}) ];

# Create Form
my $SForm2 = $CGI->start_form({-id => 'SelectPlayer2',-class => 'form-horizontal',-action => ''});
$SForm2 .= Element->new({'ID' => 'SP2_UserID','Type' => 'ScrollingList','Name' => 'UserID','Label' => 'Teilnehmer','Values' => $ActivePlayerValues,'Labels' => $PlayerLabels,%FormDefaults})->output();
$SForm2 .= $CGI->end_form();

my %PP_StatusByDate = ();
my @PP_Rows = ();
foreach my $date ($NextMatchday,@{$NextMatchdays}) {
  my $DateString = $CGI->span({-class => 'large visible-xs-block'},&getDateFormatted('Tiny',$date)) . $CGI->span({-class => 'h3 hidden-xs'},&getDateFormatted('Medium',$date));
  $PP_StatusByDate{$date} = -1;
  my $Switch = '';
  $Switch = $CGI->input({-type => 'checkbox',-name => 'PP_Teilnahme_'.$date});
  push(@PP_Rows,$CGI->Tr($CGI->td({-class => 'text-left'},$DateString),$CGI->td({-class => 'text-right'},$Switch)));
}

my $PP_Table  = $CGI->table({-class => 'table'},$CGI->tbody({-class => 'table-striped'},@PP_Rows,$CGI->Tr($CGI->td(''),$CGI->td(''))));
my $PP_Save   = &HTML::Button({-id => 'PP_Save',-type => 'button',-class => 'btn btn-primary btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Speichern'));
my $PP_Cancel = &HTML::Button({-id => 'PP_Cancel',-type => 'button',-class => 'btn btn-info btn-lg btn-block'},$CGI->span({-class => 'h2'},'Verwerfen'));

# Create Form
my $PP_Form = $CGI->start_form({-id => 'PartPlayer',-action => ''}).$PP_Table.$CGI->end_form();


# Set Content
$PartPlayer->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-10 col-md-offset-2'},$CGI->h1('Für Teilnehmer abstimmen'))));
$PartPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-10 col-md-offset-2'},$CGI->p('Falls ein Teilnehmer aus irgendeinem Grund nicht selbst abstimmen kann, kannst Du dies hier für ihn tun. Bei Terminen, für die noch nicht abgestimmt wurde, zeigt der Schalter weder Ja noch Nein. Es ist nicht notwendig, für diese Termine einen Wert zu wählen, der dem Standard-Teilnahmestatus entspricht, da dieser dann automatisch verwendet wird.'))));
$PartPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$PartPlayer->appendPane($SForm2);
$PartPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-10 col-md-offset-2'},$CGI->h4({-id => 'PP_Default'},''))));
$PartPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
$PartPlayer->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-md-8 col-md-offset-2 text-center'},$PP_Form)));

# Include Content
$Administration->appendElement($PartPlayer);


#****************************************
# Trennlinie
#****************************************

$Administration->appendElement(Dropdown::Element->new({'ID' => 'divider'.$AdminOrder,'Order' => ++$AdminOrder}));


#****************************************
# Teilnahmebericht
#****************************************

  my $ReportParticip = Dropdown::Element->new({'ID' => 'reportparticip','Order' => ++$AdminOrder,'Title' => 'Teilnahmebericht'});

# Get Data
  my $RP_Content = '';
  my @RP_Content = ();
  my $RP_i = 0;

  foreach my $year (reverse(sort(keys(%{$ClosedMatchdayByYear})))) {
    $RP_Content[$RP_i]  = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h2($year.': '.scalar(keys(%{$ClosedMatchdayByYear->{$year}})).' Spieltag'.(scalar(keys(%{$ClosedMatchdayByYear->{$year}})) == 1 ? '' : 'e'))));
    $RP_Content[$RP_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));

    my $ParticipationAggregated = $DB->getParticipation({'Year' => $year})->{'Data'};

    my @Rows = ();
    my @Details = ();
    foreach my $userid (sort { $Players->{$a}->{'SortID'} <=> $Players->{$b}->{'SortID'} } keys(%{$Players})) {
      my $Name = $CGI->span({-class => 'large'},$Players->{$userid}->{'Firstname'}.'&nbsp;'.$Players->{$userid}->{'Lastname'});
      if ($ParticipationAggregated->{$userid}->{'Participation'} or $ParticipationAggregated->{$userid}->{'TooLate'}) {
        $Name = $CGI->span({-class => 'large',-data_toggle => 'modal',-data_target => '#TeilnahmeDetails_'.$year.'_'.$userid},$Players->{$userid}->{'Firstname'}.'&nbsp;'.$Players->{$userid}->{'Lastname'});
        my $Part = $CGI->span({-class => 'large'},$ParticipationAggregated->{$userid}->{'Participation'} ? $ParticipationAggregated->{$userid}->{'Participation'} : '&mdash;');
        my $TooLate = '';
        if ($ParticipationAggregated->{$userid}->{'TooLate'}) {
          if ($ParticipationAggregated->{$userid}->{'TooLate'} > $AppConfig->{'0'}->{$year}->{'LateFreeShots'}->{'Setting'}) {
            $TooLate = $CGI->span({-class => 'large',style => 'color:red;'},$ParticipationAggregated->{$userid}->{'TooLate'});
          }
          else {
            $TooLate = $CGI->span({-class => 'large'},$ParticipationAggregated->{$userid}->{'TooLate'});
          }
        }
        else {
          $TooLate = $CGI->span({-class => 'large'},'&mdash;');
        }

        push(@Rows,$CGI->Tr($CGI->td({-class => 'text-left'},$Name),$CGI->td({-class => 'text-right'},$Part),$CGI->td({-class => 'text-right'},$TooLate)));

        my $ParticipationDetails  = $DB->getParticipationByUser({'UserID' => $userid})->{'Data'};

        my $PastParticipationDetails = {'CountTeilnahme' => 0,'CountTeilnahmeOffTime' => 0,'CountAbsage' => 0,'CountAbsageOffTime' => 0};

        foreach my $date (keys(%{$ParticipationDetails})) {
          next unless ($ParticipationDetails->{$date}->{'Final'});
          next unless (substr($date,0,4) eq $year);
          next unless (exists($ParticipationDetails->{$date}->{'Status'}));
          $PastParticipationDetails->{'CountTeilnahme'}++ if ($ParticipationDetails->{$date}->{'Status'} == 1);
          $PastParticipationDetails->{'CountTeilnahmeOffTime'}++ if ($ParticipationDetails->{$date}->{'Status'} == 1 and $ParticipationDetails->{$date}->{'OnTime'} == 0);
          $PastParticipationDetails->{'CountAbsage'}++ if ($ParticipationDetails->{$date}->{'Status'} == 0);
          $PastParticipationDetails->{'CountAbsageOffTime'}++ if ($ParticipationDetails->{$date}->{'Status'} == 0 and $ParticipationDetails->{$date}->{'OnTime'} == 0);
        }

        my $DetailsBody = $CGI->p({-class => 'hidden-xs'},&HTML::large({},$Players->{$userid}->{'Firstname'}.' hat '.($PastParticipationDetails->{'CountTeilnahme'} > 0 ? $PastParticipationDetails->{'CountTeilnahme'}.' mal' : 'nie').' teilgenommen und '.(($PastParticipationDetails->{'CountTeilnahmeOffTime'} + $PastParticipationDetails->{'CountAbsageOffTime'}) > 0 ? ($PastParticipationDetails->{'CountTeilnahmeOffTime'} + $PastParticipationDetails->{'CountAbsageOffTime'}).' mal' : 'nie').' zu spät zu- oder abgesagt.'));
        $DetailsBody   .= $CGI->p({-class => 'visible-xs-inline'},&HTML::large({},($PastParticipationDetails->{'CountTeilnahme'} > 0 ? $PastParticipationDetails->{'CountTeilnahme'}.' mal' : 'nie').' teilgenommen<br />'.(($PastParticipationDetails->{'CountTeilnahmeOffTime'} + $PastParticipationDetails->{'CountAbsageOffTime'}) > 0 ? ($PastParticipationDetails->{'CountTeilnahmeOffTime'} + $PastParticipationDetails->{'CountAbsageOffTime'}).' mal' : 'nie').' zu spät zu- oder abgesagt'));

        my @DetailsRows = ();
        foreach my $date (sort(keys(%{$ClosedMatchdayByYear->{$year}}))) {
          my $Status = (exists($ParticipationDetails->{$date}->{'Status'}) && $ParticipationDetails->{$date}->{'Status'} == 1) ? &Helpers::Icon('ok','green') : &Helpers::Icon('remove','black');
          my $OffTimeWarning = $ParticipationDetails->{$date}->{'OnTime'} ? '' : &Helpers::Icon('time','red');
          push(@DetailsRows,$CGI->Tr($CGI->td($CGI->span({-class => 'large hidden-xs'},&getDateFormatted('Medium',$date)).$CGI->span({-class => 'large visible-xs-inline'},&getDateFormatted('Tiny',$date))),$CGI->td({-align => 'right'},$CGI->table($CGI->Tr($CGI->td({-width => '30px',-align => 'right'},[$CGI->span({-class => 'large'},$Status),'&nbsp;',$CGI->span({-class => 'large'},$OffTimeWarning)]))))));
        }

        $DetailsBody .= $CGI->table({-class => 'table'},$CGI->thead($CGI->Tr($CGI->th('&nbsp;'),$CGI->th('&nbsp;'))),$CGI->tbody(@DetailsRows,$CGI->Tr($CGI->td(['&nbsp;','&nbsp;']))));

        my $Details = Modal->new({'ID' => 'TeilnahmeDetails_'.$year.'_'.$userid,'Header' => $CGI->span({-class => 'h3 hidden-xs'},'Teilnahmedetails von '.$Players->{$userid}->{'Firstname'}.'&nbsp;'.$Players->{$userid}->{'Lastname'}).$CGI->span({-class => 'h3 visible-xs-inline'},$Players->{$userid}->{'Firstname'}.'&nbsp;'.$Players->{$userid}->{'Lastname'}),'Body' => $DetailsBody,'Footer' => 'OK','Size' => 'large'});
        push(@Details,$Details->output);
      }
    }

    $RP_Content[$RP_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->table({-class => 'table'},$CGI->thead($CGI->Tr($CGI->th({-class => 'text-left'},''),$CGI->th({-class => 'text-right'},$CGI->span({-class => 'large'},&Helpers::Icon('ok','green'))),$CGI->th({-class => 'text-right'},$CGI->span({-class => 'large'},&Helpers::Icon('time','red'))))),$CGI->tbody({-class => 'table-striped'},@Rows,$CGI->Tr($CGI->td(''),$CGI->td(''),$CGI->td(''))))));
    $RP_Content[$RP_i] .= join('',@Details) if (scalar(@Details));

    $RP_i++;
  }

  $RP_Content = join('',@RP_Content) if (scalar(@RP_Content));

# Set Content
  $ReportParticip->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h1('Teilnahmebericht'))));
  $ReportParticip->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p('Der Teilnahmebericht zeigt dir für jedes Jahr, wieviele Spieltage stattgefunden haben, wer wie oft teilgenommen hat und wie oft die Zu- oder Absage zu spät war. Es werden nur Teilnehmer angezeigt, die mindestens einmal aktiv waren (auch wenn sie dann ihre Teilnahme abgesagt haben). Wenn Du auf einen Namen klickst, öffnet sich ein Fenster mit den Detaildaten für diesen Teilnehmer.'))));
  $ReportParticip->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p(''))));
  $ReportParticip->appendPane($RP_Content);


# Include Content
  $Administration->appendElement($ReportParticip);


#****************************************
# Finanzbericht
#****************************************

  my $ReportFinance = Dropdown::Element->new({'ID' => 'reportfinance','Order' => ++$AdminOrder,'Title' => 'Finanzbericht'});

# Get Data
  my $CourtsByQuarter = $DB->getCourts()->{'Data'};

  my $RF_Content = '';
  my @RF_Content = ();
  my $RF_i = 0;

  foreach my $year (reverse(sort(keys(%{$ClosedMatchdayByYear})))) {
    $RF_Content[$RF_i]  = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h2($year)));
    $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));

    my $Contributions = $DB->getContributions({'Year' => $year})->{'Data'};
    my $ParticipationAggregated = $DB->getParticipation({'Year' => $year})->{'Data'};
    my $GuestParticipation = $DB->getGuestParticipation({'Year' => $year})->{'Data'};
    my $GuestsByUser = {};
    foreach my $guest (@{$GuestParticipation}) {
      push(@{$GuestsByUser->{$guest->{'UserID'}}->{$guest->{'Date'}}},{'ID' => $guest->{'ID'},'Firstname' => $guest->{'Firstname'},'Lastname' => $guest->{'Lastname'}});
    }

    $_ = 0 for my ($TooLateTotal,$ContribTotal,$GuestsTotal,$SumTotal);
    $_ = () for my (@ContribStatus,@TooLateStatus,@GuestsStatus);

    $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-sm-6 hidden-xs h3'},'Einnahmen aus Beiträgen').$CGI->div({-class => 'col-xs-8 visible-xs-inline h3'},'Einnahmen').$CGI->div({-class => 'col-sm-2 hidden-xs text-right h3'},&Helpers::Icon('user','','Eigenbeitrag').'&nbsp;&nbsp;&nbsp;').$CGI->div({-class => 'col-sm-1 hidden-xs text-right h3'},&Helpers::Icon('time','','Verspätete Ab-/Zusagen').'&nbsp;').$CGI->div({-class => 'col-sm-1 hidden-xs text-right h3'},&Helpers::Icon('gift','','Gastbeiträge').'&nbsp;').$CGI->div({-class => 'col-xs-4 col-sm-2 text-right h3'},'Summe')).$CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->hr()));
    foreach my $userid (sort { $Players->{$a}->{'SortID'} <=> $Players->{$b}->{'SortID'} } keys(%{$Players})) {
      my $Name = $CGI->span({-class => 'large',-data_toggle => 'modal',-data_target => '#BeitragsDetails_'.$year.'_'.$userid},$Players->{$userid}->{'Firstname'}.'&nbsp;'.$Players->{$userid}->{'Lastname'});
      my $Sum  = 0;
      my @Status = ();

      my $Contrib = $CGI->span({-class => 'large'},'');
      if (exists($Contributions->{$userid}) && $Contributions->{$userid}->{'Fee'}) {
        $Contrib = $CGI->span({-class => 'large',style => ($Contributions->{$userid}->{'FeeStatus'} ? 'color:green;' : 'color:red;')},$Contributions->{$userid}->{'Fee'}.' €');
        $ContribTotal += $Contributions->{$userid}->{'Fee'};
        $Sum += $Contributions->{$userid}->{'Fee'};
        push(@Status,$Contributions->{$userid}->{'FeeStatus'});
        push(@ContribStatus,$Contributions->{$userid}->{'FeeStatus'});
      }

      my $TooLate = $CGI->span({-class => 'large'},'');
      if (exists($ParticipationAggregated->{$userid}) && $ParticipationAggregated->{$userid}->{'TooLate'} > $AppConfig->{'0'}->{$year}->{'LateFreeShots'}->{'Setting'}) {
        $TooLate = $CGI->span({-class => 'large',style => ($Contributions->{$userid}->{'LateStatus'} ? 'color:green;' : 'color:red;')},$Contributions->{$userid}->{'Late'}.' €');
        $TooLateTotal += $Contributions->{$userid}->{'Late'};
        $Sum += $Contributions->{$userid}->{'Late'};
        push(@Status,$Contributions->{$userid}->{'LateStatus'});
        push(@TooLateStatus,$Contributions->{$userid}->{'LateStatus'});
      }

      my $Guests = $CGI->span({-class => 'large'},'');
      my $GuestCount = 0;
      if (exists($GuestsByUser->{$userid})) {
        foreach my $date (keys(%{$GuestsByUser->{$userid}})) {
          $GuestCount += scalar(@{$GuestsByUser->{$userid}->{$date}});
        }
        $Guests = $CGI->span({-class => 'large',style => ($Contributions->{$userid}->{'GuestsStatus'} ? 'color:green;' : 'color:red;')},$Contributions->{$userid}->{'Guests'}.' €');
        $GuestsTotal += $Contributions->{$userid}->{'Guests'};
        $Sum += $Contributions->{$userid}->{'Guests'};
        push(@Status,$Contributions->{$userid}->{'GuestsStatus'});
        push(@GuestsStatus,$Contributions->{$userid}->{'GuestsStatus'});
      }
      if ($Sum) {
        my $StatusMean = eval(join("+",@Status)) / @Status;
        my $ColorStyle = 'color:orange;';
        $ColorStyle = 'color:red;' if ($StatusMean == 0);
        $ColorStyle = 'color:green;' if ($StatusMean == 1);
        $SumTotal += $Sum;
        my $ModalBody = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-9 large'},'Eigenbeitrag:').$CGI->div({-class => 'col-xs-3 text-right large'},$Contributions->{$userid}->{'Fee'}.' €'));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-9 large'},'Bezahlt:').$CGI->div({-class => 'col-xs-3 text-right large'},($Contributions->{$userid}->{'FeeStatus'} ? 'Ja' : 'Nein')));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->hr()));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-9 large'},'Zu späte Zu/Absagen:').$CGI->div({-class => 'col-xs-3 text-right large'},$ParticipationAggregated->{$userid}->{'TooLate'}));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-9 large'},'Kosten/Verspätung:').$CGI->div({-class => 'col-xs-3 text-right large'},$AppConfig->{'0'}->{$year}->{'LatePenalty'}->{'Setting'}.' €'));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-9 large'},'Beitrag Verspätungen:').$CGI->div({-class => 'col-xs-3 text-right large'},($ParticipationAggregated->{$userid}->{'TooLate'} > $AppConfig->{'0'}->{$year}->{'LateFreeShots'}->{'Setting'} ? $Contributions->{$userid}->{'Late'} : 0).' €'));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-9 large'},'Bezahlt:').$CGI->div({-class => 'col-xs-3 text-right large'},($ParticipationAggregated->{$userid}->{'TooLate'} > $AppConfig->{'0'}->{$year}->{'LateFreeShots'}->{'Setting'} ? ($Contributions->{$userid}->{'LateStatus'} ? 'Ja' : 'Nein') : '&ndash;')));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->hr()));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-9 large'},'Gäste:').$CGI->div({-class => 'col-xs-3 text-right large'},$GuestCount));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-9 large'},'Kosten/Gast:').$CGI->div({-class => 'col-xs-3 text-right large'},$AppConfig->{'0'}->{$year}->{'GuestContribution'}->{'Setting'}.' €'));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-9 large'},'Beitrag Gäste:').$CGI->div({-class => 'col-xs-3 text-right large'},$Contributions->{$userid}->{'Guests'}.' €'));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-9 large'},'Bezahlt:').$CGI->div({-class => 'col-xs-3 text-right large'},($Contributions->{$userid}->{'Guests'} ? ($Contributions->{$userid}->{'GuestsStatus'} ? 'Ja' : 'Nein') : '&ndash;')));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->hr()));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-9 large'},'Gesamtbeiträge:').$CGI->div({-class => 'col-xs-3 text-right large'},$Sum.' €'));
        $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-8 col-sm-6'},$Name).$CGI->div({-class => 'col-sm-2 hidden-xs text-right'},$Contrib).$CGI->div({-class => 'col-sm-1 hidden-xs text-right'},$TooLate).$CGI->div({-class => 'col-sm-1 hidden-xs text-right'},$Guests).$CGI->div({-class => 'col-xs-4 col-sm-2 text-right'},$CGI->span({-class => 'large',-style => $ColorStyle},$Sum . ' €'))).$CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->hr()));
        $RF_Content[$RF_i] .= Modal->new({'ID' => 'BeitragsDetails_'.$year.'_'.$userid,'Header' => $CGI->span({-class => 'h3'},$Players->{$userid}->{'Firstname'}.'&nbsp;'.$Players->{$userid}->{'Lastname'}),'Body' => $ModalBody,'Footer' => 'OK'})->output;
      }
    }
    my $ContribStatusMean = eval(join("+",@ContribStatus)) / @ContribStatus if (scalar(@ContribStatus));
    $ContribStatusMean = 0 unless(defined($ContribStatusMean));
    my $TooLateStatusMean = eval(join("+",@TooLateStatus)) / @TooLateStatus if (scalar(@TooLateStatus));
    $TooLateStatusMean = 0 unless(defined($TooLateStatusMean));
    my $GuestsStatusMean = eval(join("+",@GuestsStatus)) / @GuestsStatus if (scalar(@GuestsStatus));
    $GuestsStatusMean = 0 unless(defined($GuestsStatusMean));
    my $SumStatusMean = $ContribStatusMean + $TooLateStatusMean + $GuestsStatusMean;
    my $ContribColorStyle = 'color:orange;';
    $ContribColorStyle = 'color:red;' if ($ContribStatusMean == 0);
    $ContribColorStyle = 'color:green;' if ($ContribStatusMean == 1);
    my $TooLateColorStyle = 'color:orange;';
    $TooLateColorStyle = 'color:red;' if ($TooLateStatusMean == 0);
    $TooLateColorStyle = 'color:green;' if ($TooLateStatusMean == 1);
    my $GuestsColorStyle = 'color:orange;';
    $GuestsColorStyle = 'color:red;' if ($GuestsStatusMean == 0);
    $GuestsColorStyle = 'color:green;' if ($GuestsStatusMean == 1);
    my $SumColorStyle = 'color:orange;';
    $SumColorStyle = 'color:red;' if ($SumStatusMean == 0);
    $SumColorStyle = 'color:green;' if ($SumStatusMean == 1);

    $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-8 col-sm-6 h3'},'Gesamt').$CGI->div({-class => 'col-sm-2 hidden-xs text-right h3',-style => $ContribColorStyle},$ContribTotal.' €').$CGI->div({-class => 'col-sm-1 hidden-xs text-right h3',-style => $TooLateColorStyle},$TooLateTotal.' €').$CGI->div({-class => 'col-sm-1 hidden-xs text-right h3',-style => $GuestsColorStyle},$GuestsTotal.' €').$CGI->div({-class => 'col-xs-4 col-sm-2 text-right h3',-style => $SumColorStyle},$SumTotal.' €'));

    $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));

    my $TotalCosts = 0;
    $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-sm-6 hidden-xs h3'},'Ausgaben für Plätze').$CGI->div({-class => 'col-xs-6 visible-xs-inline h3'},'Ausgaben').$CGI->div({-class => 'col-sm-2 hidden-xs text-right h3'},&Helpers::Icon('calendar','','Spieltage')).$CGI->div({-class => 'col-sm-2 hidden-xs text-right h3'},&Helpers::Icon('film','','Spielzeiten')).$CGI->div({-class => 'col-xs-6 col-sm-2 text-right h3'},'Summe')).$CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->hr()));
    foreach my $quarter (1..4) {
      if (exists($CourtsByQuarter->{$year.'-'.$quarter})) {
        my $Costs = 0;
        $Costs = ($CourtsByQuarter->{$year.'-'.$quarter}->{'Courts'} * $AppConfig->{'0'}->{$year}->{'PricePerCourt'}->{'Setting'});
        $TotalCosts += $Costs;
        my $ModalBody = $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-8 large'},'Spieltage:').$CGI->div({-class => 'col-xs-4 text-right large'},$CourtsByQuarter->{$year.'-'.$quarter}->{'MatchDays'}));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-8 large'},'Spielzeiten:').$CGI->div({-class => 'col-xs-4 text-right large'},$CourtsByQuarter->{$year.'-'.$quarter}->{'Courts'}));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-8 large'},'Kosten/Spielzeit:').$CGI->div({-class => 'col-xs-4 text-right large'},$AppConfig->{'0'}->{$year}->{'PricePerCourt'}->{'Setting'}.' €'));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->hr()));
        $ModalBody .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-8 large'},'Gesamtkosten:').$CGI->div({-class => 'col-xs-4 text-right large'},$Costs.' €'));
        $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-6 large'},$CGI->span({-data_toggle => 'modal',-data_target => '#PlatzDetails_'.$year.'_'.$quarter},$quarter.'. Quartal')).$CGI->div({-class => 'col-sm-2 hidden-xs text-right large'},$CourtsByQuarter->{$year.'-'.$quarter}->{'MatchDays'}).$CGI->div({-class => 'col-sm-2 hidden-xs text-right large'},$CourtsByQuarter->{$year.'-'.$quarter}->{'Courts'}).$CGI->div({-class => 'col-xs-6 col-sm-2 text-right large'},$Costs.' €')).$CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->hr()));
        $RF_Content[$RF_i] .= Modal->new({'ID' => 'PlatzDetails_'.$year.'_'.$quarter,'Header' => $CGI->span({-class => 'h3'},$quarter.'. Quartal '.$year),'Body' => $ModalBody,'Footer' => 'OK'})->output;
      }
    }
    $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-6 h3'},'Gesamt').$CGI->div({-class => 'col-sm-2 hidden-xs text-right h3'},scalar(keys(%{$ClosedMatchdayByYear->{$year}}))).$CGI->div({-class => 'col-sm-2 hidden-xs text-right h3'},$PastCourts->{$year}).$CGI->div({-class => 'col-xs-6 col-sm-2 text-right h3'},$TotalCosts.' €'));
    $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    $RF_Content[$RF_i] .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));

    $RF_i++;
  }


  $RF_Content = join('',@RF_Content) if (scalar(@RF_Content));

# Set Content
  $ReportFinance->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h1('Finanzbericht'))));
  $ReportFinance->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p(
    'Der Finanzbericht zeigt für jedes Jahr Einnahmen (aus Beiträgen) und Ausgaben (für Plätze).',
    'Bei den Einnahmen werden für jeden Teilnehmer der Eigenbeitrag, die Kosten fürs zu späte Zu- oder Absagen und die Beiträge für mitgebrachte Gäste aufgelistet. In der letzten Spalte steht die Summe aus diesen drei Beträgen.',
    'Bei den Ausgaben werden für jedes Quartal die Anzahl der Spieltage, die Anzahl der gebuchten Spielzeiten und in der letzten Spalte die Kosten für diese Spielzeiten aufgelistet.',
    'Bei den Einnahmen werden bezahlte Beiträge grün dargestellt, noch nicht bezahlte rot und wenn eine Summenzeile oder -spalte teilweise bezahlt ist, gelb.'
    ))));
  $ReportFinance->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p(''))));
  $ReportFinance->appendPane($RF_Content);


# Include Content
  $Administration->appendElement($ReportFinance);


#****************************************
# Trennlinie
#****************************************

  $Administration->appendElement(Dropdown::Element->new({'ID' => 'divider'.$AdminOrder,'Order' => ++$AdminOrder}));


#****************************************
# Einstellungen
#****************************************

  my $Settings = Dropdown::Element->new({'ID' => 'settings','Order' => ++$AdminOrder,'Title' => 'Einstellungen'});

## Get Data

## Create Form
  my $ST_Save   = &HTML::Button({-id => 'ST_Save',-type => 'button',-class => 'btn btn-primary btn-lg btn-block',-disabled => 'disabled'},$CGI->span({-class => 'h2'},'Speichern'));
  my $ST_Cancel = &HTML::Button({-id => 'ST_Cancel',-type => 'button',-class => 'btn btn-info btn-lg btn-block'},$CGI->span({-class => 'h2'},'Verwerfen'));

  my $STForm = $CGI->start_form({-id => 'Settings',-class => 'form-horizontal',-action => ''});
  foreach my $year ($ThisYear,$LastYear) {
    $STForm .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 h2'},$year == '0000' ? 'Allgemeine Einstellungen' : $year));
    $STForm .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'));
    foreach my $key (sort(keys(%{$AppConfig->{'0'}->{$year}}))) {
      my $Label = $AppConfig->{'0'}->{$year}->{$key}->{'Description'} ? $AppConfig->{'0'}->{$year}->{$key}->{'Description'} : '';
      $STForm .= Element->new({'LabelClass' => 'col-md-5','Class' => 'col-md-4','HelpClass' => 'col-md-3','FieldClass' => 'setting','LeftLabel' => FALSE,'ID' => $key.'_'.$year,'Name' => 'New_'.$year.'_'.$key,'Label' => $Label,'Value' => $AppConfig->{'0'}->{$year}->{$key}->{'Setting'}})->output();
      $STForm .= Element->new({'ID' => $key.'_'.$year.'_Old','Type' => 'Hidden','Name' => 'Old_'.$year.'_'.$key,'Value' => $AppConfig->{'0'}->{$year}->{$key}->{'Setting'}})->output();
    }
    $STForm .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;'))
  }
  $STForm .= Element->new({'ID' => 'ST_UserID','Type' => 'Hidden','Name' => 'UserID','Value' => '0'})->output();
  $STForm .= $CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 col-md-offset-2 text-center'},$ST_Save).$CGI->div({-class => 'col-xs-12 visible-xs-block'},'&nbsp;') . $CGI->div({-class => 'col-xs-12 col-sm-6 col-md-4 text-center'},$ST_Cancel));
  $STForm .= $CGI->end_form();

# Set Content
  $Settings->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h1('Einstellungen'))));
  $Settings->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p(''))));
  $Settings->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
  $Settings->appendPane($STForm);
  $Settings->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));

# Include Content
  $Administration->appendElement($Settings);


#****************************************
# Gesamtes Protokoll
#****************************************

  my $AllActivityLog  = Dropdown::Element->new({'ID' => 'allactivitylog','Order' => ++$AdminOrder,'Title' => 'Gesamtes Protokoll'});

# Get Data
  my $All_Log_Cols  = ['Datum','Von','Für','Aktivität'];
  my $All_Log_Table = $CGI->table({-id => 'AllActivityLog',-class => 'table table-striped'},$CGI->thead($CGI->Tr($CGI->th($All_Log_Cols))),$CGI->tfoot($CGI->Tr($CGI->th($All_Log_Cols))));

# Set Content
  $AllActivityLog->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->h1('Gesamtes Protokoll'))));
  $AllActivityLog->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->p('Das Protokoll zeigt dir wer was wann im System gemacht hat. Als Admin siehst Du hier alle Einträge im Protokoll. Unter &lt;Mein Protokoll&gt; kannst Du und alle anderen Teilnehmer nur das sehen, was für einen selbst gemacht wurde &mdash; egal von wem. Du kannst die Liste nach beliebigem Text filtern.'))));
  $AllActivityLog->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));
  $AllActivityLog->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},$CGI->div({-class => 'table-responsive'},$All_Log_Table))));
  $AllActivityLog->appendPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},'&nbsp;')));

# Include Content
  $Administration->appendElement($AllActivityLog);


#****************************************
# Administration-Dropdown zur NavBar
#****************************************

  $NavBars->append(NavBar->new({$Administration->toNavBar(),'Order' => 80}));


#******************************************************************************
#
# Tab: Tests
#
#******************************************************************************

  if ($Auth->isGroupMember('superadmin')) {

#  my $TestOrder = 0;

#  my $Test = Dropdown->new({'ID' => 'tests','Title' => 'Tests'});


#****************************************
# Test1
#****************************************

#  my $Test1   = Dropdown::Element->new({'ID' => 'test1','Order' => ++$TestOrder,'Title' => 'Test 1'});

#  if (open(FILE,BASE . '/htdocs/lib/md/hilfe.md')) {
#    my $Content  = do { local $/; <FILE> };
#    close FILE;

#    $Test1->setPane($CGI->div({-class => 'row'},$CGI->div({-class => 'col-xs-12'},Text::Markdown::Discount::markdown($Content))));

#  }


# Include Content
#  $Test->appendElement($Test1);

#****************************************
# Trennlinie
#****************************************

#  $Test->appendElement(Dropdown::Element->new({'ID' => 'divider'.$TestOrder,'Order' => ++$TestOrder}));


#****************************************
# Trennlinie
#****************************************

#  $Test->appendElement(Dropdown::Element->new({'ID' => 'nolink'.$TestOrder,'Order' => ++$TestOrder,'Title' => 'Dies ist Version '}));

#****************************************
# Administration-Dropdown zur NavBar
#****************************************

#  $NavBars->append(NavBar->new({$Test->toNavBar(),'Order' => 90}));


#******************************************************************************
# Tab: debug
#******************************************************************************

    my $Debug = NavBar->new({'ID' => 'debug','Order' => 99,'Title' => 'Debug'});

    my $ParticipationAggregated = $DB->getParticipation({'Year' => 2016})->{'Data'};


    $Debug->setPane(
      $CGI->p({-class => 'text-center visible-xs-block'},'Current Device: Extra Small').
      $CGI->p({-class => 'text-center visible-sm-block'},'Current Device: Small').
      $CGI->p({-class => 'text-center visible-md-block'},'Current Device: Medium').
      $CGI->p({-class => 'text-center visible-lg-block'},'Current Device: Large')
    );

    my $Accordion = Accordion->new();
    my $Panel = [];

    my $p = 0;
    $Panel->[$p] = Panel->new({'ID' => 'Debug'.$p});
    $Panel->[$p]->setHead('$CurrentUser');
    $Panel->[$p]->setContent(Data::Dumper->Dump([$CurrentUser],['CurrentUser']));
    $Panel->[$p]->setContentClass('panel-body pre pre-scrollable');


    $p++;
    $Panel->[$p] = Panel->new({'ID' => 'Debug'.$p});
    $Panel->[$p]->setHead('$Config');
    $Panel->[$p]->setContent(Data::Dumper->Dump([$Config],['Config']));
    $Panel->[$p]->setContentClass('panel-body pre pre-scrollable');


    $p++;
    $Panel->[$p] = Panel->new({'ID' => 'Debug'.$p});
    $Panel->[$p]->setHead('$AppConfig');
    $Panel->[$p]->setContent(Data::Dumper->Dump([$AppConfig],['AppConfig']));
    $Panel->[$p]->setContentClass('panel-body pre pre-scrollable');


    $p++;
    $Panel->[$p] = Panel->new({'ID' => 'Debug'.$p});
    $Panel->[$p]->setHead('$Holidays');
    $Panel->[$p]->setContent(Data::Dumper->Dump([$Holidays],['Holidays']));
    $Panel->[$p]->setContentClass('panel-body pre pre-scrollable');


    $p++;
    $Panel->[$p] = Panel->new({'ID' => 'Debug'.$p});
    $Panel->[$p]->setHead('$DaylistStart');
    $Panel->[$p]->setContent(Data::Dumper->Dump([$DaylistStart],['DaylistStart']));
    $Panel->[$p]->setContentClass('panel-body pre pre-scrollable');


    $p++;
    $Panel->[$p] = Panel->new({'ID' => 'Debug'.$p});
    $Panel->[$p]->setHead('$FutureMatchdays');
    $Panel->[$p]->setContent(Data::Dumper->Dump([$FutureMatchdays],['FutureMatchdays']));
    $Panel->[$p]->setContentClass('panel-body pre pre-scrollable');


    $p++;
    $Panel->[$p] = Panel->new({'ID' => 'Debug'.$p});
    $Panel->[$p]->setHead('$Daylist');
    $Panel->[$p]->setContent(Data::Dumper->Dump([$Daylist],['Daylist']));
    $Panel->[$p]->setContentClass('panel-body pre pre-scrollable');


    $Accordion->set('Panels',$Panel);

    $Debug->appendPane($Accordion->output());

    $NavBars->append($Debug) if (-e BASE . '/.debug');

  } # Nur für Superadmins
} # Nur für Admins und Superadmins


#******************************************************************************
# Tab: logout
#******************************************************************************

$NavBars->append(NavBar->new({'ID' => 'logout','Order' => 90,'Title' => 'Abmelden'}));


#******************************************************************************
# Additional CSS Code
#******************************************************************************

my $CSSCode = <<END_CSS;
END_CSS


#******************************************************************************
# Additional JavaScript Code
#******************************************************************************

my $JSCode = <<END_JSC;
END_JSC


#******************************************************************************
# Put Content and Navigation together
#******************************************************************************

$NavBars->activate($Session->param('ActivePane')) if ($Session->param('ActivePane'));
$Session->clear('ActivePane');

my $Template = WebSite::Template->new({'TemplatePath' => BASE . '/htdocs/lib/templates','TemplateFile' => 'bootstrap-navbar.template'});
$Template->setVar('Title',$Config->('UI.Title'));
$Template->setVar('NavBar',$NavBars->output('Title'));
$Template->setVar('Content',$NavBars->output('Pane'));
$Template->setVar('CSSCode',$CSSCode);
$Template->setVar('JSCode',$JSCode);
$Template->setVar('TAG',$TAG) if ($TAG);
$Template->setVar('JavaScript','/lib/js/Badminton_Admin.js'.($TAG ? '?'.$TAG : '')) if ($Auth->isGroupMember('superadmin') or $Auth->isGroupMember('admin'));


###############################################################################
#
# Print HTML
#
###############################################################################

my $Params  = $CGI->Vars;
if ($Params->{'Dump'}) {
  print $CGI->header(-type => 'text/plain',-charset => 'UTF-8');
  print $Template->dump();
  print $NavBars->dump();
  exit;
}

print $Session->header(-charset => 'UTF-8');
warningsToBrowser(1);
print $Template->print();

exit;
