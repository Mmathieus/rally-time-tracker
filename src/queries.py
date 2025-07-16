main_table = """ DROP TABLE IF EXISTS timings; \
                 CREATE TABLE timings ( \
                    id SMALLSERIAL PRIMARY KEY, \
                    rally VARCHAR(20) NOT NULL, \
                    stage VARCHAR(25) NOT NULL, \
                    car VARCHAR(10), \
                    time INTERVAL NOT NULL, \
                    created TIMESTAMP DEFAULT NOW() \
                 ); """

history_table = """  DROP TABLE IF EXISTS timings_history; \
                     CREATE TABLE timings_history ( \
                        id SMALLINT PRIMARY KEY, \
                        rally VARCHAR(20) NOT NULL, \
                        stage VARCHAR(25) NOT NULL, \
                        car VARCHAR(10), \
                        time INTERVAL NOT NULL, \
                        created TIMESTAMP \
                     ); """


GET_RETRIEVE_MAIN = " SELECT rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time, created FROM timings "
GET_FORMAT_MAIN = " ORDER BY rally, stage, time DESC; "
GET_SPECIAL_RETRIEVE_MAIN = " SELECT rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time, created FROM timings WHERE rally = '{RALLY}' OR stage = '{STAGE}' "

INSERT_GET_CURRENT_RECORD_INFO_MAIN = """ SELECT ROW(COALESCE(id, NULL), COALESCE(TO_CHAR(time, 'FMMI:SS:MS'), NULL)) AS id_time FROM timings WHERE stage = '{STAGE}'; """
INSERT_INTO_MAIN_AND_HISTORY = """  BEGIN; \
                                    INSERT INTO timings(rally, stage, car, time) VALUES ('{RALLY}', '{STAGE}', '{CAR}', '{TIME}'::INTERVAL); \
                                    INSERT INTO timings_history SELECT * FROM timings WHERE stage = '{STAGE}' ORDER BY id DESC LIMIT 1 RETURNING id; \
                                    COMMIT; """

SPECIAL_RETRIEVE_MAIN = " SELECT * FROM timings ORDER BY id; "
SPECIAL_RETRIEVE_HISTORY = " SELECT * FROM timings_history ORDER BY id; "
SPECIAL_DELETE_CURRENT_RECORD_MAIN = " DELETE FROM timings WHERE id = {ID} RETURNING stage, time; "
SPECIAL_DELETE_CURRENT_RECORD_HISTORY = " DELETE FROM timings_history WHERE id = {ID} RETURNING stage, time; "

HISTORY_RETRIEVE_HISTORY_ALL = " SELECT rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time, created FROM timings_history " + GET_FORMAT_MAIN
HISTORY_RETRIEVE_HISTORY_SPECIFIC = """ \
    SELECT \
        rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time, \
        TO_CHAR(imprvmnt, '"-"MI:SS:MS') AS gain, \
        TO_CHAR(SUM(imprvmnt) OVER (PARTITION BY stage ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '"-"MI:SS:MS') AS total_gain, \
        created \
    FROM ( \
        SELECT \
            id, rally, stage, car, time, \
            LAG(time) OVER (PARTITION BY stage ORDER BY id) - time AS imprvmnt, \
            created FROM timings_history \
        WHERE stage = '{}') AS subquery \
    ORDER BY id; """

IMPORT_COMMAND = "\\copy {TABLE} FROM '{FILE}' DELIMITER ',' CSV; "

EXPORT_COMMAND = "\\copy {TABLE} TO '{FILE}'DELIMITER ',' CSV; "

SEQUENCE_UPDATE = " SELECT setval(pg_get_serial_sequence('timings', 'id'), (SELECT MAX(id) FROM timings)) + 1 AS next_id; "

SEQUENCE_VALUE = " SELECT COALESCE(MAX(id), 0) + 1 FROM timings; "

