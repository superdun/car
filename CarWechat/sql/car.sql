/*
Navicat MySQL Data Transfer

Source Server         : db
Source Server Version : 50718
Source Host           : 127.0.0.1:3306
Source Database       : car

Target Server Type    : MYSQL
Target Server Version : 50718
File Encoding         : 65001

Date: 2018-04-10 23:25:43
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `car`
-- ----------------------------
DROP TABLE IF EXISTS `car`;
CREATE TABLE `car` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `typeid` int(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `buy_at` datetime DEFAULT NULL,
  `gpsid` int(11) DEFAULT NULL,
  `img` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cargpsid` (`gpsid`),
  KEY `cartypeid` (`typeid`),
  CONSTRAINT `cargpsid` FOREIGN KEY (`gpsid`) REFERENCES `gps` (`id`),
  CONSTRAINT `cartypeid` FOREIGN KEY (`typeid`) REFERENCES `cartype` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of car
-- ----------------------------
INSERT INTO `car` VALUES ('1', '辽A66666', '1', '2018-03-03 19:06:41', '2018-03-01 19:06:43', '2', 'M5TAL/th.jpg');
INSERT INTO `car` VALUES ('3', '辽A88888', '2', '2018-03-03 19:06:41', '2018-03-01 19:06:43', '3', 'M5TAL/th.jpg');
INSERT INTO `car` VALUES ('4', '辽A88866', '1', '2018-03-16 19:44:57', '2018-03-16 19:44:59', '4', 'M5TAL/th.jpg');
INSERT INTO `car` VALUES ('5', '辽A66666', '2', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '6', '1XN15/th.jpg');
INSERT INTO `car` VALUES ('6', '辽A66666', '1', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '7', 'M5TAL/th.jp');
INSERT INTO `car` VALUES ('7', '辽A66666', '2', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '8', '1XN15/th.jpg');
INSERT INTO `car` VALUES ('8', '辽A66666', '1', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '9', '1XN15/th.jpg');
INSERT INTO `car` VALUES ('9', '辽A66666', '2', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '10', '1XN15/th.jpg');
INSERT INTO `car` VALUES ('10', '辽A66666', '1', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '13', '1XN15/th.jpg');
INSERT INTO `car` VALUES ('11', '辽A66666', '2', '2018-03-03 19:06:41', '2018-03-01 19:06:04', '12', '1XN15/th.jpg');

-- ----------------------------
-- Table structure for `cartype`
-- ----------------------------
DROP TABLE IF EXISTS `cartype`;
CREATE TABLE `cartype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `price` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `img` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of cartype
-- ----------------------------
INSERT INTO `cartype` VALUES ('1', '奔驰200', '200', '2018-03-23 22:44:48', 'BENZC200.jpg', 'pending');
INSERT INTO `cartype` VALUES ('2', '宝马7', '500', '2018-03-23 22:45:18', 'BWMX7.jpg', 'pending');

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
  `openid` varchar(100) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `driveage` int(20) DEFAULT NULL,
  `phone` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `phone` (`phone`) USING BTREE,
  UNIQUE KEY `idcode` (`idcode`),
  UNIQUE KEY `openid` (`openid`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of customer
-- ----------------------------
INSERT INTO `customer` VALUES ('20', '2018-03-24 20:35:40', null, null, null, null, 'oCmBowgviSDxO23e2v7xNLkn6mco.jpg', 'oCmBowgviSDxO23e2v7xNLkn6mco', null, null, null, 'normal');
INSERT INTO `customer` VALUES ('21', '2018-04-02 19:04:34', '李盾', '210124199111111111', null, null, 'oyNqL1g7OuQ7uqUI8LKDwJ-OFtWk.jpg', 'oyNqL1g7OuQ7uqUI8LKDwJ-OFtWk', '42dae262b8531b3df48cde9cc018c512', '50', '13061938526', 'normal');

-- ----------------------------
-- Table structure for `error`
-- ----------------------------
DROP TABLE IF EXISTS `error`;
CREATE TABLE `error` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `msg` varchar(2550) DEFAULT NULL,
  `type` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of error
-- ----------------------------
INSERT INTO `error` VALUES ('1', '2018-04-02 21:13:09', '{\"openid\": \"oyNqL1g7OuQ7uqUI8LKDwJ-OFtWk\", \"trade_type\": \"JSAPI\", \"cash_fee_type\": \"CNY\", \"nonce_str\": \"zXCieHLmGb4rI8STpdWklMJFKYsB0oVx\", \"time_end\": \"20180402211315\", \"err_code_des\": \"SUCCESS\", \"return_code\": \"SUCCESS\", \"mch_id\": \"1500651581\", \"settlement_total_fee\": 200, \"cash_fee\": 200, \"is_subscribe\": \"Y\", \"return_msg\": \"OK\", \"fee_type\": \"CNY\", \"bank_type\": \"CMC\", \"attach\": \"sandbox_attach\", \"device_info\": \"sandbox\", \"out_trade_no\": \"1500651581201804022113124325\", \"result_code\": \"SUCCESS\", \"total_fee\": 200, \"appid\": \"wxaa9d94255254a676\", \"transaction_id\": \"100539073720180402211315367019\", \"err_code\": \"SUCCESS\", \"sign\": \"6B103FDC499B252E055DD38F0EF3673D\"}', '1');
INSERT INTO `error` VALUES ('2', '2018-04-02 21:15:30', '{\"openid\": \"oyNqL1g7OuQ7uqUI8LKDwJ-OFtWk\", \"trade_type\": \"JSAPI\", \"cash_fee_type\": \"CNY\", \"nonce_str\": \"AL4qTOkPmaMjrudN0fyEbexvWVBiJgzD\", \"time_end\": \"20180402211538\", \"err_code_des\": \"SUCCESS\", \"return_code\": \"SUCCESS\", \"mch_id\": \"1500651581\", \"settlement_total_fee\": 200, \"cash_fee\": 200, \"is_subscribe\": \"Y\", \"return_msg\": \"OK\", \"fee_type\": \"CNY\", \"bank_type\": \"CMC\", \"attach\": \"sandbox_attach\", \"device_info\": \"sandbox\", \"out_trade_no\": \"1500651581201804022115344277\", \"result_code\": \"SUCCESS\", \"total_fee\": 200, \"appid\": \"wxaa9d94255254a676\", \"transaction_id\": \"100539073720180402211538101335\", \"err_code\": \"SUCCESS\", \"sign\": \"D17A3C25EE99D4BD89969A4950F2F551\"}', '1');
INSERT INTO `error` VALUES ('3', '2018-04-02 21:26:37', '{\"openid\": \"oyNqL1g7OuQ7uqUI8LKDwJ-OFtWk\", \"trade_type\": \"JSAPI\", \"cash_fee_type\": \"CNY\", \"nonce_str\": \"I2jgruKGnRDLEVMJC80QP9ldcZFAhvTz\", \"time_end\": \"20180402212646\", \"err_code_des\": \"SUCCESS\", \"return_code\": \"SUCCESS\", \"mch_id\": \"1500651581\", \"settlement_total_fee\": 200, \"cash_fee\": 200, \"is_subscribe\": \"Y\", \"return_msg\": \"OK\", \"fee_type\": \"CNY\", \"bank_type\": \"CMC\", \"attach\": \"sandbox_attach\", \"device_info\": \"sandbox\", \"out_trade_no\": \"1500651581201804022126413845\", \"result_code\": \"SUCCESS\", \"total_fee\": 200, \"appid\": \"wxaa9d94255254a676\", \"transaction_id\": \"100539073720180402212646812226\", \"err_code\": \"SUCCESS\", \"sign\": \"EA19A64ABC706C649E2D053FD9A1C6A3\"}', '1');
INSERT INTO `error` VALUES ('4', '2018-04-02 21:27:03', '{\"openid\": \"oyNqL1g7OuQ7uqUI8LKDwJ-OFtWk\", \"trade_type\": \"JSAPI\", \"cash_fee_type\": \"CNY\", \"nonce_str\": \"5a7DIxRdVumlsH9cfMh8QN1UGg4jZ0rv\", \"time_end\": \"20180402212729\", \"err_code_des\": \"SUCCESS\", \"return_code\": \"SUCCESS\", \"mch_id\": \"1500651581\", \"settlement_total_fee\": 200, \"cash_fee\": 200, \"is_subscribe\": \"Y\", \"return_msg\": \"OK\", \"fee_type\": \"CNY\", \"bank_type\": \"CMC\", \"attach\": \"sandbox_attach\", \"device_info\": \"sandbox\", \"out_trade_no\": \"1500651581201804022127264571\", \"result_code\": \"SUCCESS\", \"total_fee\": 200, \"appid\": \"wxaa9d94255254a676\", \"transaction_id\": \"100539073720180402212729758474\", \"err_code\": \"SUCCESS\", \"sign\": \"BBCA5AAE220D98C7194DB0289BAC2518\"}', '1');

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of history
-- ----------------------------

-- ----------------------------
-- Table structure for `loginrecord`
-- ----------------------------
DROP TABLE IF EXISTS `loginrecord`;
CREATE TABLE `loginrecord` (
  `detail` varchar(21485) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `userid` int(11) DEFAULT NULL,
  `ip` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `userrecordid` (`userid`),
  CONSTRAINT `userrecordid` FOREIGN KEY (`userid`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of loginrecord
-- ----------------------------
INSERT INTO `loginrecord` VALUES (null, '3', '2018-04-09 23:13:21', '3', '127.0.0.1');
INSERT INTO `loginrecord` VALUES (null, '4', '2018-04-09 23:13:21', '3', '127.0.0.1');

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
-- Table structure for `order`
-- ----------------------------
DROP TABLE IF EXISTS `order`;
CREATE TABLE `order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `carid` int(11) DEFAULT NULL,
  `tradetype` varchar(255) DEFAULT NULL,
  `totalfee` int(11) DEFAULT NULL,
  `customeropenid` varchar(255) DEFAULT NULL,
  `tradeno` varchar(255) DEFAULT NULL,
  `detail` varchar(2550) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `count` int(11) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `prepayid` varchar(255) DEFAULT NULL,
  `wxtradeno` varchar(255) DEFAULT NULL,
  `pay_at` varchar(255) DEFAULT NULL,
  `isrefund` int(11) DEFAULT NULL,
  `r_totalfee` int(11) DEFAULT NULL,
  `r_tradeno` varchar(255) DEFAULT NULL,
  `r_wxtradeno` varchar(255) DEFAULT NULL,
  `r_pay_at` varchar(255) DEFAULT NULL,
  `r_detail` varchar(2550) DEFAULT NULL,
  `userid` int(11) DEFAULT NULL,
  `fromdate` datetime DEFAULT NULL,
  `todate` datetime DEFAULT NULL,
  `offlinefee` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `caroderid` (`carid`),
  KEY `userorderid` (`customeropenid`),
  KEY `refundid` (`isrefund`),
  KEY `adminorderid` (`userid`),
  CONSTRAINT `adminorderid` FOREIGN KEY (`userid`) REFERENCES `user` (`id`),
  CONSTRAINT `caroderid` FOREIGN KEY (`carid`) REFERENCES `cartype` (`id`),
  CONSTRAINT `userorderid` FOREIGN KEY (`customeropenid`) REFERENCES `customer` (`openid`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of order
-- ----------------------------
INSERT INTO `order` VALUES ('1', '1', 'JSAPI', '1', 'oyNqL1g7OuQ7uqUI8LKDwJ-OFtWk', '1500651581201804052038594412', '{\"package\": \"prepay_id=wx05203859459526369230974c1922481338\", \"timeStamp\": \"1522931939\", \"signType\": \"MD5\", \"paySign\": \"4FFD898B649B96E5E3FA68220C7927E4\", \"appId\": \"wxaa9d94255254a676\", \"nonceStr\": \"1slKWwuN9EYJ5GXzF0ktQfpb6i3qrnDm\"}', '2018-04-05 20:38:53', '1', 'refunded', 'wx05203859459526369230974c1922481338', '4200000098201804052954108790', '20180405203903', '1', '1', '1500651581201804052041474392', '50000606392018040504042776757', '2018-04-05 20:41:54', '{\"appid\": \"wx684db814d4ca03c7\", \"cash_fee\": \"1\", \"mch_id\": \"1500651581\", \"nonce_str\": \"8JvQ3M8AQDKfv5L7\", \"out_refund_no_0\": \"1500651581201804052041474392\", \"out_trade_no\": \"1500651581201804052038594412\", \"refund_account_0\": \"REFUND_SOURCE_UNSETTLED_FUNDS\", \"refund_channel_0\": \"ORIGINAL\", \"refund_count\": \"1\", \"refund_fee\": \"1\", \"refund_fee_0\": \"1\", \"refund_id_0\": \"50000606392018040504042776757\", \"refund_recv_accout_0\": \"\\u652f\\u4ed8\\u7528\\u6237\\u7684\\u96f6\\u94b1\", \"refund_status_0\": \"SUCCESS\", \"refund_success_time_0\": \"2018-04-05 20:41:54\", \"result_code\": \"SUCCESS\", \"return_code\": \"SUCCESS\", \"return_msg\": \"OK\", \"sign\": \"50152CB740898A5067BF1A67C993F1DE\", \"total_fee\": \"1\", \"transaction_id\": \"4200000098201804052954108790\"}', null, null, null, null);
INSERT INTO `order` VALUES ('57', '1', 'JSAPI', '1', 'oyNqL1g7OuQ7uqUI8LKDwJ-OFtWk', '1500651581201804031924263254', '{\"package\": \"prepay_id=wx03192426977010123e396a9c1089216227\", \"timeStamp\": \"1522754667\", \"signType\": \"MD5\", \"paySign\": \"3ADB58ECE2263CF1CF1A21B0377A3F14\", \"appId\": \"wxaa9d94255254a676\", \"nonceStr\": \"3QG5AVSPikEbmlaoUM6qNfyXpu19Zr4v\"}', '2018-04-03 01:15:15', '1', 'ok', 'wx03192426977010123e396a9c1089216227', '4200000083201804031554688421', '20180403192435', null, null, null, null, null, null, null, null, null, null);
INSERT INTO `order` VALUES ('58', '1', 'JSAPI', '200', 'oCmBowgviSDxO23e2v7xNLkn6mco', '1500651581201804032145077181', '{\"package\": \"prepay_id=wx20180403214510346000\", \"timeStamp\": \"1522763110\", \"signType\": \"MD5\", \"paySign\": \"719A3891EDB86E33F1803FB669B5B538\", \"appId\": \"wx684db814d4ca03c7\", \"nonceStr\": \"qFtfkOXT7gejyczhUJ48V9Yp1rDEab0n\"}', '2018-04-03 21:45:04', '1', 'ok', 'wx20180403214510346000', '100539073720180403214512579206', '20180403214512', null, null, null, null, null, null, null, null, null, null);
INSERT INTO `order` VALUES ('59', '1', 'JSAPI', '200', 'oCmBowgviSDxO23e2v7xNLkn6mco', '1500651581201804032146254645', '{\"package\": \"prepay_id=wx20180403214625266417\", \"timeStamp\": \"1522763185\", \"signType\": \"MD5\", \"paySign\": \"59C3345FD8B1AF1E43A1E03F87521355\", \"appId\": \"wx684db814d4ca03c7\", \"nonceStr\": \"kogYtcSxeb1qUNBR6PTVClwO7zmrQZ0s\"}', '2018-04-03 21:46:21', '1', 'ok', 'wx20180403214625266417', '100539073720180403214627343129', '20180403214627', null, null, null, null, null, null, null, null, null, null);
INSERT INTO `order` VALUES ('60', '1', 'JSAPI', '200', 'oCmBowgviSDxO23e2v7xNLkn6mco', '1500651581201804032146483190', '{\"package\": \"prepay_id=wx20180403214649915039\", \"timeStamp\": \"1522763209\", \"signType\": \"MD5\", \"paySign\": \"7410A61CBF2FF05EA7BE094A45A0D4A8\", \"appId\": \"wx684db814d4ca03c7\", \"nonceStr\": \"RQ1CktlOLgSBUGP0E5rsAfHhzN3D8vYc\"}', '2018-04-03 21:46:21', '1', 'refunding', 'wx20180403214649915039', '100539073720180403214651994734', '20180403214651', null, null, null, null, null, null, null, null, null, null);
INSERT INTO `order` VALUES ('61', '1', 'JSAPI', '200', 'oCmBowgviSDxO23e2v7xNLkn6mco', '1500651581201804032147293342', '{\"package\": \"prepay_id=wx20180403214730285194\", \"timeStamp\": \"1522763250\", \"signType\": \"MD5\", \"paySign\": \"5FFF449553529F0AAF1611C80E56DCDB\", \"appId\": \"wx684db814d4ca03c7\", \"nonceStr\": \"tVTPJBjAr6ifxEGD4Mz5a91FvkKyLmSh\"}', '2018-04-03 21:46:21', '1', 'ok', 'wx20180403214730285194', '100539073720180403214732976700', '20180403214732', null, null, null, null, null, null, null, null, null, null);
INSERT INTO `order` VALUES ('62', '1', 'JSAPI', '200', 'oCmBowgviSDxO23e2v7xNLkn6mco', '1500651581201804032148527200', '{\"nonce_str\": \"1wzFyRB5muqkn0L9fEvOJ8KVCiA4slHD\", \"return_code\": \"SUCCESS\", \"return_msg\": \"OK\", \"sign\": \"15D85195A83E1E99B610892A9DC4A30F\", \"mch_id\": \"1500651581\", \"err_code_des\": \"SUCCESS\", \"appid\": \"wx684db814d4ca03c7\", \"device_info\": \"sandbox\", \"result_code\": \"SUCCESS\", \"err_code\": \"SUCCESS\"}', '2018-04-03 21:46:21', '1', 'canceled', 'wx20180403214852399708', '100539073720180403214854453442', '20180403214854', null, null, null, null, null, null, null, null, null, null);
INSERT INTO `order` VALUES ('63', '1', 'JSAPI', '200', 'oCmBowgviSDxO23e2v7xNLkn6mco', '1500651581201804032151187476', '{\"package\": \"prepay_id=wx20180403215121560509\", \"timeStamp\": \"1522763481\", \"signType\": \"MD5\", \"paySign\": \"438460D8D17C2A8F19BDFA0031ED8AFA\", \"appId\": \"wx684db814d4ca03c7\", \"nonceStr\": \"oxHQTef1nbcJ9MD07mdtC26LUprskq5G\"}', '2018-04-03 21:51:07', '1', 'refunding', 'wx20180403215121560509', '100539073720180403215123857613', '20180403215123', null, null, null, null, null, null, null, null, null, null);
INSERT INTO `order` VALUES ('64', '1', 'offline', null, 'oyNqL1g7OuQ7uqUI8LKDwJ-OFtWk', null, null, '2018-04-10 21:02:00', null, 'pending', null, null, null, null, null, null, null, null, null, '3', '2018-04-12 21:02:00', '2018-04-10 21:02:00', '1');

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
  `roleid` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `roleuserid` (`roleid`),
  CONSTRAINT `roleuserid` FOREIGN KEY (`roleid`) REFERENCES `userrole` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES ('1', 'admin', '21232f297a57a5a743894a0e4a801fc3', '2018-03-03 19:05:44', '0', '1');
INSERT INTO `user` VALUES ('3', 'admin1', 'e00cf25ad42683b3df678c61f42c6bda', '2018-04-09 22:02:53', '0', '2');

-- ----------------------------
-- Table structure for `userrole`
-- ----------------------------
DROP TABLE IF EXISTS `userrole`;
CREATE TABLE `userrole` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `stage` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of userrole
-- ----------------------------
INSERT INTO `userrole` VALUES ('1', '超级管理员', '1');
INSERT INTO `userrole` VALUES ('2', '管理员', '2');
