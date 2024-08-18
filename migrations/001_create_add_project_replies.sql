CREATE TABLE "Add_project_replies" (
    id              serial  PRIMARY KEY,
    language        varchar NOT NULL,
    project_name    varchar NOT NULL,
    message         varchar NOT NULL
);
