#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER authuser;
    CREATE DATABASE auth_users;
    GRANT ALL PRIVILEGES ON DATABASE auth_users TO authuser;
    CREATE USER productsuser;
    CREATE DATABASE flask_products;
    GRANT ALL PRIVILEGES ON DATABASE flask_products TO productsuser;
EOSQL