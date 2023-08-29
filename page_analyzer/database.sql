DROP TABLE IF EXISTS urls CASCADE;
CREATE TABLE urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255) UNIQUE,
    created_at timestamp
);

DROP TABLE IF EXISTS checks; 
CREATE TABLE checks (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id bigint REFERENCES urls (id),
    responce_code int NOT NULL,
    h1 text,
    title text,
    description text,
    created_at timestamp
);