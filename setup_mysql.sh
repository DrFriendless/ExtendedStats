#!/usr/bin/env bash

echo "Setting root password:"
mysqladmin -u $DBUSER password $DBPASS
mysql -u $DBUSER -p $DBPASS create database extended
mysql extended -u $DBUSER -p $DBPASS < /database/database_schema.sql

