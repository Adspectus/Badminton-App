package Badminton::DB;

use constant { TRUE => 1, FALSE => 0 };
use strict;
use warnings;
use Carp;
use DBI;


#******************************************************************************
# Constructor
#******************************************************************************

sub new {
  my ($class,$args) = (@_);
  my $self = {
    'DB'            => $args->{'Database'},
    'DB_User'       => $args->{'DB_User'},
    'DB_Pass'       => $args->{'DB_Pass'},
    'Driver'        => $args->{'Driver'}        || 'mysql',
    'Host'          => $args->{'Host'}          || 'localhost',
    'Port'          => $args->{'Port'}          || '3306',
    'Attributes'    => $args->{'Attributes'}    || { PrintError => 0,RaiseError => 1,mysql_enable_utf8 => 1 },
  };
  my $object = bless $self,$class;
  $object->_setHandle();
  $object->_setConfig();
  return $object;
}

sub set {
  my ($self,$key,$value) = (@_);
  $self->{$key} = $value;
}

sub get {
  my ($self,$key) = (@_);
  return $self->{$key};
}


#******************************************************************************
# Get methods
#******************************************************************************

sub getActivityLog { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $UserID        = $args->{'UserID'} || '%';
  my $Log = [];

  eval { $Log = $DBH->selectall_arrayref(qq{SELECT DATE_FORMAT(Timestamp,"%a., %e. %b. %Y, %T") AS Timestamp,GetFullname(UserID) AS ForUser,GetFullname(Change_By) AS ByUser,Activity FROM activity_log WHERE UserID LIKE ? ORDER BY UNIX_TIMESTAMP(Timestamp) DESC},{ Slice => {} },$UserID); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Log};
}

sub getAdmins { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Admins = [];

  eval { $Admins = $DBH->selectcol_arrayref("SELECT auth_user.userid FROM auth_user,auth_group WHERE auth_user.userid = auth_group.userid AND auth_group.groupname = 'Admin'"); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Admins};
}

sub getContributions { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Year = $args->{'Year'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter Year','Data' => undef} unless ($Year);
  my $Contributions = {};

  eval { $Contributions = $DBH->selectall_hashref("SELECT * FROM contributions WHERE Year = ?","UserID",undef,$Year); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Contributions};
}

sub getCourts { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Courts = {};

  eval { $Courts = $DBH->selectall_hashref("SELECT CONCAT(YEAR(Date),'-',QUARTER(Date)) AS Quarters,SUM(Courts) AS Courts,COUNT(*) AS MatchDays FROM matchdays WHERE Status = '1' AND Closed = '1' GROUP BY Quarters","Quarters"); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Courts};
}

sub getCourtsByDate { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Date = $args->{'Date'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter Date','Data' => undef} unless ($Date);
  my $Courts = {};

  eval { $Courts = $DBH->selectcol_arrayref("SELECT Courts,Last_Change_By FROM matchdays WHERE Date = ?",{Columns => [1,2]},$Date); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Courts};
}

sub getFutureMatchdays { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Limit = $args->{'Limit'} || 28;
  my $Matchdays = {};

  eval { $Matchdays = $DBH->selectall_hashref("SELECT Date,Remark,Status FROM matchdays WHERE Date >= DATE(NOW()) AND Closed = 0 LIMIT ?","Date",undef,$Limit); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Matchdays};
}

sub getGuests { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Guests = {};

  eval { $Guests = $DBH->selectall_hashref("SELECT * FROM guests","ID"); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Guests};
}

sub getGuestParticipation {
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Year = $args->{'Year'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter Year','Data' => undef} unless ($Year);
  my $Guests = [];

  eval { $Guests = $DBH->selectall_arrayref("SELECT guests.* FROM guests JOIN matchdays ON (guests.Date = matchdays.Date) WHERE matchdays.Closed = 1 AND YEAR(guests.Date) = ?;",{ Slice => {} },$Year); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Guests};
}

sub getNextMatchday { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Matchday = '';

  eval { $Matchday = $DBH->selectrow_hashref("SELECT GetNextMatchday() AS Date"); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Matchday->{'Date'}};
}

sub getNextMatchdays { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Limit = $args->{'Limit'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter Limit','Data' => undef} unless ($Limit);
  my $Matchdays = [];

  eval { $Matchdays = $DBH->selectcol_arrayref("SELECT Date FROM matchdays WHERE Date > GetNextMatchday() AND Status = 1 ORDER BY Date LIMIT ?",undef,$Limit); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Matchdays};
}

sub getParticipation { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Year = $args->{'Year'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter Year','Data' => undef} unless ($Year);
  my $Participation = {};

  eval { $Participation = $DBH->selectall_hashref("SELECT UserID,SUM(IF(Status = '1','1','0')) AS Participation,SUM(IF(OnTime = '0','1','0')) AS TooLate FROM participation WHERE Final = '1' AND YEAR(Date) = ? GROUP BY UserID","UserID",undef,$Year); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Participation};
}

sub getParticipationByDate { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Date = $args->{'Date'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter Date','Data' => undef} unless ($Date);
#  my $ActiveOnly = exists($args->{'ActiveOnly'}) ? $args->{'ActiveOnly'} : TRUE;
#  my $Active = '1';
#  $Active = '%' unless ($ActiveOnly);
  my $Status = {};

  eval { $Status = $DBH->selectall_hashref("SELECT p.* FROM participation AS p JOIN players ON (p.UserID = players.ID) WHERE Date = ? AND players.Excluded = '0'","UserID",undef,$Date); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Status};
}

sub getParticipationByUser { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $UserID = $args->{'UserID'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter UserID','Data' => undef} unless ($UserID);
  my $Status = {};

  eval { $Status = $DBH->selectall_hashref("SELECT * FROM participation WHERE UserID = ?","Date",undef,$UserID); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Status};
}

sub getParticipationList { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $List = [];

  eval { $List = $DBH->selectall_arrayref(qq{SELECT DATE_FORMAT(Date,"%e. %M %Y") AS Timestamp,GetFullname(UserID) AS ForUser,IF(Status,IF(Status = '-1','Passiv','Ja'),'Nein') AS Status,IF(OnTime,IF(Status = '-1','&mdash;','Rechtzeitig'),'Zu spät') AS OnTime FROM participation WHERE Final = '1' ORDER BY UNIX_TIMESTAMP(Date) DESC, GetSortID(UserID) ASC},{ Slice => {} }); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $List};
}

sub getPastMatchdays { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Matchdays = {};

  eval { $Matchdays = $DBH->selectall_hashref("SELECT * FROM matchdays WHERE Date < GetNextMatchday() AND Status = 1","Date"); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Matchdays};
}

sub getPlayers { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $Players = {};

  eval { $Players = $DBH->selectall_hashref("SELECT players.*,auth_user.username,(SELECT groupname FROM auth_group WHERE userid = players.ID) AS groupname FROM players,auth_user WHERE auth_user.userid = players.ID","ID"); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $Players};
}

#sub getSettings { #
#  my ($self,$args) = (@_);
#  my $DBH = $self->get('Handle');
#  my $ByKeys = ['UserID','Year','Parameter'];
#  my $Settings = {};

#  eval { $Settings = $DBH->selectall_hashref("SELECT * FROM settings LEFT JOIN locale USING(Parameter)",$ByKeys); };

#  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
#  return {'Success' => TRUE,'Message' => '','Data' => _removeKeys($ByKeys,$Settings)};
#}

#******************************************************************************
# Set methods
#******************************************************************************

sub log { #
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $KeyVal = _Hash2String($args);
  $DBH->do("INSERT INTO activity_log SET $KeyVal");
}

sub delGuest { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $ID            = $args->{'ID'};

  eval { $DBH->do("DELETE FROM guests WHERE ID = ?",undef,$ID); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub removeGuests { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $Date          = $args->{'Date'};

  eval { $DBH->do("DELETE FROM guests WHERE Date = ?",undef,$Date); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub reopenMatchday { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $Date          = $args->{'Date'} || undef;
  my $ChangeBy      = $args->{'Last_Change_By'} || 0;
  return {'Success' => FALSE,'Message' => 'Missing parameter Date','Data' => undef} unless ($Date);

  eval {
    $DBH->do("UPDATE matchdays SET Closed = '0',Last_Change_By = ? WHERE Date = ?",undef,$ChangeBy,$Date);
    $DBH->do("UPDATE participation SET Status = StatusBeforeClosure,OnTime = OnTimeBeforeClosure,Final = '0' WHERE Date = ?",undef,$Date);
  };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub resetParticipation { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $UserID        = $args->{'UserID'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter UserID','Data' => undef} unless ($UserID);

  eval { $DBH->do("DELETE FROM participation WHERE Date > GetNextMatchday() AND UserID = ?",undef,$UserID); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub saveContributions { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $UserID        = $args->{'UserID'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter UserID','Data' => undef} unless ($UserID);
  my $Year          = $args->{'Year'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter Year','Data' => undef} unless ($Year);
  my $FeeStatus     = $args->{'FeeStatus'} || '0';
  my $LateStatus    = $args->{'LateStatus'} || '0';
  my $GuestsStatus  = $args->{'GuestsStatus'} || '0';

  eval { $DBH->do("UPDATE contributions SET FeeStatus = ?,LateStatus = ?,GuestsStatus = ? WHERE UserID = ? AND Year = ?",undef,$FeeStatus,$LateStatus,$GuestsStatus,$UserID,$Year); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub saveCourts { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $Date          = $args->{'Date'};
  my $Courts        = $args->{'Courts'};
  my $ChangeBy      = $args->{'Last_Change_By'} || 0;

  eval { $DBH->do("UPDATE matchdays SET Courts = ?,Last_Change_By = ? WHERE Date = ?",undef,$Courts,$ChangeBy,$Date); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub saveFee { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $UserID        = $args->{'UserID'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter UserID','Data' => undef} unless ($UserID);
  my $Year          = $args->{'Year'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter Year','Data' => undef} unless ($Year);
  my $Fee           = $args->{'Fee'} || 0;
#  return {'Success' => FALSE,'Message' => 'Missing parameter Fee','Data' => undef} unless ($Fee);

  eval { $DBH->do("UPDATE contributions SET Fee = ? WHERE UserID = ? AND Year = ?",undef,$Fee,$UserID,$Year); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub saveFutureMatchday { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $Date          = $args->{'Date'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter Date','Data' => undef} unless ($Date);
  my $Status        = $args->{'Status'};
  my $DefaultCourts = $args->{'DefaultCourts'} || undef;
  if ($Status) { return {'Success' => FALSE,'Message' => 'Missing parameter DefaultCourts','Data' => undef} unless ($DefaultCourts) };
  my $Courts        = $Status ? $args->{'DefaultCourts'} : '0';
  my $ChangeBy      = $args->{'Last_Change_By'} || 0;

  eval {
    $DBH->do("UPDATE matchdays SET Courts = ?,Status = ?,Last_Change_By = ? WHERE Date = ?",undef,$Courts,$Status,$ChangeBy,$Date);
#    $DBH->do("DELETE FROM participation WHERE Date = ?",undef,$Date);
#    $DBH->do("CALL SetParticipation()");
  };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub saveNewMatchday { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $Data          = $args->{'KeyValPairs'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter KeyValPairs','Data' => undef} unless ($Data);
  my $KeyVal        = _Hash2String($Data);
#  my $NewMatchday   = $Data->{'Date'};
#  my $NextMatchday  = $self->getNextMatchday()->{'Data'};
#  warn "$NewMatchday - $NextMatchday";
  eval {
    $DBH->do("INSERT INTO matchdays SET $KeyVal");
#    $DBH->do("CALL SetParticipation()") if ($NewMatchday < $NextMatchday);
  };

  return {'Success' => FALSE,'Message' => $KeyVal.$DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub saveMatchday { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');

  my $Date          = $args->{'Date'};
  my $Courts        = $args->{'Courts'};
  my $Players       = $args->{'Players'};
  my $ChangeBy      = $args->{'Last_Change_By'} || 0;

  eval { $DBH->do("UPDATE matchdays SET Courts = ?,Players = ?,Closed = '1',Last_Change_By = ? WHERE Date = ?",undef,$Courts,$Players,$ChangeBy,$Date); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub saveNewGuest { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $Data          = $args->{'KeyValPairs'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter KeyValPairs','Data' => undef} unless ($Data);
  my $KeyVal        = _Hash2String($Data);
  my $NewID;

  eval {
    $DBH->do("INSERT INTO guests SET $KeyVal");
    $NewID = $DBH->last_insert_id(undef,undef,undef,undef);
  };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $NewID};
}

sub saveNewPlayer { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $Data          = $args->{'KeyValPairs'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter KeyValPairs','Data' => undef} unless ($Data);
  my $KeyVal        = _Hash2String($Data);
  my $NewID;

  eval {
    $DBH->do("INSERT INTO players SET $KeyVal");
    $NewID = $DBH->last_insert_id(undef,undef,undef,undef);
    $DBH->do("CALL UpdateSortID()");
  };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => $NewID};
}

sub saveNewUser { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $Data          = $args->{'KeyValPairs'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter KeyValPairs','Data' => undef} unless ($Data);
  my $KeyVal        = _Hash2String($Data);

  eval { $DBH->do("INSERT INTO auth_user SET $KeyVal"); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub savePlayer { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $UserID        = $args->{'UserID'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter UserID','Data' => undef} unless ($UserID);
  my $Data          = $args->{'KeyValPairs'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter KeyValPairs','Data' => undef} unless ($Data);
  my $KeyVal        = _Hash2String($Data);

  eval {
    $DBH->do("UPDATE players SET $KeyVal WHERE ID = $UserID");
    $DBH->do("CALL UpdateSortID()");
  };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub savePassword { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $UserID        = $args->{'UserID'};
  my $Password      = $args->{'Password'};

  eval { $DBH->do("UPDATE auth_user SET password = '$Password' WHERE userid = $UserID"); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}


sub saveParticipation { #
  my ($self,$args) = (@_);
  my $DBH          = $self->get('Handle');
  my $UserID       = $args->{'UserID'};
  my $Date         = $args->{'Date'};
  my $Status       = $args->{'Status'};
  my $OnTime       = exists($args->{'OnTime'}) ? $args->{'OnTime'} : 1;
  my $Final        = exists($args->{'Final'}) ? $args->{'Final'} : 0;
  my $StatusBeforeClosure = exists($args->{'StatusBeforeClosure'}) ? $args->{'StatusBeforeClosure'} : $Status;
  my $OnTimeBeforeClosure = exists($args->{'OnTimeBeforeClosure'}) ? $args->{'OnTimeBeforeClosure'} : $OnTime;
  my $ChangeBy     = exists($args->{'Last_Change_By'}) ? $args->{'Last_Change_By'} : 0;

  eval { $DBH->do("REPLACE INTO participation SET UserID = ?,Date = ?,Status = ?,OnTime = ?,Final = ?,StatusBeforeClosure = ?,OnTimeBeforeClosure = ?,Last_Change_By = ?",undef,$UserID,$Date,$Status,$OnTime,$Final,$StatusBeforeClosure,$OnTimeBeforeClosure,$ChangeBy); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub saveSetting {
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $UserID        = exists($args->{'UserID'}) ? $args->{'UserID'} : undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter UserID','Data' => undef} unless (defined($UserID));
  my $Year          = exists($args->{'Year'}) ? $args->{'Year'} : undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter Year','Data' => undef} unless (defined($Year));
  my $Parameter     = $args->{'Parameter'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter Parameter','Data' => undef} unless ($Parameter);
  my $Setting       = $args->{'Setting'};

  eval { $DBH->do("UPDATE settings SET Setting = ? WHERE UserID = ? AND Year = ? AND Parameter = ?",undef,$Setting,$UserID,$Year,$Parameter); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}

sub saveUser { #
  my ($self,$args)  = (@_);
  my $DBH           = $self->get('Handle');
  my $UserID        = $args->{'UserID'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter UserID','Data' => undef} unless ($UserID);
  my $Data          = $args->{'KeyValPairs'} || undef;
  return {'Success' => FALSE,'Message' => 'Missing parameter KeyValPairs','Data' => undef} unless ($Data);
  my $KeyVal        = _Hash2String($Data);

  eval { $DBH->do("UPDATE auth_user SET $KeyVal WHERE userid = $UserID"); };

  return {'Success' => FALSE,'Message' => $DBI::errstr,'Data' => undef} if ($@);
  return {'Success' => TRUE,'Message' => '','Data' => ''};
}


#******************************************************************************
# Private methods
#******************************************************************************

sub _setHandle {
  my ($self,$args) = (@_);
  my $DSN = 'dbi:'.$self->get('Driver').':database='.$self->get('DB').';host='.$self->get('Host').';port='.$self->get('Port');
  my $DBH = DBI->connect($DSN,$self->get('DB_User'),$self->get('DB_Pass'),$self->get('Attributes')) or die $DBI::errstr;
  $DBH->do(qq{SET lc_time_names = 'de_DE'});
#  $DBH->{HandleError} = sub { $_[2] = [{'Success' => FALSE,'Message' => $_[0],'Data' => undef}]; return 1 };
  $self->set('Handle',$DBH);
}

sub _setConfig {
  my ($self,$args) = (@_);
  my $DBH = $self->get('Handle');
  my $ByKeys = ['UserID','Year','Parameter'];
  my $Settings = {};

  eval { $Settings = $DBH->selectall_hashref("SELECT * FROM settings LEFT JOIN locale USING(Parameter)",$ByKeys); };

  $self->set('Config',undef) if ($@);
  $self->set('Config',_removeKeys($ByKeys,$Settings));
}

sub _getConfig {
  my ($self,$parameter) = (@_);
  my $Config = $self->get('Config');
  return $Config->{'0'}->{'0000'}->{$parameter}->{'Setting'};
}

sub _Hash2String {
  my $Hash = shift;
  return undef unless(defined($Hash));
  my $String = join(',',map { "$_ = '".$Hash->{$_}."'" } keys(%{$Hash}));
  return $String;
}

sub _removeKeys {
  my $Keys = shift;
  my $Hash = shift;
  while (my ($key,$val) = each(%{$Hash})) {
    _removeKeys($Keys,$val) if (ref($val) eq "HASH");
    delete($Hash->{$_}) foreach @{$Keys};
    $Hash->{$key} = 1 if (ref($val) eq "HASH" and !%{$val});
  }
  return $Hash;
}

1;
