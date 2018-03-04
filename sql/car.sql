CREATE DATABASE  IF NOT EXISTS `car` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `car`;
-- MySQL dump 10.13  Distrib 5.7.17, for Win64 (x86_64)
--
-- Host: localhost    Database: car
-- ------------------------------------------------------
-- Server version	5.7.18-log

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
-- Table structure for table `car`
--

DROP TABLE IF EXISTS `car`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `car` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `buy_at` datetime DEFAULT NULL,
  `gpsid` int(11) DEFAULT NULL,
  `img` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cargpsid` (`gpsid`),
  CONSTRAINT `cargpsid` FOREIGN KEY (`gpsid`) REFERENCES `gps` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `car`
--

LOCK TABLES `car` WRITE;
/*!40000 ALTER TABLE `car` DISABLE KEYS */;
INSERT INTO `car` VALUES (1,'辽A66666','奔驰C200L','2018-03-03 19:06:41','2018-03-01 19:06:43',1,'http://img1.gtimg.com/auto/pics/hv1/160/174/1775/115463905.jpg');
/*!40000 ALTER TABLE `car` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `customer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `name` varchar(20) DEFAULT NULL,
  `idcode` varchar(20) DEFAULT NULL,
  `gender` varchar(20) DEFAULT NULL,
  `comment` varchar(1000) DEFAULT NULL,
  `img` varchar(2000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` VALUES (1,'2018-03-03 19:04:03','李狗蛋','210124XXXX','男','老客户，驾龄九年','https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1520179369967&di=f4b5ac3d676be9d940f96fdbe3dde346&imgtype=0&src=http%3A%2F%2Fimgbdb2.bendibao.com%2Fxiuxian%2F20135%2F24%2F201352413328746.jpg'),(2,'2018-03-03 19:04:23','王二','12344444XXX','男','不靠谱','https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1520774125&di=6f085f422187a460be1c17ff0f97d45f&imgtype=jpg&er=1&src=http%3A%2F%2Fimg.ifeng.com%2Fres%2F200808%2F0812_432435.jpg'),(3,'2018-03-03 19:05:04','李芳','4412313XXXX','女','女司机！','https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1520179439823&di=4697c73b9f9cb89bfefad005e563cdd1&imgtype=0&src=http%3A%2F%2Fimg.soufun.com%2Fnews%2F2010_07%2F16%2Foffice%2F1279265410839_000.jpg');
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gps`
--

DROP TABLE IF EXISTS `gps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gps`
--

LOCK TABLES `gps` WRITE;
/*!40000 ALTER TABLE `gps` DISABLE KEYS */;
INSERT INTO `gps` VALUES (1,'868120142603114');
/*!40000 ALTER TABLE `gps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `history`
--

DROP TABLE IF EXISTS `history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `customerid` int(11) DEFAULT NULL,
  `carid` int(11) DEFAULT NULL,
  `started_at` datetime(6) DEFAULT NULL,
  `ended_at` datetime(6) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `price` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `historycustomerid` (`customerid`),
  KEY `historycarid` (`carid`),
  CONSTRAINT `historycarid` FOREIGN KEY (`carid`) REFERENCES `car` (`id`),
  CONSTRAINT `historycustomerid` FOREIGN KEY (`customerid`) REFERENCES `customer` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `history`
--

LOCK TABLES `history` WRITE;
/*!40000 ALTER TABLE `history` DISABLE KEYS */;
INSERT INTO `history` VALUES (1,1,1,'2017-10-17 19:13:34.000000','2018-03-03 19:13:38.000000','正在进行','租赁','1000','2018-03-03 19:13:58.000000'),(2,1,1,'2016-07-12 19:14:52.000000','2017-04-18 19:14:58.000000','完成订单','租赁','1200','2018-03-03 19:15:13.000000'),(3,3,1,'2014-09-02 19:15:51.000000','2015-11-19 19:15:58.000000','完成订单','租赁','500','2018-03-03 19:16:18.000000');
/*!40000 ALTER TABLE `history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mendhistory`
--

DROP TABLE IF EXISTS `mendhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mendhistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userid` int(11) DEFAULT NULL,
  `carid` int(11) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `price` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `historycustomerid` (`userid`),
  KEY `historycarid` (`carid`),
  CONSTRAINT `mendhistory_ibfk_1` FOREIGN KEY (`carid`) REFERENCES `car` (`id`),
  CONSTRAINT `mendhistory_ibfk_2` FOREIGN KEY (`userid`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mendhistory`
--

LOCK TABLES `mendhistory` WRITE;
/*!40000 ALTER TABLE `mendhistory` DISABLE KEYS */;
INSERT INTO `mendhistory` VALUES (1,1,1,'正在进行','大修','1000','2018-03-03 19:13:58.000000'),(2,1,1,'完成订单','保养','1200','2018-03-03 19:15:13.000000'),(3,1,1,'完成订单','小修','500','2018-03-03 19:16:18.000000');
/*!40000 ALTER TABLE `mendhistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','admin','2018-03-03 19:05:44');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-03-04 23:42:48
