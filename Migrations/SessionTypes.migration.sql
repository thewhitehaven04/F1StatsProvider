CREATE SEQUENCE SessionTypes_SessionTypeID_seq AS SMALLINT INCREMENT BY 1;
CREATE TABLE session_types (
    session_type_id SMALLINT PRIMARY KEY DEFAULT nextval('SessionTypes_SessionTypeID_seq'),
    session_name VARCHAR(32),
    session_display_name text
);
INSERT INTO session_types (session_name, session_display_name)
VALUES ('fp1', 'Practice 1'),
    ('fp2', 'Practice 2'),
    ('fp3', 'Practice 3'),
    ('qualifying', 'Qualifying'),
    ('sprint', 'Sprint'),
    (
        'sprint_qualifying',
        'Sprint Qualifying'
    ),
    ('sprint_shootout', 'Sprint Shootout'),
    ('race', 'Race');