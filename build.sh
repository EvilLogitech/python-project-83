#!/usr/bin/env bash
make install && psql -a -d $DB_ACCESS -f database.sql
