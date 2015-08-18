


DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
`id` int(11) NOT NULL ,
`name` varchar(80) NOT NULL,
PRIMARY KEY (`id`),
UNIQUE (`name`)
)  ;


DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
`id` int(11) NOT NULL ,
`group_id` int(11) NOT NULL,
`permission_id` int(11) NOT NULL,
PRIMARY KEY (`id`),
UNIQUE (`group_id`,`permission_id`),
CONSTRAINT `group_id_refs_id_f4b32aac` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
CONSTRAINT `permission_id_refs_id_6ba0f519` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
)  ;


DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
`id` int(11) NOT NULL ,
`name` varchar(50) NOT NULL,
`content_type_id` int(11) NOT NULL,
`codename` varchar(100) NOT NULL,
PRIMARY KEY (`id`),
UNIQUE (`content_type_id`,`codename`),
CONSTRAINT `content_type_id_refs_id_d043b34a` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
);

DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE `auth_user` (
`id` int(11) NOT NULL ,
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
UNIQUE (`username`)
)   ;


DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE `auth_user_groups` (
`id` int(11) NOT NULL ,
`user_id` int(11) NOT NULL,
`group_id` int(11) NOT NULL,
PRIMARY KEY (`id`),
UNIQUE (`user_id`,`group_id`),
CONSTRAINT `group_id_refs_id_274b862c` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
CONSTRAINT `user_id_refs_id_40c41112` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
)  ;


DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE `auth_user_user_permissions` (
`id` int(11) NOT NULL ,
`user_id` int(11) NOT NULL,
`permission_id` int(11) NOT NULL,
PRIMARY KEY (`id`),
UNIQUE (`user_id`,`permission_id`),
CONSTRAINT `permission_id_refs_id_35d9ac25` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
CONSTRAINT `user_id_refs_id_4dc23c39` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
)  ;


DROP TABLE IF EXISTS `collectiongames`;
CREATE TABLE `collectiongames` (
`groupindex` int(11) NOT NULL,
`bggid` int(11) NOT NULL,
`ckey` int(11) NOT NULL,
`orderindex` int(11) NOT NULL
)  ;


DROP TABLE IF EXISTS `collectiongroups`;
CREATE TABLE `collectiongroups` (
`groupindex` int(11) NOT NULL,
`groupname` varchar(128) DEFAULT NULL,
`groupdesc` varchar(512) DEFAULT NULL,
`display` tinyint(4) NOT NULL,
`ckey` int(11) NOT NULL
)  ;


DROP TABLE IF EXISTS `collections`;
CREATE TABLE `collections` (
`geek` varchar(128) NOT NULL,
`collectionname` varchar(256) DEFAULT NULL,
`description` varchar(512) DEFAULT NULL,
`collectionindex` int(11) NOT NULL,
`ckey` int(11) NOT NULL,
PRIMARY KEY (`ckey`)
)  ;


DROP TABLE IF EXISTS `designers`;
CREATE TABLE `designers` (
`name` varchar(254) NOT NULL DEFAULT '',
`bggid` int(11) NOT NULL,
`boring` tinyint(1) DEFAULT '0',
`url` varchar(254) DEFAULT NULL,
PRIMARY KEY (`bggid`)
)  ;


DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
`id` int(11) NOT NULL ,
`name` varchar(100) NOT NULL,
`app_label` varchar(100) NOT NULL,
`model` varchar(100) NOT NULL,
PRIMARY KEY (`id`),
UNIQUE (`app_label`,`model`)
);


DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
`session_key` varchar(40) NOT NULL,
`session_data` longtext NOT NULL,
`expire_date` datetime NOT NULL,
PRIMARY KEY (`session_key`)
)  ;


DROP TABLE IF EXISTS `django_site`;
CREATE TABLE `django_site` (
`id` int(11) NOT NULL ,
`domain` varchar(100) NOT NULL,
`name` varchar(50) NOT NULL,
PRIMARY KEY (`id`)
)   ;


DROP TABLE IF EXISTS `downloader`;
CREATE TABLE `downloader` (
`starttime` datetime NOT NULL,
`endtime` datetime NOT NULL,
`filesprocessed` int(11) NOT NULL,
`waittime` float NOT NULL,
`pausetime` float NOT NULL,
`failures` int(11) NOT NULL,
`users` int(11) NOT NULL,
`games` int(11) NOT NULL
)  ;


DROP TABLE IF EXISTS `expansions`;
CREATE TABLE `expansions` (
`basegame` int(10) NOT NULL,
`expansion` int(10) NOT NULL
)  ;


DROP TABLE IF EXISTS `files`;
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
UNIQUE  (`url`)
)  ;


DROP TABLE IF EXISTS `frontpagegeek`;
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
)  ;


DROP TABLE IF EXISTS `gameCategories`;
CREATE TABLE `gameCategories` (
`gameId` int(10) NOT NULL,
`category` varchar(256) NOT NULL
)  ;


DROP TABLE IF EXISTS `gameDesigners`;
CREATE TABLE `gameDesigners` (
`gameId` int(10) NOT NULL,
`designerId` int(11) NOT NULL
)  ;


DROP TABLE IF EXISTS `gameMechanics`;
CREATE TABLE `gameMechanics` (
`gameId` int(10) NOT NULL,
`mechanic` varchar(256) NOT NULL
)  ;


DROP TABLE IF EXISTS `gamePublishers`;
CREATE TABLE `gamePublishers` (
`gameId` int(10) NOT NULL,
`publisherId` int(11) NOT NULL
)  ;


DROP TABLE IF EXISTS `games`;
CREATE TABLE `games` (
`bggid` int(10) NOT NULL,
`name` varchar(256) NOT NULL DEFAULT '',
`average` float DEFAULT '0',
`rank` int(11) DEFAULT '-1',
`yearPublished` int(11) DEFAULT '0',
`minPlayers` int(10) DEFAULT '0',
`maxPlayers` int(10) DEFAULT '0',
`playTime` int(10) DEFAULT '0',
`usersRated` int(10) DEFAULT '0',
`usersTrading` int(10) DEFAULT '0',
`usersWanting` int(10) DEFAULT '0',
`usersWishing` int(10) DEFAULT '0',
`averageWeight` float DEFAULT '0',
`bayesAverage` float DEFAULT '0',
`stdDev` float DEFAULT '0',
`median` float DEFAULT '0',
`numComments` int(10) DEFAULT '0',
`expansion` int(10) NOT NULL DEFAULT '0',
`thumbnail` varchar(256) DEFAULT '',
`usersOwned` int(10) DEFAULT '0',
`subdomain` varchar(45) DEFAULT NULL,
PRIMARY KEY (`bggid`)
)  ;


DROP TABLE IF EXISTS `geekgames`;
CREATE TABLE `geekgames` (
`geek` varchar(128) NOT NULL DEFAULT '',
`game` int(10) NOT NULL DEFAULT '0',
`rating` float NOT NULL DEFAULT '0',
`owned` tinyint(1) DEFAULT '0',
`want` tinyint(1) DEFAULT '0',
`wish` int(10) DEFAULT '0',
`trade` tinyint(1) DEFAULT '0',
`comment` varchar(1024) DEFAULT NULL,
`plays` int(10) DEFAULT NULL,
`prevowned` tinyint(1) DEFAULT '0',
`wanttobuy` tinyint(1) NOT NULL DEFAULT '0',
`wanttoplay` tinyint(1) NOT NULL DEFAULT '0',
`preordered` tinyint(1) NOT NULL DEFAULT '0'
)  ;


DROP TABLE IF EXISTS `geekgametags`;
CREATE TABLE `geekgametags` (
`geek` varchar(128) NOT NULL,
`game` int(10) NOT NULL,
`tag` varchar(128) NOT NULL
)  ;


DROP TABLE IF EXISTS `geeks`;
CREATE TABLE `geeks` (
`username` varchar(128) NOT NULL DEFAULT '',
`shouldplay` int(10) NOT NULL DEFAULT '0',
`avatar` varchar(256) DEFAULT '',
PRIMARY KEY (`username`)
)  ;


DROP TABLE IF EXISTS `history`;
CREATE TABLE `history` (
`geek` varchar(128) NOT NULL,
`ts` datetime NOT NULL,
`friendless` int(11) DEFAULT '-1000',
`wanted` int(10) DEFAULT '0',
`wished` int(10) DEFAULT '0',
`owned` int(10) DEFAULT '0',
`unplayed` int(10) DEFAULT '0',
`distinctPlayed` int(10) DEFAULT '0',
`traded` int(10) DEFAULT '0',
`nickelPercent` float NOT NULL DEFAULT '0',
`yourAverage` float NOT NULL DEFAULT '0',
`percentPlayedEver` float NOT NULL DEFAULT '0',
`percentPlayedThisYear` float NOT NULL DEFAULT '0',
`averagePogo` float NOT NULL DEFAULT '0',
`bggAverage` float NOT NULL DEFAULT '0',
`curmudgeon` float NOT NULL DEFAULT '0',
`meanYear` float NOT NULL DEFAULT '0',
`the100` int(10) DEFAULT '0',
`sdj` int(10) DEFAULT '0',
`top50` int(10) DEFAULT '0',
`totalPlays` int(10) DEFAULT '0',
`medYear` int(10) DEFAULT '0'
)  ;


DROP TABLE IF EXISTS `market`;
CREATE TABLE `market` (
`geek` varchar(128) NOT NULL,
`gameid` int(10) NOT NULL,
`itemid` int(10) NOT NULL
)  ;


DROP TABLE IF EXISTS `metadata`;
CREATE TABLE `metadata` (
`ruletype` int(11) DEFAULT NULL,
`bggid` int(11) DEFAULT NULL
)  ;


DROP TABLE IF EXISTS `monthsplayed`;
CREATE TABLE `monthsplayed` (
`geek` varchar(128) NOT NULL,
`month` int(10) NOT NULL,
`year` int(10) NOT NULL
)  ;


DROP TABLE IF EXISTS `numplayers`;
CREATE TABLE `numplayers` (
`game` int(10) NOT NULL DEFAULT '0',
`best1` int(10) NOT NULL DEFAULT '0',
`recommended1` int(10) NOT NULL DEFAULT '0',
`notrec1` int(10) NOT NULL DEFAULT '0',
`best2` int(10) NOT NULL DEFAULT '0',
`recommended2` int(10) NOT NULL DEFAULT '0',
`notrec2` int(10) NOT NULL DEFAULT '0',
`best3` int(10) NOT NULL DEFAULT '0',
`recommended3` int(10) NOT NULL DEFAULT '0',
`notrec3` int(10) NOT NULL DEFAULT '0',
`best4` int(10) NOT NULL DEFAULT '0',
`recommended4` int(10) NOT NULL DEFAULT '0',
`notrec4` int(10) NOT NULL DEFAULT '0',
`best5` int(10) NOT NULL DEFAULT '0',
`recommended5` int(10) NOT NULL DEFAULT '0',
`notrec5` int(10) NOT NULL DEFAULT '0',
`best6` int(10) NOT NULL DEFAULT '0',
`best7` int(10) NOT NULL DEFAULT '0',
`recommended6` int(10) NOT NULL DEFAULT '0',
`recommended7` int(10) NOT NULL DEFAULT '0',
`notrec6` int(10) NOT NULL DEFAULT '0',
`notrec7` int(10) NOT NULL DEFAULT '0'
)  ;


DROP TABLE IF EXISTS `opponents`;
CREATE TABLE `opponents` (
`name` varchar(45) DEFAULT NULL,
`username` varchar(128) DEFAULT NULL,
`colour` varchar(45) DEFAULT NULL,
`geek` varchar(128) NOT NULL,
`month` int(11) NOT NULL,
`year` int(11) NOT NULL,
`count` int(11) NOT NULL
)  ;


DROP TABLE IF EXISTS `plays`;
CREATE TABLE `plays` (
`game` int(10) NOT NULL DEFAULT '0',
`geek` varchar(128) NOT NULL DEFAULT '',
`playDate` date NOT NULL,
`quantity` int(10)  NOT NULL DEFAULT '1',
`basegame` int(10) DEFAULT '0',
`raters` int(11) DEFAULT '0',
`ratingsTotal` int(11) DEFAULT '0',
`location` varchar(256) DEFAULT NULL
)  ;


DROP TABLE IF EXISTS `publishers`;
CREATE TABLE `publishers` (
`name` varchar(254) NOT NULL DEFAULT '',
`bggid` int(11) NOT NULL,
`url` varchar(254) DEFAULT NULL,
PRIMARY KEY (`bggid`)
)  ;


DROP TABLE IF EXISTS `series`;
CREATE TABLE `series` (
`name` varchar(128) NOT NULL,
`game` int(10) NOT NULL
)  ;


DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
`geek` varchar(128) NOT NULL,
`lastProfileView` timestamp NULL DEFAULT NULL,
`profileViews` int(11) NOT NULL DEFAULT '0',
`bggid` int(11) DEFAULT '0',
`country` varchar(64) DEFAULT NULL,
PRIMARY KEY (`geek`)
)  ;

