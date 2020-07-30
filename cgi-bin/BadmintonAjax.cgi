#!/usr/bin/perl

use constant { TRUE => 1, FALSE => 0, BASE => $ENV{'VIRTUAL_ROOT'} };
use lib '/srv/www/perl-lib',BASE . '/perl-lib';
#use open qw( :encoding(UTF-8) :std );
use strict;
#use utf8;
use warnings;
use Badminton::DB;
use Badminton::Functions qw(:all);
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use CGI::Session;
use CGI::Session::Auth::DBI;
use Config::Merge;
use Data::Dumper;
use Digest::MD5 qw(md5_hex);
use Encode qw(decode encode);
use JSON -convert_blessed_universally;
use POSIX qw(locale_h);
use Time::Piece;

$Data::Dumper::Indent = 1;
$Data::Dumper::Purity = 1;

setlocale(LC_ALL, "de_DE.UTF-8");

my $Config = Config::Merge->new('path' => BASE . '/config','is_local' => qr/local/i);


#******************************************************************************
# Settings
#******************************************************************************

my $CGI             = CGI->new();
my $Session         = CGI::Session->new(undef, $CGI, {Directory=>'/tmp'});
my $Output          = {'JSON' => \&_printJSON,'HTML' => \&_printHTML};
my $DB              = Badminton::DB->new({'Host' => $Config->('DB.Host'),'Database' => $Config->('DB.Database'),'DB_User' => $Config->('DB.User'),'DB_Pass' => $Config->('DB.Password')});
my $Params          = {'Format' => 'JSON',%{$CGI->Vars}};
$Params->{'Format'} = 'JSON' unless (exists($Output->{$Params->{'Format'}}));
my $JSON            = JSON->new->utf8(1)->allow_nonref(1)->allow_blessed(1)->convert_blessed(1);


#******************************************************************************
# Check Authentication
#******************************************************************************

my $Auth            = CGI::Session::Auth::DBI->new({CGI => $CGI,Session => $Session,LoginVarPrefix => $Config->('UI.LoginVarPrefix'),DBHandle => $DB->get('Handle'),'EncryptPW' => 1,'PasswordField' => 'password','IPAuth' => 1});

$Auth->authenticate();

unless ($Auth->loggedIn) {
  $Output->{$Params->{'Format'}}->('ERROR: User not authenticated!');
  exit;
}


#******************************************************************************
# Check Action: Exit if no valid Action
#******************************************************************************

my $Actions     = {
  'delGuest'                   => \&delGuest,
  'existsUsername'             => \&existsUsername,
  'getActivityLog'             => \&getActivityLog,
  'getAllActivityLog'          => \&getAllActivityLog,
  'getContributions'           => \&getContributions,
  'getParticipationList'       => \&getParticipationList,
  'getPlayerList'              => \&getPlayerList,
  'getPlayerData'              => \&getPlayerData,
  'getPlayerParticipation'     => \&getPlayerParticipation,
  'reopenMatchday'             => \&reopenMatchday,
  'resetParticipation'         => \&resetParticipation,
  'saveContributions'          => \&saveContributions,
  'saveCourts'                 => \&saveCourts,
  'saveEditPlayer'             => \&saveEditPlayer,
  'saveFutureMatchday'         => \&saveFutureMatchday,
  'saveNewMatchday'            => \&saveNewMatchday,
  'saveMatchday'               => \&saveMatchday,
  'saveNewGuest'               => \&saveNewGuest,
  'saveNewPlayer'              => \&saveNewPlayer,
  'saveParticipation'          => \&saveParticipation,
  'savePassword'               => \&savePassword,
  'savePersonalData'           => \&savePersonalData,
  'saveSettings'               => \&saveSettings,
};

unless (exists($Params->{'Action'})) {
  $Output->{$Params->{'Format'}}->('ERROR: Parameter Action is missing!');
  exit;
}

unless (exists($Actions->{$Params->{'Action'}})) {
  $Output->{$Params->{'Format'}}->('ERROR: Action "'.$Params->{'Action'}.'" not implemented!');
  exit;
}


#******************************************************************************
# Get necessary data
#******************************************************************************

my $NextMatchday         = $DB->getNextMatchday()->{'Data'};
my $Players              = $DB->getPlayers()->{'Data'};
my $CurrentUser          = $Players->{$Auth->profile('userid')};
my $Guests               = $DB->getGuests()->{'Data'};
my $ThisYear             = &getDateFormatted('Year');
my $LastYear             = $ThisYear - 1;


#******************************************************************************
# Call Output subroutine with Action subroutine as parameter
#******************************************************************************

$Output->{$Params->{'Format'}}->($Actions->{$Params->{'Action'}}->());

exit;


#******************************************************************************
# Formats
#******************************************************************************

sub _printJSON {
  my $Content = shift;
  $JSON->pretty(1)->canonical(1) if ($Params->{'Debug'});
  print $CGI->header(-charset => 'UTF-8',-type => 'application/json');
  print $JSON->encode($Content);
}

sub _printHTML {
  my $Content = shift;
  print $CGI->header(-charset => 'UTF-8',-type => 'text/html');
#  warningsToBrowser(1);
  print $Content;
}


#******************************************************************************
# Actions
#******************************************************************************

# Read-Only

sub existsUsername {
  my $Username = $Params->{'Benutzername'};
  my $UserID   = $Params->{'userid'};
  if (defined($UserID)) {
    return {'valid' => JSON::true} if (lc($Username) eq lc($Players->{$UserID}->{'username'}));
  }
  my %Usernames = map { lc($Players->{$_}->{'username'}) => 1 } keys(%{$Players});
  return {'valid' => JSON::false} if ($Usernames{lc($Username)});
  return {'valid' => JSON::true};
}

sub getActivityLog {
  my $Result = $DB->getActivityLog({'UserID' => $Auth->profile('userid')});
  return $Result;
}

sub getAllActivityLog {
  my $Result = $DB->getActivityLog();
  return $Result;
}

sub getContributions {
  my $FormData = CGI->new($Params->{'FormData'})->Vars;
  return [$FormData] if ($Params->{'Debug'});
  my $UserID = $FormData->{'UserID'};
  my @Years = split("\0",$FormData->{'Year'});
  my $Contributions = {};
  foreach my $year (@Years) {
    my $Result = $DB->getContributions({'Year' => $year});
    if ($Result->{'Success'}) {
      $Contributions->{$year} = $Result->{'Data'}->{$UserID};
      delete($Contributions->{$year}->{'UserID'});
      delete($Contributions->{$year}->{'Year'});
    }
  }
  return {'Success' => JSON::true,'Message' => '','Data' => $Contributions};
}

sub getParticipationList {
  my $Result = $DB->getParticipationList();
  return $Result;
}

sub getPlayerData {
  my $UserID = $Params->{'UserID'};
  my $Result = $DB->getContributions({'Year' => $ThisYear})->{'Data'};
  $Players->{$UserID}->{'Fee'} = $Result->{$UserID}->{'Fee'};
  return {'Success' => JSON::true,'Message' => '','Result' => $Players->{$UserID}};
}

sub getPlayerList {
  my @PlayerList = ();
  foreach my $id (sort {$Players->{$a}->{'SortID'} <=> $Players->{$b}->{'SortID'}} grep { $Players->{$_}->{'Excluded'} == 0 } keys(%{$Players})) {
    my $PhoneDisplay = &getPhoneFormatted($Players->{$id}->{'CountryCode'},$Players->{$id}->{'GeoCode'},$Players->{$id}->{'SubscriberCode'});
    my $PhoneLink = $PhoneDisplay;
    $PhoneLink =~ s/&nbsp;/-/g if ($PhoneLink);
    push(@PlayerList,{
      'Name'          => {'display' => $Players->{$id}->{'Lastname'}.', '.$Players->{$id}->{'Firstname'},'sort' => $Players->{$id}->{'SortID'}},
      'Benutzername'  => $Players->{$id}->{'username'},
      'EMail'         => $Players->{$id}->{'EMail'},
      'Telefon'       => {'display' => $PhoneDisplay,'link' => $PhoneLink},
#      'Eintritt'      => &getDateFormatted('Tiny',$Players->{$id}->{'EntryDate'}),
      'Aktiv'         => $Players->{$id}->{'Active'} ? 'Aktiv' : 'Passiv',
#      'DefaultStatus' => $Players->{$id}->{'Default_Status'} ? 'Teilnahme' : 'Absage',
    });
  }
  return {'Success' => JSON::true,'Message' => '','Data' => [@PlayerList]};
}

sub getPlayerParticipation {
  my $UserID = $Params->{'UserID'};
  my $Participation = $DB->getParticipationByUser({'UserID' => $UserID})->{'Data'};
  my $NextMatchday  = $DB->getNextMatchday()->{'Data'};
  my $NextMatchdays = $DB->getNextMatchdays()->{'Data'};
  my %StatusByDate  = map { $_ => $Participation->{$_}->{'Status'} } ($NextMatchday,@{$NextMatchdays});
  foreach my $date (@{$NextMatchdays}) {
    $StatusByDate{$date} = -1 unless (defined($StatusByDate{$date}));
  }
  return {'Success' => JSON::true,'Message' => $Players->{$UserID}->{'Default_Status'} ? 'Zusagen' : 'Absagen','Data' => {%StatusByDate}};
}

# Read-Write

sub delGuest {
  my $Date = $Params->{'Date'};
  my $Guest  = $Params->{'ID'};
  return [$Date,$Guest] if ($Params->{'Debug'});
  my $Result = $DB->delGuest({'ID' => $Guest});
  $DB->log({'UserID' => $Guests->{$Guest}->{'UserID'},'Change_By' => $Auth->profile('userid'),'Activity' => 'Gast '.encode("utf8",$Guests->{$Guest}->{'Firstname'}).' '.encode("utf8",$Guests->{$Guest}->{'Lastname'}).' für '.&getDateFormatted('Simple',$Date).' gelöscht.'}) if ($Result->{'Success'});
  return {'Success' => $Result->{'Success'} ? JSON::true : JSON::false,'Message' => $Result->{'Message'},'Data' => undef};
}

sub reopenMatchday {
  my $Date = $Params->{'Date'};
  return [$Date] if ($Params->{'Debug'});
  my $Result = $DB->reopenMatchday({'Date' => $Date,'Last_Change_By' => $Auth->profile('userid')});
  $DB->log({'UserID' => '0','Change_By' => $Auth->profile('userid'),'Activity' => 'Spieltag vom '.&getDateFormatted('Simple',$Date).' wiedereröffnet.'}) if ($Result->{'Success'});
  return {'Success' => $Result->{'Success'} ? JSON::true : JSON::false,'Message' => $Result->{'Message'},'Data' => $Result->{'Data'}};
}

sub resetParticipation {
  return {'Success' => JSON::true,'Data' => $CurrentUser->{'Default_Status'} } if ($Params->{'Debug'});
  my $Result = $DB->resetParticipation({'UserID' => $Auth->profile('userid')});
  $DB->log({'UserID' => $Auth->profile('userid'),'Change_By' => $Auth->profile('userid'),'Activity' => 'Zukünftige Teilnahme auf Standard zurückgesetzt.'}) if ($Result->{'Success'});
  return {'Success' => $Result->{'Success'} ? JSON::true : JSON::false,'Message' => $Result->{'Message'},'Data' => $CurrentUser->{'Default_Status'}};
}

sub saveContributions {
  my $FormData = CGI->new($Params->{'FormData'})->Vars;
  return [$FormData] if ($Params->{'Debug'});
  my $UserID = $FormData->{'UserID'};
  my @Years = split("\0",$FormData->{'Year'});
  foreach my $year (@Years) {
    my $FeeStatus = $FormData->{'FeeStatus_'.$year} eq 'on' ? '1' : '0';
    my $LateStatus = $FormData->{'LateStatus_'.$year} eq 'on' ? '1' : '0';
    my $GuestsStatus = $FormData->{'GuestsStatus_'.$year} eq 'on' ? '1' : '0';
    my $Result = $DB->saveContributions({'UserID' => $UserID,'Year' => $year,'FeeStatus' => $FeeStatus,'LateStatus' => $LateStatus,'GuestsStatus' => $GuestsStatus});
    $DB->log({'UserID' => $UserID,'Change_By' => $Auth->profile('userid'),'Activity' => 'Beitragsstatus aktualisiert.'}) if ($Result->{'Success'});
  }
  return {'Success' => JSON::true,'Message' => '','Data' => undef};
}

sub saveCourts {
  my $Date = $Params->{'Date'};
  my $FormData = CGI->new($Params->{'FormData'})->Vars;
  return [$Date,$FormData] if ($Params->{'Debug'});
  my $Courts = $FormData->{'CourtsSet'};
  my $Result = $DB->saveCourts({'Date' => $Date,'Courts' => $Courts,'Last_Change_By' => $Auth->profile('userid')});
  $DB->log({'UserID' => '0','Change_By' => $Auth->profile('userid'),'Activity' => 'Spieltag '.&getDateFormatted('Simple',$Date).': Spielzeiten festgelegt.'}) if ($Result->{'Success'});
  return {'Success' => $Result->{'Success'} ? JSON::true : JSON::false,'Message' => $Result->{'Message'},'Data' => undef};
}

sub saveEditPlayer {
  my $FormData = CGI->new($Params->{'FormData'})->Vars;
  return $FormData if ($Params->{'Debug'});
  my $UserID = $FormData->{'UserID'};
  my $PData = {};
  my $Password = &makePassword();
  $PData->{'Firstname'} = $FormData->{'Vorname'};
  $PData->{'Lastname'} = $FormData->{'Nachname'};
  $PData->{'EMail'} = $FormData->{'EMail'};
  $PData->{'Active'} = exists($FormData->{'Aktiv'}) ? '1' : '0';
  if ($PData->{'Active'}) { $PData->{'Default_Status'} = exists($FormData->{'Default_Status'}) ? '1' : '0'; }
  else { $PData->{'Default_Status'} = '-1'; }
  my $PResult = $DB->savePlayer({'UserID' => $UserID,'KeyValPairs' => $PData});
  if ($PResult->{'Success'}) {
    my $AData = {};
    $AData->{'username'} = $FormData->{'Benutzername'};
    $AData->{'password'} = md5_hex($Password) if ($FormData->{'Passwort'});
    my $AResult = $DB->saveUser({'UserID' => $UserID,'KeyValPairs' => $AData});
    if ($AResult->{'Success'}) {
      my $CResult = $DB->saveFee({'UserID' => $UserID,'Year' => $ThisYear,'Fee' => $FormData->{'Fee'}});
      if ($CResult->{'Success'}) {
        $DB->log({'UserID' => $UserID,'Change_By' => $Auth->profile('userid'),'Activity' => 'Teilnehmerdaten geändert.'});
        if ($FormData->{'Passwort'}) {
          my $Firstname  = decode("utf8",$PData->{'Firstname'});
          my $Lastname   = decode("utf8",$PData->{'Lastname'});
          my $Recipient  = [ $Firstname.' '.$Lastname.' <'.$PData->{'EMail'}.'>' ];
          my $ReplyTo    = $CurrentUser->{'Firstname'}.' '.$CurrentUser->{'Lastname'}.' <'.$CurrentUser->{'EMail'}.'>';
#          my $MailResult = &sendPassword($FormData->{'Benutzername'},$Password,$Recipient,$ReplyTo);
          my $Username   = $AData->{'username'};
          my $Subject    = $Config->('UI.Title').': Neues Passwort';
          my $Message    = "Hallo $Firstname!\n\n".decode("utf8","Dein neues Passwort für die Website $ENV{REQUEST_SCHEME}://$ENV{HTTP_HOST}/ lautet:\n\n$Password\n\nDein Benutzername ist: $Username\nViel Spaß!");
          my $MailResult = &sendMail($Recipient,$Subject,$Message,$ReplyTo,FALSE,$Config);
        }
      }
      return {'Success' => $CResult->{'Success'} ? JSON::true : JSON::false,'Message' => $CResult->{'Message'}};
    }
    return {'Success' => $AResult->{'Success'} ? JSON::true : JSON::false,'Message' => $AResult->{'Message'}};
  }
  return {'Success' => $PResult->{'Success'} ? JSON::true : JSON::false,'Message' => $PResult->{'Message'}};
}

sub saveFutureMatchday {
  my $Status = $Params->{'Status'};
  my $Date   = $Params->{'Date'};
  return [$Date,$Status] if ($Params->{'Debug'});
  my $ParticipationByDate = $DB->getParticipationByDate({'Date' => $NextMatchday})->{'Data'};
  my $Result = $DB->saveFutureMatchday({'Date' => $Date,'Status' => $Status,'Last_Change_By' => $Auth->profile('userid')});
  if ($Result->{'Success'}) {
    $DB->log({'UserID' => '0','Change_By' => $Auth->profile('userid'),'Activity' => 'Spieltagstatus für '.&getDateFormatted('Simple',$Date).' geändert auf "'.($Status ? 'Findet statt' : 'Findet nicht statt').'".'});
    if ($Status == 0) {
      my $Recipients = [ map { $Players->{$_}->{'Firstname'}.' '.$Players->{$_}->{'Lastname'}.' <'.$Players->{$_}->{'EMail'}.'>' } @{&getParticipants($ParticipationByDate)} ];
      my $ReplyTo    = $CurrentUser->{'Firstname'}.' '.$CurrentUser->{'Lastname'}.' <'.$CurrentUser->{'EMail'}.'>';
      my $Holidays   = &getHolidays();
      my $DateExt    = exists($Holidays->{$Date}) ? ' ('.$Holidays->{$Date}.')' : '';
      my $Subject    = $Config->('UI.Title').': Spieltag abgesagt!';
      my $Datum      = &getDateFormatted('Simple',$Date).$DateExt;
      my $Message    = qq(Der Spieltag am $Datum wurde soeben abgesagt!);
      my $MailResult = &sendMail($Recipients,$Subject,$Message,$ReplyTo,TRUE,$Config);
    }
  }
  return {'Success' => $Result->{'Success'} ? JSON::true : JSON::false,'Message' => $Result->{'Message'},'Data' => undef};
}

sub saveNewMatchday {
  my $FormData = CGI->new($Params->{'FormData'})->Vars;
  return [$FormData] if ($Params->{'Debug'});
  my $Data = {'Date' => $FormData->{'Date'},'Status' => '0'};
  my $Result = $DB->saveNewMatchday({'KeyValPairs' => $Data});
  $DB->log({'UserID' => '0','Change_By' => $Auth->profile('userid'),'Activity' => 'Neuen Spieltag am '.&getDateFormatted('Simple',$FormData->{'Date'}).' hinzugefügt.'}) if ($Result->{'Success'});
  return {'Success' => $Result->{'Success'} ? JSON::true : JSON::false,'Message' => $Result->{'Message'},'Data' => $Result->{'Data'}};
}

sub saveMatchday {
  my $Date = $Params->{'Date'};
  my $FormData = CGI->new($Params->{'FormData'})->Vars;
  return [$Date,$FormData] if ($Params->{'Debug'});
  my $Courts = $FormData->{'Courts'};
  my $PlayerStatus = &deSerialize($FormData,'Player');
  my $GuestStatus = &deSerialize($FormData,'Guest');
#  return [$PlayerStatus,$GuestStatus];
  my $ParticipationByDate = $DB->getParticipationByDate({'Date' => $Date})->{'Data'};
  foreach my $id (keys(%{$PlayerStatus})) {
    my $OnTime = $ParticipationByDate->{$id}->{'Status'} == $PlayerStatus->{$id} ? $ParticipationByDate->{$id}->{'OnTime'} : '0';
    my $StatusBeforeClosure = $ParticipationByDate->{$id}->{'Status'};
    my $OnTimeBeforeClosure = $ParticipationByDate->{$id}->{'OnTime'} || '0';
#      if ($Players->{$id}->{'Active'} and ($Players->{$id}->{'EntryDate'} lt $Date)) {
#    $OnTime = $ParticipationByDate->{$id}->{'Status'} == $PlayerStatus->{$id} ? $ParticipationByDate->{$id}->{'OnTime'} : '0';
#    $StatusBeforeClosure = $ParticipationByDate->{$id}->{'Status'};
#    $OnTimeBeforeClosure = $ParticipationByDate->{$id}->{'OnTime'} || '0';
#      }
#      else {
#        $PlayerStatus->{$id} = '-1';
#        $OnTime = '1';
#        $StatusBeforeClosure = '-1';
#        $OnTimeBeforeClosure = '1';
#      }
    my $Result = $DB->saveParticipation({'UserID' => $id,'Date' => $Date,'Status' => $PlayerStatus->{$id},'OnTime' => $OnTime,'Final' => '1','StatusBeforeClosure' => $StatusBeforeClosure,'OnTimeBeforeClosure' => $OnTimeBeforeClosure,'Last_Change_By' => $Auth->profile('userid')});
    $DB->log({'UserID' => $id,'Change_By' => $Auth->profile('userid'),'Activity' => 'Status für '.&getDateFormatted('Simple',$Date).' abgeschlossen: "'.($PlayerStatus->{$id} ? 'Teilgenommen' : 'Nicht teilgenommen').'"'}) if ($Result->{'Success'});
#    return {'Success' => JSON::false,'Message' => $Result->{'Message'},'Data' => {'UserID' => $id,'Date' => $Date,'Status' => $PlayerStatus->{$id},'OnTime' => $OnTime,'Final' => '1','StatusBeforeClosure' => $StatusBeforeClosure,'OnTimeBeforeClosure' => $OnTimeBeforeClosure,'Last_Change_By' => $Auth->profile('userid')}};
  }

  foreach my $id (keys(%{$GuestStatus})) {
    unless ($GuestStatus->{$id}) {
      my $Result = $DB->delGuest({'ID' => $id});
      $DB->log({'UserID' => '0','Change_By' => $Auth->profile('userid'),'Activity' => 'Gast '.$id.' für '.&getDateFormatted('Simple',$Date).' gelöscht'}) if ($Result->{'Success'});
    }
  }

  my $Count = scalar(grep { $_ == 1 } values(%{$PlayerStatus}));
  my $Result = $DB->saveMatchday({'Date' => $Date,'Courts' => $Courts,'Players' => $Count,'Last_Change_By' => $Auth->profile('userid')});
  $DB->log({'UserID' => '0','Change_By' => $Auth->profile('userid'),'Activity' => 'Spieltag '.&getDateFormatted('Simple',$Date).' abgeschlossen.'}) if ($Result->{'Success'});

  return {'Success' => $Result->{'Success'} ? JSON::true : JSON::false,'Message' => $Result->{'Message'},'Data' => undef};
}

sub saveNewGuest {
  my $FormData = CGI->new($Params->{'FormData'})->Vars;
  return [$FormData] if ($Params->{'Debug'});
  my $Data = {};
  $Data->{'Date'} = $FormData->{'Date'};
  $Data->{'UserID'} = exists($FormData->{'Host'}) ? $FormData->{'Host'} : $Auth->profile('userid');
  $Data->{'Firstname'} = $FormData->{'Vorname'};
  $Data->{'Lastname'} = $FormData->{'Nachname'};
  my $Result = $DB->saveNewGuest({'KeyValPairs' => $Data});
  $DB->log({'UserID' => $Data->{'UserID'},'Change_By' => $Auth->profile('userid'),'Activity' => 'Gast '.$Data->{'Firstname'}.' '.$Data->{'Lastname'}.' für '.&getDateFormatted('Simple',$Data->{'Date'}).' eingetragen.'}) if ($Result->{'Success'});
  return {'Success' => $Result->{'Success'} ? JSON::true : JSON::false,'Message' => $Result->{'Message'},'Data' => $Result->{'Data'}};
}

sub saveNewPlayer {
  my $FormData = CGI->new($Params->{'FormData'})->Vars;
  return $FormData if ($Params->{'Debug'});
  my $PData = {};
  $PData->{'Firstname'} = $FormData->{'Vorname'};
  $PData->{'Lastname'} = $FormData->{'Nachname'};
  $PData->{'EMail'} = $FormData->{'EMail'};
  $PData->{'EntryDate'} = &getDateFormatted('MySQL');
  my $PResult = $DB->saveNewPlayer({'KeyValPairs' => $PData});
  if ($PResult->{'Success'}) {
    my $AData = {};
    my $Password = &makePassword();
    $AData->{'userid'} = $PResult->{'Data'};
    $AData->{'username'} = $FormData->{'Benutzername'};
    $AData->{'password'} = md5_hex($Password);
    my $AResult = $DB->saveNewUser({'KeyValPairs' => $AData});
    if ($AResult->{'Success'}) {
      $DB->log({'UserID' => $PResult->{'Data'},'Change_By' => $Auth->profile('userid'),'Activity' => 'Neuen Teilnehmer erstellt.'});
      my $Firstname  = decode("utf8",$PData->{'Firstname'});
      my $Lastname   = decode("utf8",$PData->{'Lastname'});
      my $Recipient  = [ $Firstname.' '.$Lastname.' <'.$PData->{'EMail'}.'>' ];
      my $ReplyTo    = $CurrentUser->{'Firstname'}.' '.$CurrentUser->{'Lastname'}.' <'.$CurrentUser->{'EMail'}.'>';
#      my $MailResult = &sendCredentials($FormData->{'Benutzername'},$Password,$Recipient,$ReplyTo);
      my $Username   = $AData->{'username'};
      my $Subject    = $Config->('UI.Title').': Zugangsdaten';
      my $Message    = "Hallo $Firstname!\n\n".decode("utf8","Deine Zugangsdaten für die Website $ENV{REQUEST_SCHEME}://$ENV{HTTP_HOST}/ lauten:\n\nBenutzername: $Username\nPasswort:     $Password\n\n\nViel Spaß!");
      my $MailResult = &sendMail($Recipient,$Subject,$Message,$ReplyTo,FALSE,$Config);
    }
    return {'Success' => $AResult->{'Success'} ? JSON::true : JSON::false,'Message' => $AResult->{'Message'}};
  }
  return {'Success' => $PResult->{'Success'} ? JSON::true : JSON::false,'Message' => $PResult->{'Message'}};
}

sub saveParticipation {
  my $NextMatchday  = $DB->getNextMatchday()->{'Data'};
  my $Status        = $Params->{'Status'};
  my $UserID        = exists($Params->{'UserID'}) ? $Params->{'UserID'} : $Auth->profile('userid');
  my $Date          = exists($Params->{'Date'}) ? $Params->{'Date'} : $NextMatchday;
  my $DayBefore     = &getDayBefore($Date);
  my $Now           = localtime;
  my $OnTime        = '1';
  $OnTime           = '0' if (($Now->ymd eq $Date) or ($Now->ymd eq $DayBefore and $Now->hour >= 18));
  return [$Status,$UserID,$Date,$OnTime,$Auth->profile('userid')] if ($Params->{'Debug'});
  my $Result = $DB->saveParticipation({'UserID' => $UserID,'Date' => $Date,'Status' => $Status,'OnTime' => $OnTime,'Last_Change_By' => $Auth->profile('userid')});
  $DB->log({'UserID' => $UserID,'Change_By' => $Auth->profile('userid'),'Activity' => 'Status für '.&getDateFormatted('Simple',$Date).' geändert auf "'.($Status ? 'Zugesagt' : 'Abgesagt').'"'}) if ($Result->{'Success'});
  return {'Success' => $Result->{'Success'} ? JSON::true : JSON::false,'Message' => $Result->{'Message'}};
}

sub savePassword {
  my $FormData = CGI->new($Params->{'FormData'})->Vars;
  return $FormData if ($Params->{'Debug'});
  my $UserID = $FormData->{'UserID'};
  my $Password = $FormData->{'Passwort'};
  my $Password2 = $FormData->{'Passwort2'};
  return {'Success' => JSON::false,'Message' => 'The passwords do not match!'} unless ($Password eq $Password2);
  my $Result = $DB->savePassword({'UserID' => $UserID,'Password' => md5_hex($Password)});
  $DB->log({'UserID' => $UserID,'Change_By' => $Auth->profile('userid'),'Activity' => 'Passwort geändert.'}) if ($Result->{'Success'});
  return {'Success' => $Result->{'Success'} ? JSON::true : JSON::false,'Message' => $Result->{'Message'}};
}

sub savePersonalData {
  my $FormData = CGI->new($Params->{'FormData'})->Vars;
  return $FormData if ($Params->{'Debug'});
  my $UserID = $FormData->{'UserID'};
  my $PData = {};
  $PData->{'EMail'} = $FormData->{'EMail'};
  if ($FormData->{'Telefon_GC'}) {
    $PData->{'GeoCode'} = $FormData->{'Telefon_GC'};
  }
  if ($FormData->{'Telefon_SC'}) {
    $PData->{'SubscriberCode'} = $FormData->{'Telefon_SC'};
  }
  if ($FormData->{'Geburtstag'}) {
    my ($day,$month,$year) = split(/\./,$FormData->{'Geburtstag'});
    $PData->{'Birthday'} = sprintf("%04d-%02d-%02d",$year,$month,$day);
  }
  $PData->{'Default_Status'} = exists($FormData->{'Default_Status'}) ? '1' : '0';
  my $PResult = $DB->savePlayer({'UserID' => $UserID,'KeyValPairs' => $PData});
  if ($PResult->{'Success'}) {
    my $AData = {};
    $AData->{'username'} = $FormData->{'Benutzername'};
    my $AResult = $DB->saveUser({'UserID' => $UserID,'KeyValPairs' => $AData});
    if ($AResult->{'Success'}) {
      $DB->log({'UserID' => $UserID,'Change_By' => $Auth->profile('userid'),'Activity' => 'Teilnehmerdaten geändert.'});
    }
    return {'Success' => $AResult->{'Success'} ? JSON::true : JSON::false,'Message' => $AResult->{'Message'}};
  }
  return {'Success' => $PResult->{'Success'} ? JSON::true : JSON::false,'Message' => $PResult->{'Message'}};
}

sub saveSettings {
  my $FormData = CGI->new($Params->{'FormData'})->Vars;
  return $FormData if ($Params->{'Debug'});
  my $UserID = $FormData->{'UserID'};
  my $OldData = &deSerialize($FormData,'Old');
  my $NewData = &deSerialize($FormData,'New');
  my $Error = 0;
  my $Message = '';
  foreach my $key (keys(%{$NewData})) {
    my ($Year,$Parameter) = split(/_/,$key,2);
    unless (exists($OldData->{$key})) {
      my $Result = $DB->saveSetting({'UserID' => $UserID,'Year' => $Year,'Parameter' => $Parameter,'Setting' => $NewData->{$key}});
      $DB->log({'UserID' => '0','Change_By' => $Auth->profile('userid'),'Activity' => 'Parameter '.$Parameter.' für '.$Year.' auf '.$NewData->{$key}.' gesetzt.'}) if ($Result->{'Success'});
      $Message .= $Result->{'Message'}."\n";
      $Error++ unless ($Result->{'Success'});
    }
    else {
      unless ($NewData->{$key} == $OldData->{$key}) {
        my $Result = $DB->saveSetting({'UserID' => $UserID,'Year' => $Year,'Parameter' => $Parameter,'Setting' => $NewData->{$key}});
        $DB->log({'UserID' => '0','Change_By' => $Auth->profile('userid'),'Activity' => 'Parameter '.$Parameter.' für '.$Year.' von '.$OldData->{$key}.' auf '.$NewData->{$key}.' geändert.'}) if ($Result->{'Success'});
        $Message .= $Result->{'Message'}."\n";
        $Error++ unless ($Result->{'Success'});
      }
    }
  }
  return {'Success' => $Error ? JSON::false : JSON::true,'Message' => $Message,'Data' => undef};
}
