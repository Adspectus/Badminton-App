#!/usr/bin/perl

use constant { TRUE => 1, FALSE => 0, BASE => $ENV{'VIRTUAL_ROOT'} };
use lib BASE . '/perl-lib';
use open qw( :encoding(UTF-8) :std );
use strict;
use utf8;
use warnings;
use Badminton::DB;
use Badminton::Functions qw(getDateFormatted sendMail);
use Config::Merge;
use Data::Dumper;
use POSIX qw(locale_h);

$Data::Dumper::Indent = 1;
$Data::Dumper::Purity = 1;

setlocale(LC_ALL, "de_DE.UTF-8");

my $Config = Config::Merge->new('path' => BASE . '/config','is_local' => qr/local/i);

my $DEBUG          = -e BASE . '/.debug' ? 1 : 0;
my $DB             = Badminton::DB->new({'Host' => $Config->('DB.Host'),'Port' => $Config->('DB.Port'),'Database' => $Config->('DB.Database'),'DB_User' => $Config->('DB.User'),'DB_Pass' => $Config->('DB.Password')});
my $PastMatchdays  = $DB->getPastMatchdays()->{'Data'};
my $OpenMatchdays  = { map { $_ => $PastMatchdays->{$_} } grep { $PastMatchdays->{$_}->{'Closed'} == 0 } keys(%{$PastMatchdays}) };

exit unless (scalar(keys(%{$OpenMatchdays})));

my $Players        = $DB->getPlayers()->{'Data'};

if ($DEBUG) { print STDERR Data::Dumper->Dump([$Players],['Players']),Data::Dumper->Dump([$OpenMatchdays],['OpenMatchdays']) }

my $Recipient     = $Config->('Email.ToName').' <'.$Config->('Email.ToMail').'>';
my @Recipients    = ($Recipient);
my $Subject       = $Config->('UI.Title') . " Erinnerung: Spieltage abschließen";
my $Message       = "Nachfolgende Spieltage sind noch nicht abgeschlossen:\n\n";
$Message         .= join("\n",map { &getDateFormatted('Long',$_) } sort(keys(%{$OpenMatchdays})))."\n";
my $ReplyTo       = $Config->('Email.FromName').' <'.$Config->('Email.FromMail').'>';

if ($DEBUG) { print STDERR "Recipients: ",join(",",@Recipients),"\n","Reply-To:   $ReplyTo\n","Subject:    $Subject\n\n",$Message,"\n"; }
else { push(@Recipients,map { $Players->{$_}->{'Firstname'}.' '.$Players->{$_}->{'Lastname'}.' <'.$Players->{$_}->{'EMail'}.'>' } @{$DB->getAdmins()->{'Data'}}); }

sendMail(\@Recipients,$Subject,$Message,$ReplyTo,FALSE,$Config);

exit;
