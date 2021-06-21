SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for status
-- ----------------------------
-- DROP TABLE IF EXISTS `errorLink`;
CREATE TABLE If Not Exists `errorLink`  (
  `id` INT UNSIGNED AUTO_INCREMENT,
  `type` varchar(255) COMMENT '文献类型，用于区分专利patent和（期刊、博硕、成果）的链接获取',
  `code` varchar(255) COMMENT '学科分类',
  `Link` varchar(255) NOT NULL COMMENT '链接',
  `date` varchar(255) NOT NULL COMMENT '日期',
   PRIMARY KEY(`id`)
) ENGINE = InnoDB