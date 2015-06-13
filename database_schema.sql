CREATE DATABASE  IF NOT EXISTS `extended` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `extended`;
-- MySQL dump 10.13  Distrib 5.5.43, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: extended
-- ------------------------------------------------------
-- Server version	5.5.43-0ubuntu0.14.04.1

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
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_5f412f9a` (`group_id`),
  KEY `auth_group_permissions_83d7f98b` (`permission_id`),
  CONSTRAINT `group_id_refs_id_f4b32aac` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `permission_id_refs_id_6ba0f519` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_37ef4eb4` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_d043b34a` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_6340c63c` (`user_id`),
  KEY `auth_user_groups_5f412f9a` (`group_id`),
  CONSTRAINT `group_id_refs_id_274b862c` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `user_id_refs_id_40c41112` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_6340c63c` (`user_id`),
  KEY `auth_user_user_permissions_83d7f98b` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_35d9ac25` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `user_id_refs_id_4dc23c39` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collectiongames`
--

DROP TABLE IF EXISTS `collectiongames`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collectiongames` (
  `groupindex` int(11) NOT NULL,
  `bggid` int(11) NOT NULL,
  `ckey` int(11) NOT NULL,
  `orderindex` int(11) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collectiongroups`
--

DROP TABLE IF EXISTS `collectiongroups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collectiongroups` (
  `groupindex` int(11) NOT NULL,
  `groupname` varchar(128) CHARACTER SET utf8 DEFAULT NULL,
  `groupdesc` varchar(512) CHARACTER SET utf8 DEFAULT NULL,
  `display` tinyint(4) NOT NULL,
  `ckey` int(11) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collections`
--

DROP TABLE IF EXISTS `collections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collections` (
  `geek` varchar(128) NOT NULL,
  `collectionname` varchar(256) DEFAULT NULL,
  `description` varchar(512) DEFAULT NULL,
  `collectionindex` int(11) NOT NULL,
  `ckey` int(11) NOT NULL,
  PRIMARY KEY (`ckey`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `designers`
--

DROP TABLE IF EXISTS `designers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `designers` (
  `name` varchar(254) NOT NULL DEFAULT '',
  `bggid` int(11) NOT NULL,
  `boring` tinyint(1) DEFAULT '0',
  `url` varchar(254) DEFAULT NULL,
  PRIMARY KEY (`bggid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_b7b81f0c` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `downloader`
--

DROP TABLE IF EXISTS `downloader`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `downloader` (
  `starttime` datetime NOT NULL,
  `endtime` datetime NOT NULL,
  `filesprocessed` int(11) NOT NULL,
  `waittime` float NOT NULL,
  `pausetime` float NOT NULL,
  `failures` int(11) NOT NULL,
  `users` int(11) NOT NULL,
  `games` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `expansions`
--

DROP TABLE IF EXISTS `expansions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `expansions` (
  `basegame` int(10) unsigned NOT NULL,
  `expansion` int(10) unsigned NOT NULL,
  KEY `expansions_basegame` (`basegame`),
  KEY `expansions_expansion` (`expansion`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `files`
--

DROP TABLE IF EXISTS `files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `files` (
  `filename` varchar(128) NOT NULL,
  `url` varchar(256) NOT NULL,
  `lastUpdate` datetime DEFAULT NULL,
  `processMethod` varchar(128) NOT NULL,
  `nextUpdate` datetime DEFAULT NULL,
  `geek` varchar(128) DEFAULT NULL,
  `tillNextUpdate` varchar(128) DEFAULT NULL,
  `description` varchar(256) DEFAULT NULL,
  `lastattempt` datetime DEFAULT NULL,
  UNIQUE KEY `files_url_unique` (`url`),
  KEY `files_geek` (`geek`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `frontpagegeek`
--

DROP TABLE IF EXISTS `frontpagegeek`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `frontpagegeek` (
  `geek` varchar(128) NOT NULL DEFAULT '',
  `totalPlays` int(10) NOT NULL DEFAULT '0',
  `distinctGames` int(10) NOT NULL DEFAULT '0',
  `top50` int(10) NOT NULL DEFAULT '0',
  `sdj` int(10) NOT NULL DEFAULT '0',
  `the100` int(10) NOT NULL DEFAULT '0',
  `owned` int(10) NOT NULL DEFAULT '0',
  `want` int(10) NOT NULL DEFAULT '0',
  `wish` int(10) NOT NULL DEFAULT '0',
  `trade` int(10) NOT NULL DEFAULT '0',
  `prevOwned` int(10) NOT NULL DEFAULT '0',
  `friendless` int(10) NOT NULL DEFAULT '0',
  `cfm` float DEFAULT '0',
  `utilisation` float DEFAULT '0',
  `tens` int(10) NOT NULL DEFAULT '0',
  `zeros` int(10) NOT NULL DEFAULT '0',
  `ext100` int(10) NOT NULL DEFAULT '0',
  `mv` int(10) NOT NULL DEFAULT '0',
  `hindex` int(10) NOT NULL DEFAULT '0'
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gameCategories`
--

DROP TABLE IF EXISTS `gameCategories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gameCategories` (
  `gameId` int(10) unsigned NOT NULL,
  `category` varchar(256) NOT NULL,
  KEY `category_game` (`gameId`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gameDesigners`
--

DROP TABLE IF EXISTS `gameDesigners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gameDesigners` (
  `gameId` int(10) unsigned NOT NULL,
  `designerId` int(11) NOT NULL,
  KEY `gameDesigners_game` (`gameId`),
  KEY `gameDesigners_designer` (`designerId`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gameMechanics`
--

DROP TABLE IF EXISTS `gameMechanics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gameMechanics` (
  `gameId` int(10) unsigned NOT NULL,
  `mechanic` varchar(256) NOT NULL,
  KEY `mechanic_game` (`gameId`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gamePublishers`
--

DROP TABLE IF EXISTS `gamePublishers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gamePublishers` (
  `gameId` int(10) unsigned NOT NULL,
  `publisherId` int(11) NOT NULL,
  KEY `gamePublishers_game` (`gameId`),
  KEY `gamePublishers_publisher` (`publisherId`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `games`
--

DROP TABLE IF EXISTS `games`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `games` (
  `bggid` int(10) unsigned NOT NULL,
  `name` varchar(256) NOT NULL DEFAULT '',
  `average` float DEFAULT '0',
  `rank` int(11) DEFAULT '-1',
  `yearPublished` int(11) DEFAULT '0',
  `minPlayers` int(10) unsigned DEFAULT '0',
  `maxPlayers` int(10) unsigned DEFAULT '0',
  `playTime` int(10) unsigned DEFAULT '0',
  `usersRated` int(10) unsigned DEFAULT '0',
  `usersTrading` int(10) unsigned DEFAULT '0',
  `usersWanting` int(10) unsigned DEFAULT '0',
  `usersWishing` int(10) unsigned DEFAULT '0',
  `averageWeight` float DEFAULT '0',
  `bayesAverage` float DEFAULT '0',
  `stdDev` float DEFAULT '0',
  `median` float DEFAULT '0',
  `numComments` int(10) unsigned DEFAULT '0',
  `expansion` int(10) unsigned NOT NULL DEFAULT '0',
  `thumbnail` varchar(256) DEFAULT '',
  `usersOwned` int(10) unsigned DEFAULT '0',
  `subdomain` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`bggid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `geekgames`
--

DROP TABLE IF EXISTS `geekgames`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `geekgames` (
  `geek` varchar(128) NOT NULL DEFAULT '',
  `game` int(10) unsigned NOT NULL DEFAULT '0',
  `rating` float NOT NULL DEFAULT '0',
  `owned` tinyint(1) DEFAULT '0',
  `want` tinyint(1) DEFAULT '0',
  `wish` int(10) unsigned DEFAULT '0',
  `trade` tinyint(1) DEFAULT '0',
  `comment` varchar(1024) DEFAULT NULL,
  `plays` int(10) unsigned DEFAULT NULL,
  `prevowned` tinyint(1) DEFAULT '0',
  `wanttobuy` tinyint(1) NOT NULL DEFAULT '0',
  `wanttoplay` tinyint(1) NOT NULL DEFAULT '0',
  `preordered` tinyint(1) NOT NULL DEFAULT '0',
  KEY `geekgame_game` (`game`),
  KEY `geekgame_geek` (`geek`),
  KEY `geek` (`geek`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `geekgametags`
--

DROP TABLE IF EXISTS `geekgametags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `geekgametags` (
  `geek` varchar(128) NOT NULL,
  `game` int(10) unsigned NOT NULL,
  `tag` varchar(128) NOT NULL,
  KEY `geekgametags_game` (`game`),
  KEY `geekgametags_geek` (`geek`),
  KEY `geek` (`geek`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `geeks`
--

DROP TABLE IF EXISTS `geeks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `geeks` (
  `username` varchar(128) NOT NULL DEFAULT '',
  `shouldplay` int(10) unsigned NOT NULL DEFAULT '0',
  `avatar` varchar(256) DEFAULT '',
  PRIMARY KEY (`username`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `history`
--

DROP TABLE IF EXISTS `history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `history` (
  `geek` varchar(128) NOT NULL,
  `ts` datetime NOT NULL,
  `friendless` int(11) DEFAULT '-1000',
  `wanted` int(10) unsigned DEFAULT '0',
  `wished` int(10) unsigned DEFAULT '0',
  `owned` int(10) unsigned DEFAULT '0',
  `unplayed` int(10) unsigned DEFAULT '0',
  `distinctPlayed` int(10) unsigned DEFAULT '0',
  `traded` int(10) unsigned DEFAULT '0',
  `nickelPercent` float NOT NULL DEFAULT '0',
  `yourAverage` float NOT NULL DEFAULT '0',
  `percentPlayedEver` float NOT NULL DEFAULT '0',
  `percentPlayedThisYear` float NOT NULL DEFAULT '0',
  `averagePogo` float NOT NULL DEFAULT '0',
  `bggAverage` float NOT NULL DEFAULT '0',
  `curmudgeon` float NOT NULL DEFAULT '0',
  `meanYear` float NOT NULL DEFAULT '0',
  `the100` int(10) unsigned DEFAULT '0',
  `sdj` int(10) unsigned DEFAULT '0',
  `top50` int(10) unsigned DEFAULT '0',
  `totalPlays` int(10) unsigned DEFAULT '0',
  `medYear` int(10) unsigned DEFAULT '0',
  KEY `history_geek` (`geek`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `market`
--

DROP TABLE IF EXISTS `market`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `market` (
  `geek` varchar(128) NOT NULL,
  `gameid` int(10) unsigned NOT NULL,
  `itemid` int(10) unsigned NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `metadata`
--

DROP TABLE IF EXISTS `metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metadata` (
  `ruletype` int(11) DEFAULT NULL,
  `bggid` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `monthsplayed`
--

DROP TABLE IF EXISTS `monthsplayed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monthsplayed` (
  `geek` varchar(128) NOT NULL,
  `month` int(10) unsigned NOT NULL,
  `year` int(10) unsigned NOT NULL,
  KEY `monthsplayed_geek` (`geek`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `numplayers`
--

DROP TABLE IF EXISTS `numplayers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `numplayers` (
  `game` int(10) unsigned NOT NULL DEFAULT '0',
  `best1` int(10) unsigned NOT NULL DEFAULT '0',
  `recommended1` int(10) unsigned NOT NULL DEFAULT '0',
  `notrec1` int(10) unsigned NOT NULL DEFAULT '0',
  `best2` int(10) unsigned NOT NULL DEFAULT '0',
  `recommended2` int(10) unsigned NOT NULL DEFAULT '0',
  `notrec2` int(10) unsigned NOT NULL DEFAULT '0',
  `best3` int(10) unsigned NOT NULL DEFAULT '0',
  `recommended3` int(10) unsigned NOT NULL DEFAULT '0',
  `notrec3` int(10) unsigned NOT NULL DEFAULT '0',
  `best4` int(10) unsigned NOT NULL DEFAULT '0',
  `recommended4` int(10) unsigned NOT NULL DEFAULT '0',
  `notrec4` int(10) unsigned NOT NULL DEFAULT '0',
  `best5` int(10) unsigned NOT NULL DEFAULT '0',
  `recommended5` int(10) unsigned NOT NULL DEFAULT '0',
  `notrec5` int(10) unsigned NOT NULL DEFAULT '0',
  `best6` int(10) unsigned NOT NULL DEFAULT '0',
  `best7` int(10) unsigned NOT NULL DEFAULT '0',
  `recommended6` int(10) unsigned NOT NULL DEFAULT '0',
  `recommended7` int(10) unsigned NOT NULL DEFAULT '0',
  `notrec6` int(10) unsigned NOT NULL DEFAULT '0',
  `notrec7` int(10) unsigned NOT NULL DEFAULT '0',
  KEY `numplayers_game` (`game`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opponents`
--

DROP TABLE IF EXISTS `opponents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `opponents` (
  `name` varchar(45) DEFAULT NULL,
  `username` varchar(128) DEFAULT NULL,
  `colour` varchar(45) DEFAULT NULL,
  `geek` varchar(128) NOT NULL,
  `month` int(11) NOT NULL,
  `year` int(11) NOT NULL,
  `count` int(11) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plays`
--

DROP TABLE IF EXISTS `plays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plays` (
  `game` int(10) unsigned NOT NULL DEFAULT '0',
  `geek` varchar(128) NOT NULL DEFAULT '',
  `playDate` date NOT NULL,
  `quantity` int(10) unsigned NOT NULL DEFAULT '1',
  `basegame` int(10) DEFAULT '0',
  `raters` int(11) DEFAULT '0',
  `ratingsTotal` int(11) DEFAULT '0',
  `location` varchar(256) DEFAULT NULL,
  KEY `plays_index` (`geek`,`playDate`),
  KEY `plays_games` (`geek`,`game`),
  KEY `plays_game` (`game`),
  KEY `plays_geek` (`geek`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `publishers`
--

DROP TABLE IF EXISTS `publishers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `publishers` (
  `name` varchar(254) NOT NULL DEFAULT '',
  `bggid` int(11) NOT NULL,
  `url` varchar(254) DEFAULT NULL,
  PRIMARY KEY (`bggid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `series`
--

DROP TABLE IF EXISTS `series`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `series` (
  `name` varchar(128) NOT NULL,
  `game` int(10) unsigned NOT NULL,
  KEY `series_game` (`game`),
  KEY `series_name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `geek` varchar(128) NOT NULL,
  `lastProfileView` timestamp NULL DEFAULT NULL,
  `profileViews` int(11) NOT NULL DEFAULT '0',
  `bggid` int(11) DEFAULT '0',
  `country` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`geek`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-06-13 18:37:33
