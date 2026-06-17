CREATE SCHEMA IF NOT EXISTS oulad;
USE oulad;

DROP TABLE IF EXISTS `assessments`;
CREATE TABLE `assessments` (
  `code_module` VARCHAR(5) NOT NULL,
  `code_presentation` VARCHAR(6) NOT NULL,
  `id_assessment` INT NOT NULL,
  `assessment_type` VARCHAR(15) NOT NULL,
  `date` SMALLINT NULL,
  `weight` SMALLINT NULL,
  PRIMARY KEY (`id_assessment`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `class_ordinal_info`;
CREATE TABLE `class_ordinal_info` (
  `info_ord_id` INT NOT NULL,
  `info_ord_group` VARCHAR(20) NOT NULL,
  `info_ord_label` VARCHAR(3) NOT NULL,
  `info_ord_value` SMALLINT NOT NULL,
  `info_ord_text` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`info_ord_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses` (
  `code_module` VARCHAR(5) NOT NULL,
  `code_presentation` VARCHAR(6) NOT NULL,
  `module_presentation_length` SMALLINT NOT NULL,
  PRIMARY KEY (`code_module`,`code_presentation`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `etl_view_assess_level`;
CREATE TABLE `etl_view_assess_level` (
  `sujeto_id` INT NOT NULL,
  `code_module` VARCHAR(15) NOT NULL,
  `code_presentation` VARCHAR(15) NOT NULL,
  `id_student` VARCHAR(15) NOT NULL,
  `id_assessment` INT NOT NULL,
  `assessment_type` VARCHAR(15) NOT NULL,
  `gender` VARCHAR(15) NULL,
  `region` VARCHAR(60) NULL,
  `highest_education` VARCHAR(60) NULL,
  `imd_band` VARCHAR(15) NULL,
  `age_band` VARCHAR(15) NULL,
  `num_of_prev_attempts` SMALLINT NULL,
  `studied_credits` SMALLINT NULL,
  `disability` VARCHAR(1) NULL,
  `final_result` VARCHAR(15) NULL,
  `date_registration` SMALLINT NULL,
  `date_unregistration` SMALLINT NULL,
  `date_submitted` SMALLINT NULL,
  `score` DECIMAL(6, 2) NULL,
  `n_days_dataplus` SMALLINT NULL,
  `n_days_dualpane` SMALLINT NULL,
  `n_days_externalquiz` SMALLINT NULL,
  `n_days_folder` SMALLINT NULL,
  `n_days_forumng` SMALLINT NULL,
  `n_days_glossary` SMALLINT NULL,
  `n_days_homepage` SMALLINT NULL,
  `n_days_htmlactivity` SMALLINT NULL,
  `n_days_oucollaborate` SMALLINT NULL,
  `n_days_oucontent` SMALLINT NULL,
  `n_days_ouelluminate` SMALLINT NULL,
  `n_days_ouwiki` SMALLINT NULL,
  `n_days_page` SMALLINT NULL,
  `n_days_questionnaire` SMALLINT NULL,
  `n_days_quiz` SMALLINT NULL,
  `n_days_repeatactivity` SMALLINT NULL,
  `n_days_resource` SMALLINT NULL,
  `n_days_sharedsubpage` SMALLINT NULL,
  `n_days_subpage` SMALLINT NULL,
  `n_days_url` SMALLINT NULL,
  `avg_sum_clicks_dataplus` FLOAT NULL,
  `avg_sum_clicks_dualpane` FLOAT NULL,
  `avg_sum_clicks_externalquiz` FLOAT NULL,
  `avg_sum_clicks_folder` FLOAT NULL,
  `avg_sum_clicks_forumng` FLOAT NULL,
  `avg_sum_clicks_glossary` FLOAT NULL,
  `avg_sum_clicks_homepage` FLOAT NULL,
  `avg_sum_clicks_htmlactivity` FLOAT NULL,
  `avg_sum_clicks_oucollaborate` FLOAT NULL,
  `avg_sum_clicks_oucontent` FLOAT NULL,
  `avg_sum_clicks_ouelluminate` FLOAT NULL,
  `avg_sum_clicks_ouwiki` FLOAT NULL,
  `avg_sum_clicks_page` FLOAT NULL,
  `avg_sum_clicks_questionnaire` FLOAT NULL,
  `avg_sum_clicks_quiz` FLOAT NULL,
  `avg_sum_clicks_repeatactivity` FLOAT NULL,
  `avg_sum_clicks_resource` FLOAT NULL,
  `avg_sum_clicks_sharedsubpage` FLOAT NULL,
  `avg_sum_clicks_subpage` FLOAT NULL,
  `avg_sum_clicks_url` FLOAT NULL,
  `total_n_days` SMALLINT NULL,
  `avg_total_sum_clicks` FLOAT NULL,
  PRIMARY KEY (`sujeto_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `etl_view_student_level`;
CREATE TABLE `etl_view_student_level` (
  `sujeto_id` INT NOT NULL,
  `code_module` VARCHAR(15) NOT NULL,
  `code_presentation` VARCHAR(15) NOT NULL,
  `id_student` VARCHAR(15) NOT NULL,
  `gender` VARCHAR(15) NULL,
  `region` VARCHAR(60) NULL,
  `highest_education` VARCHAR(60) NULL,
  `imd_band` VARCHAR(15) NULL,
  `age_band` VARCHAR(15) NULL,
  `num_of_prev_attempts` SMALLINT NULL,
  `studied_credits` SMALLINT NULL,
  `disability` VARCHAR(1) NULL,
  `final_result` VARCHAR(15) NULL,
  `date_registration` SMALLINT NULL,
  `date_unregistration` SMALLINT NULL,
  `n_days_dataplus` SMALLINT NULL,
  `n_days_dualpane` SMALLINT NULL,
  `n_days_externalquiz` SMALLINT NULL,
  `n_days_folder` SMALLINT NULL,
  `n_days_forumng` SMALLINT NULL,
  `n_days_glossary` SMALLINT NULL,
  `n_days_homepage` SMALLINT NULL,
  `n_days_htmlactivity` SMALLINT NULL,
  `n_days_oucollaborate` SMALLINT NULL,
  `n_days_oucontent` SMALLINT NULL,
  `n_days_ouelluminate` SMALLINT NULL,
  `n_days_ouwiki` SMALLINT NULL,
  `n_days_page` SMALLINT NULL,
  `n_days_questionnaire` SMALLINT NULL,
  `n_days_quiz` SMALLINT NULL,
  `n_days_repeatactivity` SMALLINT NULL,
  `n_days_resource` SMALLINT NULL,
  `n_days_sharedsubpage` SMALLINT NULL,
  `n_days_subpage` SMALLINT NULL,
  `n_days_url` SMALLINT NULL,
  `avg_sum_clicks_dataplus` FLOAT NULL,
  `avg_sum_clicks_dualpane` FLOAT NULL,
  `avg_sum_clicks_externalquiz` FLOAT NULL,
  `avg_sum_clicks_folder` FLOAT NULL,
  `avg_sum_clicks_forumng` FLOAT NULL,
  `avg_sum_clicks_glossary` FLOAT NULL,
  `avg_sum_clicks_homepage` FLOAT NULL,
  `avg_sum_clicks_htmlactivity` FLOAT NULL,
  `avg_sum_clicks_oucollaborate` FLOAT NULL,
  `avg_sum_clicks_oucontent` FLOAT NULL,
  `avg_sum_clicks_ouelluminate` FLOAT NULL,
  `avg_sum_clicks_ouwiki` FLOAT NULL,
  `avg_sum_clicks_page` FLOAT NULL,
  `avg_sum_clicks_questionnaire` FLOAT NULL,
  `avg_sum_clicks_quiz` FLOAT NULL,
  `avg_sum_clicks_repeatactivity` FLOAT NULL,
  `avg_sum_clicks_resource` FLOAT NULL,
  `avg_sum_clicks_sharedsubpage` FLOAT NULL,
  `avg_sum_clicks_subpage` FLOAT NULL,
  `avg_sum_clicks_url` FLOAT NULL,
  `total_n_days` SMALLINT NULL,
  `avg_total_sum_clicks` FLOAT NULL,
  PRIMARY KEY (`sujeto_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `studentAssessment`;
CREATE TABLE `studentAssessment` (
  `id_assessment` INT NOT NULL,
  `id_student` INT NOT NULL,
  `date_submitted` SMALLINT NULL,
  `is_banked` BOOLEAN NULL,
  `score` DECIMAL(6, 2) NULL,
  PRIMARY KEY (`id_assessment`,`id_student`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `studentInfo`;
CREATE TABLE `studentInfo` (
  `code_module` VARCHAR(5) NOT NULL,
  `code_presentation` VARCHAR(6) NOT NULL,
  `id_student` INT NOT NULL,
  `gender` VARCHAR(10) NULL,
  `region` VARCHAR(60) NOT NULL,
  `highest_education` VARCHAR(30) NULL,
  `imd_band` VARCHAR(10) NULL,
  `age_band` VARCHAR(10) NULL,
  `num_of_prev_attempts` SMALLINT NULL,
  `studied_credits` SMALLINT NULL,
  `disability` CHAR(1) NOT NULL,
  `final_result` VARCHAR(15) NULL,
  PRIMARY KEY (`code_module`,`code_presentation`,`id_student`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `StudentInfo_ordinal`;
CREATE TABLE `StudentInfo_ordinal` (
  `code_module` VARCHAR(5) NOT NULL,
  `code_presentation` VARCHAR(6) NOT NULL,
  `id_student` INT NOT NULL,
  `gender` VARCHAR(10) NULL,
  `region` VARCHAR(60) NOT NULL,
  `highest_education` VARCHAR(30) NULL,
  `imd_band` VARCHAR(10) NULL,
  `age_band` VARCHAR(10) NULL,
  `num_of_prev_attempts` SMALLINT NULL,
  `studied_credits` SMALLINT NULL,
  `disability` CHAR(1) NOT NULL,
  `final_result` VARCHAR(15) NULL,
  `ordinal_genero` INT NOT NULL,
  `ordinal_claseSocial` INT NOT NULL,
  `ordinal_edad` INT NOT NULL,
  `ordinal_disability` INT NOT NULL,
  `ordinal_finalResult` INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `studentRegistration`;
CREATE TABLE `studentRegistration` (
  `code_module` VARCHAR(5) NOT NULL,
  `code_presentation` VARCHAR(6) NOT NULL,
  `id_student` INT NOT NULL,
  `date_registration` SMALLINT NULL,
  `date_unregistration` SMALLINT NULL,
  PRIMARY KEY (`code_module`,`code_presentation`,`id_student`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `studentVle`;
CREATE TABLE `studentVle` (
  `code_module` VARCHAR(5) NOT NULL,
  `code_presentation` VARCHAR(6) NOT NULL,
  `id_student` INT NOT NULL,
  `id_site` INT NOT NULL,
  `date` SMALLINT NULL,
  `sum_click` SMALLINT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `vle`;
CREATE TABLE `vle` (
  `id_site` INT NOT NULL,
  `code_module` VARCHAR(5) NOT NULL,
  `code_presentation` VARCHAR(6) NOT NULL,
  `activity_type` VARCHAR(15) NOT NULL,
  `week_from` SMALLINT NULL,
  `week_to` SMALLINT NULL,
  PRIMARY KEY (`id_site`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `assessments` ADD CONSTRAINT `FK_assessments_courses_02` FOREIGN KEY (`code_module`,`code_presentation`) REFERENCES `courses` (`code_module`,`code_presentation`);
ALTER TABLE `assessments` ADD CONSTRAINT `FK_assessments_courses_02]
GO
ALTER TABLE [dbo].[studentAssessment]  WITH CHECK ADD  CONSTRAINT [FK_studentassessment_assessment_01` FOREIGN KEY (`id_assessment`) REFERENCES `assessments` (`id_assessment`);
ALTER TABLE `studentAssessment` ADD CONSTRAINT `FK_studentassessment_assessment_01]
GO
ALTER TABLE [dbo].[studentInfo]  WITH CHECK ADD  CONSTRAINT [FK_studentInfo_courses_03` FOREIGN KEY (`code_module`,`code_presentation`) REFERENCES `courses` (`code_module`,`code_presentation`);
ALTER TABLE `studentInfo` ADD CONSTRAINT `FK_studentInfo_courses_03]
GO
ALTER TABLE [dbo].[studentRegistration]  WITH CHECK ADD  CONSTRAINT [FK_studentRegistration_studentInfo_04` FOREIGN KEY (`code_module`,`code_presentation`,`id_student`) REFERENCES `studentInfo` (`code_module`,`code_presentation`,`id_student`);
ALTER TABLE `studentRegistration` ADD CONSTRAINT `FK_studentRegistration_studentInfo_04]
GO
ALTER TABLE [dbo].[studentVle]  WITH CHECK ADD  CONSTRAINT [FK_studentVle_studentInfo_05` FOREIGN KEY (`code_module`,`code_presentation`,`id_student`) REFERENCES `studentInfo` (`code_module`,`code_presentation`,`id_student`);
ALTER TABLE `studentVle` ADD CONSTRAINT `FK_studentVle_studentInfo_05]
GO
ALTER TABLE [dbo].[studentVle]  WITH CHECK ADD  CONSTRAINT [FK_studentVle_Vle` FOREIGN KEY (`id_site`) REFERENCES `vle` (`id_site`);