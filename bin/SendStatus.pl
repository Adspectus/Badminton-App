#!/usr/bin/perl

use constant { TRUE => 1, FALSE => 0, BASE => $ENV{'VIRTUAL_ROOT'} };
use lib BASE . '/perl-lib';
use open qw( :encoding(UTF-8) :std );
use strict;
use utf8;
use warnings;
use Badminton::DB;
use Badminton::Functions qw(getCourtsFromPlayers getDateFormatted getDayBefore getNonParticipants getParticipants sendMail);
use Config::Merge;
use Data::Dumper;
use POSIX qw(locale_h);

$Data::Dumper::Indent = 1;
$Data::Dumper::Purity = 1;

setlocale(LC_ALL, "de_DE.UTF-8");

my $Config = Config::Merge->new('path' => BASE . '/config','is_local' => qr/local/i);

my $DEBUG         = -e BASE . '/.debug' ? 1 : 0;
my $DB            = Badminton::DB->new({'Host' => $Config->('DB.Host'),'Port' => $Config->('DB.Port'),'Database' => $Config->('DB.Database'),'DB_User' => $Config->('DB.User'),'DB_Pass' => $Config->('DB.Password')});
my $Players       = $DB->getPlayers()->{'Data'};
my $Guests        = $DB->getGuests()->{'Data'};
my $NextMatchday  = $DB->getNextMatchday()->{'Data'};
my $DayBefore     = &getDayBefore($NextMatchday);
my $Today         = &getDateFormatted('MySQL');

if ($DEBUG) { print STDERR Data::Dumper->Dump([$Players],['Players']),Data::Dumper->Dump([$Guests],['Guests']),"NextMatchday: $NextMatchday\nDayBefore:    $DayBefore\nToday:        $Today\n"; }
else { exit unless ($Today eq $DayBefore); }

my $Participation = $DB->getParticipationByDate({'Date' => $NextMatchday})->{'Data'};
my @Zusagen       = map { $Players->{$_}->{'Firstname'}.' '.$Players->{$_}->{'Lastname'} } sort { $Players->{$a}->{'SortID'} <=> $Players->{$b}->{'SortID'} } @{&getParticipants($Participation)};
my $CountZusagen  = scalar(@Zusagen) ? scalar(@Zusagen) : 'Keine';
my @Guests        = grep { $Guests->{$_}->{'Date'} eq $NextMatchday } keys(%{$Guests});
my $CountGuests   = scalar(@Guests) ? scalar(@Guests) : 'Keine';
my $Suggestion    = &getCourtsFromPlayers(scalar(@Zusagen) + scalar(@Guests));

my $Recipient     = $Config->('Email.ToName').' <'.$Config->('Email.ToMail').'>';
my @Recipients    = ($Recipient);
my $Subject       = $Config->('UI.Title') . " Morgen: $CountZusagen Zusagen";
$Subject         .= scalar(@Guests) ? " + " . scalar(@Guests) . (scalar(@Guests) == 1 ? " angemeldeter Gast" : " angemeldete Gäste") : '';
$Subject         .= " / " . ($Suggestion ? $Suggestion . " Spielzeiten empfohlen" : "Spieltag absagen");
my $Message       = scalar(@Zusagen) ? "Folgende Spieler haben zugesagt:\n\n" . join("\n",@Zusagen) : '';
$Message         .= scalar(@Guests) ? "\n\n\nFolgende Gäste wurden angemeldet:\n\n" . join("\n",map { $Guests->{$_}->{'Firstname'}.' '.$Guests->{$_}->{'Lastname'}.' (Gast von '.$Players->{$Guests->{$_}->{'UserID'}}->{'Firstname'}.' '.$Players->{$Guests->{$_}->{'UserID'}}->{'Lastname'}.')' } @Guests) : '';
$Message         .= "\n\n\nEmpfehlung: " . ($Suggestion ? $Suggestion . " Spielzeiten buchen." : "Spieltag absagen.") . "\n";
my $ReplyTo       = $Config->('Email.FromName').' <'.$Config->('Email.FromMail').'>';

if ($DEBUG) { print STDERR "Recipients: ",join(",",@Recipients),"\n","Reply-To:   $ReplyTo\n","Subject:    $Subject\n\n",$Message,"\n"; }
else { push(@Recipients,map { $Players->{$_}->{'Firstname'}.' '.$Players->{$_}->{'Lastname'}.' <'.$Players->{$_}->{'EMail'}.'>' } @{$DB->getAdmins()->{'Data'}}); }

sendMail(\@Recipients,$Subject,$Message,$ReplyTo,FALSE,$Config);

unless ($DEBUG) {
  my $Extern     = $Config->('Email.Extern.Name').' <'.$Config->('Email.Extern.Mail').'>';
  my @Externs    = ($Extern);

  sendMail(\@Externs,$Subject,'',$ReplyTo,FALSE,$Config);
}

exit;
