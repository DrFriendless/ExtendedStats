#!/usr/bin/env bash

/usr/sbin/mysqld &
sleep 5

mysql -u $DBUSER -e "CREATE DATABASE extended"
mysql extended -u $DBUSER < /home/ubuntu/extended/database_schema.sql
mysqladmin shutdown

