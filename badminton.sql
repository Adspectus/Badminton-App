CREATE DATABASE IF NOT EXISTS `badminton` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `badminton`;
-- MySQL dump 10.13  Distrib 5.7.30, for Linux (x86_64)
--
-- Host: localhost    Database: badminton
-- ------------------------------------------------------
-- Server version	5.5.5-10.1.44-MariaDB-0+deb9u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity_log`
--

DROP TABLE IF EXISTS `activity_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_log` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `UserID` int(3) unsigned NOT NULL DEFAULT '0',
  `Change_By` int(3) unsigned NOT NULL DEFAULT '0',
  `Activity` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `groupname` varchar(32) NOT NULL DEFAULT '',
  `userid` tinyint(3) unsigned NOT NULL DEFAULT '0',
  UNIQUE KEY `groupname` (`groupname`,`userid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_ip`
--

DROP TABLE IF EXISTS `auth_ip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_ip` (
  `userid` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `network` varchar(15) NOT NULL DEFAULT '',
  `netmask` varchar(15) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `userid` tinyint(3) unsigned NOT NULL,
  `username` varchar(32) NOT NULL DEFAULT '',
  `password` varchar(32) NOT NULL DEFAULT '',
  PRIMARY KEY (`userid`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `contributions`
--

DROP TABLE IF EXISTS `contributions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `contributions` (
  `UserID` tinyint(3) unsigned NOT NULL,
  `Year` year(4) NOT NULL,
  `Fee` smallint(5) unsigned NOT NULL DEFAULT '0',
  `FeeStatus` set('0','1') NOT NULL DEFAULT '0',
  `Late` smallint(5) unsigned NOT NULL DEFAULT '0',
  `LateStatus` set('0','1') NOT NULL DEFAULT '0',
  `Guests` smallint(5) unsigned NOT NULL DEFAULT '0',
  `GuestsStatus` set('0','1') NOT NULL DEFAULT '0',
  UNIQUE KEY `UserID` (`UserID`,`Year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guests`
--

DROP TABLE IF EXISTS `guests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guests` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Date` date NOT NULL DEFAULT '0000-00-00',
  `UserID` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `Firstname` varchar(64) NOT NULL,
  `Lastname` varchar(64) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `locale`
--

DROP TABLE IF EXISTS `locale`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `locale` (
  `Parameter` varchar(32) NOT NULL,
  `Description` varchar(128) NOT NULL DEFAULT '',
  PRIMARY KEY (`Parameter`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locale`
--

LOCK TABLES `locale` WRITE;
/*!40000 ALTER TABLE `locale` DISABLE KEYS */;
INSERT INTO `locale` VALUES
  ('DefaultCourts','Spielzeiten für neue Spieltage (Standardwert)'),
  ('Fee','Eigenbeitrag in € (Standardwert)'),
  ('GuestContribution','Beitrag für Gäste pro Besuch in €'),
  ('LateFreeShots','Freischüsse fürs zu späte Ab- oder Zusagen'),
  ('LatePenalty','Strafe fürs zu späte Ab- oder Zusagen in €'),
  ('ParticipationDeadline','Zeitpunkt vor Spielbeginn ab dem die Abstimmung als zu spät vermerkt wird in Sekunden'),
  ('PricePerCourt','Preis für 1 Platz und 1 Spielzeit in €'),
  ('MatchDay','Spieltag (Montag = 0, Dienstag = 1, usw.)'),
  ('MatchTime','Spielbeginn (HH:MM)'),
  ('NextMatchdays','Anzahl der Spieltage für die zukünftige Teilnahme');
/*!40000 ALTER TABLE `locale` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `matchdays`
--

DROP TABLE IF EXISTS `matchdays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `matchdays` (
  `Date` date NOT NULL,
  `Remark` varchar(128) DEFAULT NULL,
  `Courts` tinyint(3) unsigned NOT NULL DEFAULT '9',
  `Players` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `Status` tinyint(1) NOT NULL DEFAULT '1',
  `Closed` tinyint(1) NOT NULL DEFAULT '0',
  `Last_Change_By` tinyint(3) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`Date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `AfterUpdateMatchdays` AFTER UPDATE ON `matchdays` FOR EACH ROW BEGIN
IF NEW.Closed <> OLD.Closed THEN
	BEGIN
    IF NEW.Closed = '1' THEN
    	BEGIN
        Call UpdateContributions();
        INSERT INTO activity_log SET Activity = 'Prozedur UpdateContributions vom Trigger AfterUpdateMatchdays gerufen.';
        END;
    END IF;
	END;
END IF;
IF NEW.Status <> OLD.Status THEN
	BEGIN
    IF NEW.Status = '0' THEN
        DELETE FROM participation WHERE Date = NEW.Date;
    END IF;
	CALL SetParticipation();
    INSERT INTO activity_log SET Activity = 'Prozedur SetParticipation vom Trigger AfterUpdateMatchdays gerufen.';
	END;
END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `participation`
--

DROP TABLE IF EXISTS `participation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `participation` (
  `UserID` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `Date` date NOT NULL DEFAULT '0000-00-00',
  `Status` tinyint(1) DEFAULT NULL,
  `OnTime` tinyint(1) NOT NULL DEFAULT '1',
  `Final` tinyint(1) NOT NULL DEFAULT '0',
  `StatusBeforeClosure` tinyint(1) DEFAULT NULL,
  `OnTimeBeforeClosure` tinyint(1) NOT NULL DEFAULT '1',
  `Last_Change_By` int(3) unsigned NOT NULL DEFAULT '0',
  UNIQUE KEY `UserID` (`UserID`,`Date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `players`
--

DROP TABLE IF EXISTS `players`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `players` (
  `ID` tinyint(3) unsigned NOT NULL AUTO_INCREMENT,
  `SortID` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `Firstname` varchar(64) NOT NULL DEFAULT '',
  `Lastname` varchar(64) NOT NULL DEFAULT '',
  `EMail` varchar(64) NOT NULL DEFAULT '',
  `CountryCode` int(3) unsigned DEFAULT NULL,
  `GeoCode` int(5) unsigned DEFAULT NULL,
  `SubscriberCode` int(10) unsigned DEFAULT NULL,
  `EntryDate` date DEFAULT NULL,
  `Birthday` date DEFAULT NULL,
  `Default_Status` tinyint(1) NOT NULL DEFAULT '0',
  `Active` tinyint(1) NOT NULL DEFAULT '1',
  `Excluded` set('0','1') NOT NULL DEFAULT '0',
  `ExitDate` date DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `SetStatusOnInsert` AFTER INSERT ON `players` FOR EACH ROW BEGIN
INSERT INTO participation SET UserID = NEW.ID,Date = GetNextMatchday(),Status = NEW.Default_Status;
INSERT INTO contributions SET UserID = NEW.ID,Year = YEAR(NOW()),Fee = GetFee(YEAR(NOW()));
INSERT INTO contributions SET UserID = NEW.ID,Year = YEAR(NOW())-1;
INSERT INTO activity_log SET Activity = 'Werte in participation und contributions vom Trigger SetStatusOnInsert eingefügt.';
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `ChangeExitDateOnUpdate` BEFORE UPDATE ON `players` FOR EACH ROW BEGIN
IF OLD.Active <> NEW.Active THEN
	BEGIN
    IF NEW.Active = '0' THEN
        BEGIN
        SET NEW.ExitDate = CURDATE();
        END;
    END IF;
    IF NEW.Active = '1' THEN
        BEGIN
        SET NEW.ExitDate = NULL;
        END;
    END IF;
    INSERT INTO activity_log SET Activity = 'ExitDate in players vom Trigger ChangeExitDateOnUpdate geändert.';
	END;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `ChangeStatusOnUpdate` AFTER UPDATE ON `players` FOR EACH ROW BEGIN
IF OLD.Default_Status <> NEW.Default_Status THEN
	BEGIN
	UPDATE participation SET Status = NEW.Default_Status WHERE UserID = NEW.ID AND Date = GetNextMatchday() AND Last_Change_By = '0';
    INSERT INTO activity_log SET Activity = 'Status in participation vom Trigger ChangeStatusOnUpdate geändert.';
    END;
END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `settings` (
  `UserID` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `Year` year(4) NOT NULL DEFAULT '0000',
  `Parameter` varchar(32) NOT NULL,
  `Setting` varchar(32) NOT NULL,
  UNIQUE KEY `UserID` (`UserID`,`Year`,`Parameter`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `AfterUpdateSettings` AFTER UPDATE ON `settings` FOR EACH ROW BEGIN
IF NEW.Setting <> OLD.Setting THEN
	BEGIN
    IF NEW.Parameter = 'Fee' THEN
    	BEGIN
        UPDATE contributions SET Fee = NEW.Setting WHERE Fee = OLD.Setting AND Year = NEW.Year;
        INSERT INTO activity_log SET Activity = 'Eigenbeitrag in contributions vom Trigger AfterUpdateSettings angepasst.';
        END;
    END IF;
	END;
END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Dumping events for database 'badminton'
--
/*!50106 SET @save_time_zone= @@TIME_ZONE */ ;
/*!50106 DROP EVENT IF EXISTS `CloseParticipation` */;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = '' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`localhost`*/ /*!50106 EVENT `CloseParticipation` ON SCHEDULE EVERY 1 DAY STARTS '2018-02-08 19:30:00' ON COMPLETION PRESERVE ENABLE DO CALL CloseParticipation() */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
/*!50106 DROP EVENT IF EXISTS `NewYear` */;;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = '' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`localhost`*/ /*!50106 EVENT `NewYear` ON SCHEDULE EVERY 1 YEAR STARTS '2019-01-01 00:01:00' ON COMPLETION PRESERVE ENABLE DO BEGIN
CALL CloneSettings();
CALL CleanHistory();
END */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
DELIMITER ;
/*!50106 SET TIME_ZONE= @save_time_zone */ ;

--
-- Dumping routines for database 'badminton'
--
/*!50003 DROP FUNCTION IF EXISTS `GetFee` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `GetFee`(`ThisYear` YEAR(4)) RETURNS int(11)
    READS SQL DATA
    SQL SECURITY INVOKER
BEGIN
DECLARE amount INT(6);
SELECT Setting FROM settings WHERE UserID = '0' AND Year = ThisYear AND Parameter = 'Fee' INTO amount;
RETURN amount;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `GetFullname` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `GetFullname`(`userid` INT) RETURNS varchar(128) CHARSET utf8
    READS SQL DATA
    SQL SECURITY INVOKER
BEGIN
DECLARE fullname VARCHAR(128);
IF userid = '0' THEN SET fullname = 'SYSTEM';
ELSE SELECT CONCAT_WS(' ',Firstname,Lastname) FROM players WHERE ID = userid INTO fullname;
END IF;
RETURN fullname;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `GetNextMatchday` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `GetNextMatchday`() RETURNS date
    READS SQL DATA
    SQL SECURITY INVOKER
BEGIN
DECLARE var_date DATE;
SELECT Date INTO var_date
FROM matchdays
WHERE (Date > DATE(NOW()) OR (Date = DATE(NOW()) AND HOUR(NOW()) < (SELECT HOUR(Setting) FROM settings WHERE UserID = '0' AND Year = '0000' AND Parameter = 'MatchTime')) OR (Date = DATE(NOW()) AND HOUR(NOW()) = (SELECT HOUR(Setting) FROM settings WHERE UserID = '0' AND Year = '0000' AND Parameter = 'MatchTime') AND MINUTE(NOW()) < (SELECT MINUTE(Setting) FROM settings WHERE UserID = '0' AND Year = '0000' AND Parameter = 'MatchTime')))
AND Status = '1'
ORDER BY Date
LIMIT 1;
RETURN var_date;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `GetSortID` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `GetSortID`(`userid` INT) RETURNS int(11)
    READS SQL DATA
    SQL SECURITY INVOKER
BEGIN
DECLARE sort INT(3);
IF userid = '0' THEN SET sort = 0;
ELSE SELECT SortID FROM players WHERE ID = userid INTO sort;
END IF;
RETURN sort;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `GetThisMatchday` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `GetThisMatchday`() RETURNS date
    READS SQL DATA
    SQL SECURITY INVOKER
BEGIN
DECLARE var_date DATE;
SELECT Date INTO var_date
FROM matchdays
WHERE (Date = DATE(NOW()))
AND Status = '1'
ORDER BY Date
LIMIT 1;
RETURN var_date;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `CleanHistory` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `CleanHistory`()
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
BEGIN
DELETE FROM participation WHERE YEAR(Date) < YEAR(NOW())-1;
DELETE FROM matchdays WHERE YEAR(Date) < YEAR(NOW())-1;
DELETE FROM guests WHERE YEAR(Date) < YEAR(NOW())-1;
DELETE FROM contributions WHERE Year < YEAR(NOW())-1;
DELETE FROM settings WHERE Year BETWEEN 2000 AND YEAR(NOW())-2;
DELETE FROM activity_log WHERE YEAR(Timestamp) < YEAR(NOW())-1;
INSERT INTO activity_log SET Activity = 'Prozedur CleanHistory ausgeführt.';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `CloneSettings` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `CloneSettings`()
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
BEGIN
INSERT INTO settings (UserID,Year,Parameter,Setting) SELECT settings.UserID,settings.Year + 1 AS Year,settings.Parameter,settings.Setting FROM settings WHERE settings.Year = YEAR(NOW())-1;
REPLACE INTO settings (UserID,Year,Parameter,Setting) VALUES('0',YEAR(NOW()),'Fee','0');
INSERT INTO contributions (UserID,Year,Fee) SELECT players.ID,YEAR(NOW()) AS Year,GetFee(YEAR(NOW())) * players.Active AS Fee FROM players;
INSERT INTO activity_log SET Activity = 'Prozedur CloneSettings ausgeführt.';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `CloseParticipation` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `CloseParticipation`()
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
this_proc:BEGIN
IF (ISNULL(GetThisMatchday())) THEN BEGIN
  INSERT INTO activity_log SET Activity = 'Prozedur CloseParticipation abgebrochen, da kein Spieltag.';
  LEAVE this_proc;
  END;
END IF;
SET @p0=DATE(NOW());
UPDATE matchdays AS m INNER JOIN (SELECT Date,COUNT(*) AS Players FROM participation WHERE Date = @p0 AND Status = '1') AS p ON m.Date = p.Date SET m.Players = p.Players;
CALL SetParticipation();
CALL CreateMatchdays(@p0);
CALL ExcludePlayer();
INSERT INTO activity_log SET Activity = 'Prozedur CloseParticipation ausgeführt.';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `CreateMatchdays` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `CreateMatchdays`(IN `StartDate` DATE)
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
this_proc:BEGIN
DECLARE x INT;
DECLARE adate DATE;
DECLARE weekday INT;
SET x = 1;
SET weekday = (SELECT Setting FROM settings WHERE UserID = '0' AND Year = '0' AND Parameter = 'MatchDay');
IF (WEEKDAY(StartDate) <> weekday) THEN BEGIN
  LEAVE this_proc;
  END;
END IF;
REPEAT
  SET adate = (SELECT Date FROM matchdays WHERE Date = StartDate);
  IF adate IS NULL THEN BEGIN
    INSERT INTO matchdays (Date) VALUES (StartDate);
    END;
  END IF;
  SET StartDate = DATE_ADD(StartDate, INTERVAL 1 WEEK);
  SET  x = x + 1;
UNTIL x > 52
END REPEAT;
INSERT INTO activity_log SET Activity = 'Prozedur CreateMatchdays ausgeführt.';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `DeletePlayer` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `DeletePlayer`(IN `DelUserID` INT)
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
BEGIN
DELETE FROM settings WHERE UserID=DelUserID;
DELETE FROM players WHERE ID=DelUserID;
DELETE FROM participation WHERE UserID=DelUserID;
DELETE FROM contributions WHERE UserID=DelUserID;
DELETE FROM auth_user WHERE userid=DelUserID;
DELETE FROM auth_ip WHERE userid=DelUserID;
DELETE FROM auth_group WHERE userid=DelUserID;
DELETE FROM activity_log WHERE (UserID=DelUserID OR Change_By=DelUserID);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `ExcludePlayer` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `ExcludePlayer`()
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
BEGIN
DECLARE StartDate DATE;
SET StartDate = DATE(NOW()) - INTERVAL 52 WEEK;
UPDATE players SET Excluded = '1' WHERE ID IN (SELECT UserID FROM `participation` WHERE Date BETWEEN StartDate AND DATE(NOW()) GROUP BY UserID HAVING AVG(Status) = '-1');
DELETE FROM auth_user WHERE userid IN (SELECT ID FROM players WHERE Excluded = '1');
INSERT INTO activity_log SET Activity = 'Prozedur ExcludePlayer ausgeführt.';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `SetParticipation` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `SetParticipation`()
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
BEGIN
CREATE TEMPORARY TABLE temporary_state SELECT players.ID AS UserID,GetNextMatchday() AS Date,players.Default_Status AS Status,players.Default_Status AS StatusBeforeClosure FROM players WHERE players.Excluded = '0' AND NOT EXISTS (SELECT 1 FROM participation WHERE Date = GetNextMatchday() AND players.ID = participation.UserID);
INSERT INTO participation (UserID,Date,Status,StatusBeforeClosure) SELECT * FROM temporary_state;
INSERT INTO activity_log SET Activity = 'Prozedur SetParticipation ausgeführt.';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `UpdateContributions` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `UpdateContributions`()
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
BEGIN
CREATE TEMPORARY TABLE late_contribution SELECT p.UserID,s.Year,s.Setting * (COUNT(1) - (SELECT Setting FROM settings WHERE Parameter = 'LateFreeShots' AND Year = s.Year)) AS Amount FROM participation AS p LEFT JOIN settings AS s ON YEAR(p.Date) = s.Year WHERE s.Parameter = 'LatePenalty' AND p.OnTime = 0 AND p.Final = 1 GROUP BY YEAR(p.Date),p.UserID HAVING Amount > 0;
UPDATE contributions AS c,late_contribution AS l SET c.Late = l.Amount WHERE c.UserID = l.UserID AND c.Year = l.Year;
CREATE TEMPORARY TABLE guest_contribution SELECT g.UserID,s.Year,s.Setting * COUNT(*) AS Amount FROM guests AS g LEFT JOIN settings AS s ON YEAR(g.Date) = s.Year WHERE s.Parameter = 'GuestContribution' GROUP BY YEAR(g.Date),g.UserID;
UPDATE contributions AS c,guest_contribution AS g SET c.Guests = g.Amount WHERE c.UserID = g.UserID AND c.Year = g.Year;
INSERT INTO activity_log SET Activity = 'Prozedur UpdateContributions ausgeführt.';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `UpdateSortID` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `UpdateSortID`()
    MODIFIES SQL DATA
    SQL SECURITY INVOKER
BEGIN
SET @rownumber = 0;
UPDATE players SET SortID = (@rownumber:=@rownumber+1) ORDER BY Lastname,Firstname;
INSERT INTO activity_log SET Activity = 'Prozedur UpdateSortID ausgeführt.';
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
