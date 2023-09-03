DROP TABLE IF EXISTS urls CASCADE;
CREATE TABLE urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255) UNIQUE,
    created_at timestamp DEFAULT NOW()
);

DROP TABLE IF EXISTS url_checks; 
CREATE TABLE url_checks (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id bigint NOT NULL REFERENCES urls (id),
    status_code int NOT NULL,
    h1 text,
    title text,
    description text,
    created_at timestamp DEFAULT NOW()
);
