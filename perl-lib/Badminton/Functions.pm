package Badminton::Functions;

use constant { TRUE => 1, FALSE => 0 };
use strict;
use utf8;
use warnings;
use Carp;
#use Data::Dumper;
use Date::Calc qw(Add_Delta_Days Easter_Sunday);
use Email::MessageID;
use Email::Sender::Simple qw(sendmail try_to_sendmail);
use Email::Sender::Transport::SMTP;
use Email::Simple;
use Encode qw(decode encode);
use Exporter qw(import);
use POSIX qw(locale_h);
use Sys::Hostname;
use Time::Piece;
use Time::Seconds;

#$Data::Dumper::Indent = 1;
#$Data::Dumper::Purity = 1;

setlocale(LC_ALL, "de_DE.UTF-8");

our @EXPORT      = qw(deSerialize getCourtsFromPlayers getDateFormatted getDayBefore getHolidays getPhoneFormatted makePassword sendMail);
our @EXPORT_OK   = qw(getNonParticipants getOffTimeParticipants getParticipants getPassive);
our %EXPORT_TAGS = (all => [@EXPORT,@EXPORT_OK]);


sub deSerialize { #
  my ($FormData,$key) = (@_);
  my $HashRef = {};
  foreach (keys(%{$FormData})) {
    my ($a,$b) = split(/_/,$_,2);
    if (defined($key)) {
      if ($a eq $key) {
        $HashRef->{$b} = $FormData->{$_};
        $HashRef->{$b} = '1' if ($FormData->{$_} eq 'true' or $FormData->{$_} eq 'on');
        $HashRef->{$b} = '0' if ($FormData->{$_} eq 'false' or $FormData->{$_} eq 'off');
      }
    }
    else {
      $HashRef->{$b} = $FormData->{$_};
      $HashRef->{$b} = '1' if ($FormData->{$_} eq 'true' or $FormData->{$_} eq 'on');
      $HashRef->{$b} = '0' if ($FormData->{$_} eq 'false' or $FormData->{$_} eq 'off');
    }
  }
  return $HashRef;
}

sub getCourtsFromPlayers { #
  my $Players = shift;
  return 0 if ($Players < 2);
  return 1 if ($Players == 2);
  return 2 if ($Players == 3);
  return 2 if ($Players == 4);
  return 3 if ($Players == 5);
  return 5 if ($Players == 6); # Changed from 4 due to issue #16
  return 5 if ($Players == 7);
  return 6 if ($Players == 8);
  return 6 if ($Players == 9);
  return 8 if ($Players == 10);
  return 8 if ($Players == 11);
  return 9 if ($Players == 12);
  return 9 if ($Players == 13);
  return 9 if ($Players == 14);
  return 10 if ($Players == 15);
  return 11 if ($Players == 16);
  return 12 if ($Players == 17);
  return 12 if ($Players == 18);
  return 13 if ($Players == 19);
  return 14 if ($Players == 20);
  return 15 if ($Players > 20);
}

sub getDateFormatted { #
  my $Format = shift;
  my $t = shift || localtime;
  $t = Time::Piece->strptime($t,"%Y-%m-%d") if ($t =~ /^(\d{4}-\d{2}-\d{2})$/);
  return $t->strftime("%Y") if ($Format eq 'Year');
  return $t->strftime("%d.%m.%Y") if ($Format eq 'Simple');
  return $t->strftime("%Y-%m-%d") if ($Format eq 'MySQL');

  my $now = localtime;
  my $tom = $now + ONE_DAY;
  my $Date = '';
  my $Time = '';
  if ($Format =~ /Time/) {
    $Time = $t->strftime("%k") unless ($t->min);
    $Time = $t->strftime("%k:%M") if ($t->min);
  }

  if ($t->date eq $now->date) {
    $Date = 'Heute';
  }
  elsif ($t->date eq $tom->date) {
    $Date = 'Morgen';
  }
  else {
    $Date = $t->strftime("%A, %e. %B %Y") if ($Format =~ /^Long/);
    $Date = $t->strftime("%a., %e. %b. %Y") if ($Format =~ /^AbbrLong/);
    $Date = $t->strftime("%e. %B %Y") if ($Format =~ /^Medium/);
    $Date = $t->strftime("%a., %d.%m.%Y") if ($Format =~ /^Short/);
    $Date = $t->strftime("%d.%m.%Y") if ($Format =~ /^Tiny/);

  }

  return decode("utf8",$Date.($Time ? ', ' : '').$Time);
}

sub getDayBefore { #
  my $t = shift;
  $t = Time::Piece->strptime($t,"%Y-%m-%d") if ($t =~ /^(\d{4}-\d{2}-\d{2})$/);
  my $DayBefore = $t - ONE_DAY;
  return $DayBefore->strftime("%Y-%m-%d");
}

sub getHolidays { #
  my $t = localtime;
  my $Year = $t->year;
  my %FixedHolidays = ('01-01' => 'Neujahr','05-01' => 'Tag der Arbeit','10-03' => 'Tag der Deutschen Einheit','11-01' => 'Allerheiligen','12-25' => 'Weihnachten','12-26' => 'Weihnachten');
  my %OtherHolidays = ('12-24' => 'Heiligabend','12-31' => 'Silvester');
  my %FlexiHolidays = (
     -52 => 'Weiberfastnacht',
      -3 => 'Gründonnerstag',
      39 => 'Christi Himmelfahrt',
      60 => 'Fronleichnam',
  );
  my %Holidays = ();
  for my $year (($Year-1)..($Year+2)) {
    %Holidays = (%Holidays,map { $year.'-'.$_ => $FixedHolidays{$_} } keys(%FixedHolidays));
    %Holidays = (%Holidays,map { $year.'-'.$_ => $OtherHolidays{$_} } keys(%OtherHolidays));
    %Holidays = (%Holidays,map { sprintf("%04d-%02d-%02d",Add_Delta_Days(Easter_Sunday($year),$_)) => $FlexiHolidays{$_} } keys(%FlexiHolidays));
  }
  return { %Holidays };
}

sub getNonParticipants { #
  my $Participants = shift;
  my @NonParticipants;
  foreach my $userid (keys(%{$Participants})) {
    next unless (exists($Participants->{$userid}->{'Status'}));
    next unless ($Participants->{$userid}->{'Status'} == 0);
    push(@NonParticipants,$userid);
  }
  return [@NonParticipants];
}

sub getOffTimeParticipants { #
  my $Participants = shift;
  my @OffTime;
  foreach my $userid (keys(%{$Participants})) {
    next if ($Participants->{$userid}->{'OnTime'} == 1);
    push(@OffTime,$userid);
  }
  return [@OffTime];
}

sub getParticipants { #
  my $Participants = shift;
  my @Participants;
  foreach my $userid (keys(%{$Participants})) {
    next unless (exists($Participants->{$userid}->{'Status'}));
    next unless ($Participants->{$userid}->{'Status'} == 1);
    push(@Participants,$userid);
  }
  return [@Participants];
}

sub getPassive { #
  my $Participants = shift;
  my @Passive;
  foreach my $userid (keys(%{$Participants})) {
    next unless (exists($Participants->{$userid}->{'Status'}));
    next unless ($Participants->{$userid}->{'Status'} == -1);
    push(@Passive,$userid);
  }
  return [@Passive];
}

sub getPhoneFormatted {
  my ($CC,$GC,$SC) = (@_);
  my $PhoneNumber = '+49';
  return $PhoneNumber.'&nbsp;'.$GC.'&nbsp;'.$SC if ($GC and $SC);
  return '';
}

sub makePassword { #
  my @chars = ("A".."Z","a".."z",0..9);
  my $string;
  $string .= $chars[rand @chars] for 1..8;
  return $string;
}

sub sendMail { #
  my ($Recipients,$Subject,$Message,$ReplyTo,$BCC,$Config) = (@_);

  my $From = '"'.$Config->('Email.FromName');
  $From .= ' ('.$Config->('Environment').')' if ($Config->('Environment'));
  $From .= '" <'.$Config->('Email.FromMail').'>';

  $Subject = '['.$Config->('Environment').'] '.$Subject if ($Config->('Environment'));
  $Subject = encode('MIME-Header',$Subject);
  $Subject =~ s/\v+/\x20/g;

  if ($Config->('Environment')) {
    $Message   .= "\n\nDiese Mail wäre ";
    $Message   .= "als BCC " if $BCC;
    $Message   .= "an folgende Empfänger verschickt worden:\n\n";
    $Message   .= join("\n",@{$Recipients})."\n";
    my $Recipient = $Config->('Email.ToName').' <'.$Config->('Email.ToMail').'>';
    $Recipients = [$Recipient];
  }
  $Message .= "\n\nDiese Mail wurde automatisch erstellt und gesendet.\n";

  my $To = [ map { $_ =~ /^.*?\<(.*?)\>$/;$_ = $1 } @{$Recipients} ];

  my $Hostname = hostname;

  my $Transport = Email::Sender::Transport::SMTP->new({
    host => $Config->('Email.Host'),
    ssl  => $Config->('Email.SSL'),
    helo => $Hostname,
    sasl_username => $Config->('Email.User'),
    sasl_password => $Config->('Email.Password'),
  });

  my $Email = Email::Simple->create(
    header => [
      'To'                        => $BCC ? $From : join(',',@{$To}),
      'From'                      => $From,
      'Subject'                   => $Subject,
      'Content-Transfer-Encoding' => '8bit',
      'Content-type'              => 'text/plain; charset=UTF-8',
      'Message-Id'                => Email::MessageID->new(host => $Hostname)->in_brackets,
    ],
    body => encode('utf8',$Message),
  );

  $Email->header_set('Reply-To',$ReplyTo) if ($ReplyTo);

  my $Result = try_to_sendmail($Email,{
    to => $To,
    from => $Config->('Email.FromMail'),
    transport => $Transport,
  });

  return $Result;
}

1;
