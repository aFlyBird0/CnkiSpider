SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for status
-- ----------------------------
-- DROP TABLE IF EXISTS `status`;
CREATE TABLE If Not Exists `status`  (
  -- `id` INT UNSIGNED AUTO_INCREMENT,
  `type` varchar(255) COMMENT '爬虫类型，用于区分专利patent和（期刊、博硕、成果）paperAndAch的链接获取',
  `curCode` varchar(255) COMMENT '目前正在爬（链接获取）的学科分类',
  `curDate` varchar(255) NOT NULL COMMENT '目前正在爬（链接获取）的日期',
  `endDate` varchar(255) NOT NULL COMMENT '终止日期（包含）',
  `status` varchar(255) COMMENT '爬虫状态',
   PRIMARY KEY(`type`)
) ENGINE = InnoDB
