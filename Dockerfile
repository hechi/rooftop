# This is a comment
FROM ubuntu:16.04
MAINTAINER Andreas Hechenberger <world@greenstation.de>

# Manually set up the apache environment variables
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid

RUN apt-get update && apt-get install -y \
	apache2 \
	libapache2-mod-wsgi-py3 \
	python3-dev \
	python3-pip \
	ldap-utils \
	libldap2-dev \
	libsasl2-dev

#create and copy files for rooftop
RUN mkdir -p /var/opt && cd /var/opt/
COPY ./ /var/opt/rooftop/

#configure apache
RUN cp /var/opt/rooftop/apache2_rooftop.conf /etc/apache2/sites-available/
RUN cd /etc/apache2/sites-enabled &&  ln -s /etc/apache2/sites-available/apache2_rooftop.conf apache2_rooftop.conf
RUN rm /etc/apache2/sites-enabled/000-default.conf

#install python libs and initial sqlite database
RUN cd /var/opt/rooftop/ && pip3 install -r requirements.txt && python3 manage.py migrate

#set permissions
RUN chown www-data:www-data -R /var/opt/rooftop/

# Expose web 
EXPOSE 80

CMD ["/usr/sbin/apache2", "-D", "FOREGROUND"]
