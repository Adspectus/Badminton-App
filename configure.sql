-- 
-- Initial configuration for the badminton database
-- Delete or archive this file in a save place after importing to your database server
--
-- All of the following variables require a value!
--

SET @db_host       = '';      -- Hostname/IP of database server
SET @db_name       = '';      -- Name of database (must match the name used in badminton.sql!)
SET @db_user       = '';      -- MySQL user for database connection
SET @db_pass       = '';      -- Password of MySQL user for database connection

SET @my_user       = '';      -- The username of the first user with superuser privileges for the app
SET @my_pass       = '';      -- The password of the first user
SET @my_fname      = '';      -- The firstname of the first user
SET @my_lname      = '';      -- The lastname of the first user
SET @my_email      = '';      -- The emailaddress of the first user

SET @matchday      = '3';     -- The day of the week for the training (Monday = 0, Tuesday = 1, etc.)
SET @matchtime     = '19:30'; -- The time when the training starts (HH:MM)
SET @deadline      = '91800'; -- The deadline for voting in seconds before the training starts
SET @courts        = '9';     -- The number of courts which will be usually booked
SET @nextdays      = '8';     -- The number of next training dates shown in user interface

SET @fee           = '0';     -- The fee each player has to pay (per year)
SET @guestcontrib  = '5';     -- The fee a guest has to pay (per training)
SET @latefreeshots = '3';     -- The number of late votings without sanction
SET @latepenalty   = '5';     -- The fee for every late voting (minus free shots)
SET @pricepercourt = '12';    -- The price for each court

--
-- No changes after this line
-- 

SET @startdate = (SELECT CURDATE() + INTERVAL @matchday - WEEKDAY(CURDATE()) + IF(@matchday - WEEKDAY(CURDATE()) <= 0, 7, 0) DAY);
SET @thisyear = YEAR(CURDATE());
SET @nextyear = YEAR(CURDATE() + INTERVAL 1 YEAR);

--
-- Creation of db user
--

SET @create_user = CONCAT("CREATE USER ",@db_user,"@",@db_host," IDENTIFIED BY '",@db_pass,"'");
PREPARE stmt FROM @create_user;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @grant_user = CONCAT("GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE, TRIGGER, CREATE TEMPORARY TABLES ON ",@db_name,".* TO ",@db_user,"@",@db_host);
PREPARE stmt FROM @grant_user;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

FLUSH PRIVILEGES;

--
-- Insert default settings and creation of matchdays
--

SET @settings = CONCAT("INSERT INTO ",@db_name,".`settings` (Parameter,Setting) VALUES('MatchDay','",@matchday,"'), ('MatchTime','",@matchtime,"'), ('ParticipationDeadline','",@deadline,"'), ('DefaultCourts','",@courts,"'), ('NextMatchdays','",@nextdays,"')");
PREPARE stmt FROM @settings;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @settings = CONCAT("INSERT INTO ",@db_name,".`settings` (Year,Parameter,Setting) VALUES(",@thisyear,",'Fee','",@fee,"'), (",@thisyear,",'GuestContribution','",@guestcontrib,"'), (",@thisyear,",'LateFreeShots','",@latefreeshots,"'), (",@thisyear,",'LatePenalty','",@latepenalty,"'), (",@thisyear,",'PricePerCourt','",@pricepercourt,"')");
PREPARE stmt FROM @settings;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @create_matchdays = CONCAT("CALL ",@db_name,".CreateMatchdays(@startdate)");
PREPARE stmt FROM @create_matchdays;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

--
-- Creation of first user/player
--

SET @ins_user = CONCAT("INSERT INTO ",@db_name,".`auth_user` ","VALUES (1,'",@my_user,"','",MD5(@my_pass),"')");
PREPARE stmt FROM @ins_user;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @ins_group = CONCAT("INSERT INTO ",@db_name,".`auth_group` ","VALUES ('superadmin',1)");
PREPARE stmt FROM @ins_group;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @ins_ip = CONCAT("INSERT INTO ",@db_name,".`auth_ip` ","VALUES (1,'127.0.0.1','255.0.0.0')");
PREPARE stmt FROM @ins_ip;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @ins_player = CONCAT("INSERT INTO ",@db_name,".`players` (Firstname,Lastname,EMail,EntryDate) VALUES('",@my_fname,"','",@my_lname,"','",@my_email,"','",CURDATE(),"')");
PREPARE stmt FROM @ins_player;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
