/*
Navicat MySQL Data Transfer

Source Server         : db
Source Server Version : 50718
Source Host           : 127.0.0.1:3306
Source Database       : car

Target Server Type    : MYSQL
Target Server Version : 50718
File Encoding         : 65001

Date: 2018-03-16 22:52:54
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `car`
-- ----------------------------
DROP TABLE IF EXISTS `car`;
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of car
-- ----------------------------
INSERT INTO `car` VALUES ('1', '辽A66666', '奔驰C200L', '2018-03-03 19:06:41', '2018-03-01 19:06:43', '2', 'M5TAL/th.jpg');
INSERT INTO `car` VALUES ('3', '辽A88888', '奔驰C200L', '2018-03-03 19:06:41', '2018-03-01 19:06:43', '3', 'M5TAL/th.jpg');
INSERT INTO `car` VALUES ('4', '辽A88866', '奔驰C200L', '2018-03-16 19:44:57', '2018-03-16 19:44:59', '4', 'M5TAL/th.jpg');
INSERT INTO `car` VALUES ('5', '辽A66666', '奔驰C200L', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '6', '1XN15/th.jpg');
INSERT INTO `car` VALUES ('6', '辽A66666', '奔驰C200L', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '7', 'M5TAL/th.jp');
INSERT INTO `car` VALUES ('7', '辽A66666', '奔驰C200L', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '8', '1XN15/th.jpg');
INSERT INTO `car` VALUES ('8', '辽A66666', '奔驰C200L', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '9', '1XN15/th.jpg');
INSERT INTO `car` VALUES ('9', '辽A66666', '奔驰C200L', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '10', '1XN15/th.jpg');
INSERT INTO `car` VALUES ('10', '辽A66666', '奔驰C200L', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '13', '1XN15/th.jpg');
INSERT INTO `car` VALUES ('11', '辽A66666', '奔驰C200L', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '12', '1XN15/th.jpg');

-- ----------------------------
-- Table structure for `customer`
-- ----------------------------
DROP TABLE IF EXISTS `customer`;
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

-- ----------------------------
-- Records of customer
-- ----------------------------
INSERT INTO `customer` VALUES ('1', '2018-03-03 19:04:03', '李狗蛋', '210124XXXX', '男', '老客户，驾龄九年', 'PKCGK/th.jpg');
INSERT INTO `customer` VALUES ('2', '2018-03-03 19:04:23', '王二', '12344444XXX', '男', '不靠谱', 'PKCGK/th_1.jpg');
INSERT INTO `customer` VALUES ('3', '2018-03-03 19:05:04', '李芳', '4412313XXXX', '女', '女司机！', 'PKCGK/th_2.jpg');

-- ----------------------------
-- Table structure for `gps`
-- ----------------------------
DROP TABLE IF EXISTS `gps`;
CREATE TABLE `gps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of gps
-- ----------------------------
INSERT INTO `gps` VALUES ('2', '868120185824940');
INSERT INTO `gps` VALUES ('3', '868120185825079');
INSERT INTO `gps` VALUES ('4', '868120185825087');
INSERT INTO `gps` VALUES ('5', '868120185831606');
INSERT INTO `gps` VALUES ('6', '868120185841985');
INSERT INTO `gps` VALUES ('7', '868120185852073');
INSERT INTO `gps` VALUES ('8', '868120185852172');
INSERT INTO `gps` VALUES ('9', '868120185836449');
INSERT INTO `gps` VALUES ('10', '868120185847065');
INSERT INTO `gps` VALUES ('11', '868120185847297');
INSERT INTO `gps` VALUES ('12', '868120185847578');
INSERT INTO `gps` VALUES ('13', '868120185848196');

-- ----------------------------
-- Table structure for `history`
-- ----------------------------
DROP TABLE IF EXISTS `history`;
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

-- ----------------------------
-- Records of history
-- ----------------------------
INSERT INTO `history` VALUES ('1', '1', '1', '2017-10-17 19:13:34.000000', '2018-03-03 19:13:38.000000', '正在进行', '租赁', '1000', '2018-03-03 19:13:58.000000');
INSERT INTO `history` VALUES ('2', '1', '1', '2016-07-12 19:14:52.000000', '2017-04-18 19:14:58.000000', '完成订单', '租赁', '1200', '2018-03-03 19:15:13.000000');
INSERT INTO `history` VALUES ('3', '3', '1', '2014-09-02 19:15:51.000000', '2015-11-19 19:15:58.000000', '完成订单', '租赁', '500', '2018-03-03 19:16:18.000000');

-- ----------------------------
-- Table structure for `mendhistory`
-- ----------------------------
DROP TABLE IF EXISTS `mendhistory`;
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

-- ----------------------------
-- Records of mendhistory
-- ----------------------------
INSERT INTO `mendhistory` VALUES ('1', '1', '1', '正在进行', '大修', '1000', '2018-03-03 19:13:58.000000');
INSERT INTO `mendhistory` VALUES ('2', '1', '1', '完成订单', '保养', '1200', '2018-03-03 19:15:13.000000');
INSERT INTO `mendhistory` VALUES ('3', '1', '1', '完成订单', '小修', '500', '2018-03-03 19:16:18.000000');

-- ----------------------------
-- Table structure for `user`
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `auth` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES ('1', 'admin', '21232f297a57a5a743894a0e4a801fc3', '2018-03-03 19:05:44', '0');
