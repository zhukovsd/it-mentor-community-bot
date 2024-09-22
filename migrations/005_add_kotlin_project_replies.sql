INSERT INTO "Add_project_replies" (
    language, 
    project_name, 
    message
) 
VALUES ( 
    'kotlin', 
    'hangman', 
    (SELECT message FROM "Add_project_replies" WHERE language = 'java' AND project_name = 'hangman')
),
( 
    'kotlin', 
    'simulation', 
    (SELECT message FROM "Add_project_replies" WHERE language = 'java' AND project_name = 'simulation')
),
( 
    'kotlin', 
    'currency-exchange', 
    (SELECT message FROM "Add_project_replies" WHERE language = 'java' AND project_name = 'currency-exchange')
),
( 
    'kotlin', 
    'tennis-scoreboard', 
    (SELECT message FROM "Add_project_replies" WHERE language = 'java' AND project_name = 'tennis-scoreboard')
),
( 
    'kotlin', 
    'weather-viewer', 
    (SELECT message FROM "Add_project_replies" WHERE language = 'java' AND project_name = 'weather-viewer')
),
( 
    'kotlin', 
    'cloud-file-storage', 
    (SELECT message FROM "Add_project_replies" WHERE language = 'java' AND project_name = 'cloud-file-storage')
),
( 
    'kotlin', 
    'task-tracker', 
    (SELECT message FROM "Add_project_replies" WHERE language = 'java' AND project_name = 'task-tracker')
);
