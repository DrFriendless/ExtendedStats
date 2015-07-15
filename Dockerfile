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
ENV DBPASS basilisk

#install files
RUN mkdir -p /home/ubuntu/extended
ADD * /home/ubuntu/extended/
RUN chmod -R 777 /home/ubuntu/extended
#setup supervisord
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

#setup database
RUN chmod +x /home/ubuntu/extended/setup_mysql.sh
RUN /home/ubuntu/extended/setup_mysql.sh

#setup apache2
RUN mkdir -p /var/lock/apache2
RUN mkdir -p /var/run/apache2
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ADD stats.conf /etc/apache2/conf-enabled/
RUN a2enmod wsgi

#add cronjob
ADD crons.conf /etc/cron.d/extended
RUN chmod 0644 /etc/cron.d/extended


#expose the basic web ports
EXPOSE 80 8080
#start supervisor which starts web & mysql
CMD ["/usr/bin/supervisord"]
