# Image based on debian with python3
FROM python:3-onbuild

MAINTAINER Vitaliy Tsutsman <vitaliyacm@gmail.com>

# Install dependencies
RUN pip install python-redmine && \
    apt-get update && apt-get install -y cron && \
    pip install --upgrade git+https://github.com/coffeine-009/python-redmine.git@softjourn

# Share app sources
COPY . /usr/local/officeman
WORKDIR /usr/local/officeman

# Configuration of sheduler
# Add crontab file in the cron directory
ADD crontab /etc/cron.d/time-tracker-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/time-tracker-cron && \
    chmod +x /usr/local/officeman/time-tracker.py

# Create the log file to be able to run tail
RUN touch /var/log/office-man.log

# Trick to keep container running
EXPOSE 2222

# Run cron and tail of logs
ENTRYPOINT ["cron", "&&", "tail", "-f", "/var/log/office-man.log"]
