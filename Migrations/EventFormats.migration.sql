CREATE SEQUENCE EventFormats_EventFormatID_seq AS SMALLINT INCREMENT BY 1;
CREATE TABLE event_formats (
    event_format_id SMALLINT PRIMARY KEY DEFAULT nextval('EventFormats_EventFormatID_seq'),
    event_format_name VARCHAR(32) UNIQUE
);
INSERT INTO event_formats 
VALUES (DEFAULT, 'conventional'),
    (DEFAULT, 'sprint'),
    (DEFAULT, 'sprint_shootout'),
    (DEFAULT, 'sprint_qualifying'),
    (DEFAULT, 'testing');
