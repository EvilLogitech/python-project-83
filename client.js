const { Client } = require('pg');

const pgclient = new Client({
    host: process.env.POSTGRES_HOST,
    port: process.env.POSTGRES_PORT,
    user: 'postgres',
    password: 'postgres',
    database: 'postgres'
});

pgclient.connect();

const table1 = 'CREATE TABLE urls (id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY, name varchar(255) UNIQUE, created_at timestamp DEFAULT NOW())'
const table2 = 'CREATE TABLE url_checks (id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY, url_id bigint NOT NULL REFERENCES urls (id), status_code int NOT NULL, h1 text, title text, description text, created_at timestamp DEFAULT NOW())'

pgclient.query(table1, (err, res) => {
    if (err) throw err
});

pgclient.query(table2, (err, res) => {
    if (err) throw err
});