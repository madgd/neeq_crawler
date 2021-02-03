-- create datebase if not exist.
-- if db not exist run cmd:
-- sqlite3 neeq_rules.db < neeq_rules.sql
CREATE TABLE neeq_rules(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   infoId INT,
   title CHAR(1000),
   fileExtension CHAR(50),
   fileUrl CHAR(1000),
   linkUrl CHAR(1000),
   htmlUrl CHAR(1000),
   publishDate CHAR(1000),
   filePath CHAR(1000),
   attachPath CHAR(1000),
   ruleType INT
);
CREATE UNIQUE INDEX infoIdIndex on neeq_rules(infoId);

-- type relation table
CREATE TABLE rule_types(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   ruleType INT,
   ruleName CHAR(255)
);
CREATE UNIQUE INDEX ruleTypeIndex on rule_types(ruleType);

-- insert type data
INSERT INTO rule_types (ruleType, ruleName) VALUES (105, '法律规则');
INSERT INTO rule_types (ruleType, ruleName) VALUES (106, '部门规章');
INSERT INTO rule_types (ruleType, ruleName) VALUES (115, '业务规则$$综合类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (116, '业务规则$$挂牌业务类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (117, '业务规则$$公司业务-信息披露类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (482, '业务规则$$公司业务-融资类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (484, '业务规则$$公司业务-并购重组类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (486, '业务规则$$公司业务-公司治理类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (488, '业务规则$$公司业务-其他类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (118, '业务规则$$交易监察类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (119, '业务规则$$机构业务类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (120, '业务规则$$投资者服务类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (490, '业务规则$$信息管理类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (121, '业务规则$$两网及退市公司');
INSERT INTO rule_types (ruleType, ruleName) VALUES (122, '业务规则$$登记结算类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (496, '业务规则$$已废止业务类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (492, '服务指南$$监管信息公开类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (494, '服务指南$$业务文件及协议模板类');
INSERT INTO rule_types (ruleType, ruleName) VALUES (268, '技术专区$$接口规范');
INSERT INTO rule_types (ruleType, ruleName) VALUES (269, '业务规则$$技术指引');
INSERT INTO rule_types (ruleType, ruleName) VALUES (270, '业务规则$$测试专区');
INSERT INTO rule_types (ruleType, ruleName) VALUES (1127, '公开征求意见');
INSERT INTO rule_types (ruleType, ruleName) VALUES (1131, '改革专区');