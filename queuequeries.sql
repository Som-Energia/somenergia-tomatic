-- SQL proposals to implement the pbx interface


-- Definition
CREATE TABLE queue_member_table (
	uniqueid INT(10) UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	membername varchar(40),
	queue_name varchar(128),
	interface varchar(128),
	penalty INT(11),
	paused INT(11),
	UNIQUE KEY queue_interface (queue_name, interface)
);

-- setCurrentQueue([200,201])
BEGIN;
DELETE 
FROM `queue_member_table`
WHERE `queue_name` = 'callcenter_somenergia'
;
INSERT INTO `queue_member_table`
	(`membername`,`queue_name`,`interface`,`penalty`,`paused`)
VALUES
	('SIP/200@bustia_veu','callcenter_somenergia','SIP/200',NULL,0),
	('SIP/201@bustia_veu','callcenter_somenergia','SIP/201',NULL,0),
;
COMMIT;

-- add(202)
INSERT INTO `queue_member_table`
	(`membername`,`queue_name`,`interface`,`penalty`,`paused`)
VALUES
	('SIP/202@bustia_veu','callcenter_somenergia','SIP/202',NULL,0),
;

-- pause(200) / resume(200)
UPDATE `queue_member_table`
SET `paused` = 1 -- or 0 for RESUME
WHERE `interface` = "SIP/200"
AND `queue_name` = 'callcenter_somenergia'
;

-- currentQueue()
SELECT `interface`, `paused`
FROM `queue_member_table`
WHERE `queue_name` = 'callcenter_somenergia'
;

