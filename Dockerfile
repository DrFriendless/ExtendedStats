#preliminary stuff
FROM python:2.7
MAINTAINER Jay Atkinson <jgatkinsn@gmail.com>


#install basics
RUN apt-get update
RUN apt-get install python-mysqldb
RUN apt-get install apache2
RUN apt-get install mysql-server
RUN apt-get install mysql-client
RUN apt-get install python-django
RUN apt-get install libapache2-mod-wsqi
RUN apt-get install python-imaging
RUN pip install supervisord

ENV DBUSER
ENV DBPASS

#install files
RUN mkdir /database
ADD database_schema.sql /database
RUN mkdir /extended
ADD * /extended

#setup database
RUN mysql -u root -p bubba create database extended;
RUN mysql extended -u root -p bubba < /database/database_schema.sql 
#setup apache2
ADD stats.conf /etc/apache2/conf-enabled/
RUN service apache2 restart

#expose the basic web port
EXPOSE 80
