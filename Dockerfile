#preliminary stuff
FROM ubuntu:14.04
MAINTAINER Jay Atkinson <jgatkinsn@gmail.com>


#install basics
RUN apt-get update
RUN apt-get install -y python2.7
RUN apt-get install -y python-mysqldb
RUN apt-get install -y apache2
RUN apt-get install -y mysql-server
RUN apt-get install -y mysql-client
RUN apt-get install -y python-django
RUN apt-get install -y libapache2-mod-wsgi
RUN apt-get install -y python-imaging
RUN apt-get install -y supervisor
RUN apt-get install -y cron

ENV DBUSER root
ENV DBPASS ""

#install files
RUN mkdir /extended
ADD * /extended/
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

#setup database
RUN mysql -u root create database extended;
RUN mysql extended -u root < /extended/database_schema.sql 
#setup apache2
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ADD stats.conf /etc/apache2/conf-enabled/
#ADD /etc/apache/000-default.conf /etc/apache2/sites-available/000-default.conf
RUN a2enmod wsgi

#expose the basic web ports
EXPOSE 80 8080
#start supervisor which starts web & mysql
CMD["/usr/bin/supervisord"]
