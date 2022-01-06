DROP PROCEDURE IF EXISTS PROC_DROP_CHECK_CONSTRAINT;
    DELIMITER $$
    CREATE PROCEDURE PROC_DROP_CHECK_CONSTRAINT(IN tableName VARCHAR(64), IN constraintName VARCHAR(64))
    BEGIN
        IF EXISTS(
            SELECT * FROM information_schema.table_constraints
            WHERE 
                table_schema    = DATABASE()     AND
                table_name      = tableName      AND
                constraint_name = constraintName AND
                constraint_type = 'CHECK')
        THEN
            SET @query = CONCAT('ALTER TABLE ', tableName, ' DROP CONSTRAINT ', constraintName, ';');
            PREPARE stmt FROM @query; 
            EXECUTE stmt; 
            DEALLOCATE PREPARE stmt; 
        END IF; 
    END$$
    DELIMITER ;