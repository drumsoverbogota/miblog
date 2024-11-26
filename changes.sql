ALTER TABLE `entradas_entrada` ADD `slug` VARCHAR(200) NOT NULL AFTER `id`; 
UPDATE `entradas_entrada`  SET `slug` = `id`;
ALTER TABLE `entradas_entrada` ADD UNIQUE (`slug`);


ALTER TABLE `entradas_diario` ADD `slug` VARCHAR(200) NOT NULL AFTER `id`; 
UPDATE `entradas_diario`  SET `slug` = `id`;
ALTER TABLE `entradas_diario` ADD UNIQUE (`slug`);
