#!/usr/bin/env bash

echo "start mysql server"
/usr/sbin/mysqld &
sleep 5

echo "create database"
mysql -u "$DBUSER" -e "CREATE DATABASE extended"
echo "import database"
mysql extended -u "$DBUSER" < /home/ubuntu/extended/database_schema.sql
echo "Reset root password"
mysqladmin -h localhost -u "$DBUSER" password "$DBPASS"
echo "shutdown mysql server"
#mysqladmin -h localhost shutdown
mysqladmin -h localhost -u "$DBUSER" --password="$DBPASS" shutdown

