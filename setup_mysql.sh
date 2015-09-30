#!/usr/bin/env bash
echo "import database"
mysql -h mysqldb -u "$DBUSER" -p"$DBPASS" extended < /home/ubuntu/extended/database_schema.sql

