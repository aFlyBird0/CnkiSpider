/*
 Navicat Premium Data Transfer

 Source Server         : 实验室142
 Source Server Type    : MySQL
 Source Server Version : 50716
 Source Host           : 10.1.13.142:3306
 Source Schema         : ZhiWangSpider

 Target Server Type    : MySQL
 Target Server Version : 50716
 File Encoding         : 65001

 Date: 12/04/2021 14:51:58
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for status
-- ----------------------------
DROP TABLE IF EXISTS `status`;
CREATE TABLE `status`  (
  -- `id` INT UNSIGNED AUTO_INCREMENT,
  `type` varchar(255) COMMENT '爬虫类型，用于区分专利patent和（期刊、博硕、成果）paperAndAch的链接获取',
  `curCode` varchar(255) COMMENT '目前正在爬（链接获取）的学科分类',
  `curDate` varchar(255) NOT NULL COMMENT '目前正在爬（链接获取）的日期',
  `endDate` varchar(255) NOT NULL COMMENT '终止日期（包含）',
  `status` varchar(255) COMMENT '爬虫状态',
   PRIMARY KEY(`type`)
) ENGINE = InnoDB
