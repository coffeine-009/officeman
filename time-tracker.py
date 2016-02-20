#!/usr/bin/python

import sys
from datetime import datetime
import logging
from redmine import Redmine


class TrackingSystem:
    """
    Tracking system base.
    """
    client = None
    log = None

    def __init__(self, client):
        """
        Constructor for creating a new tracking system.

        :param client: HTTP client for current system
        """
        self.client = client
        # Set logger
        self.log = logging.getLogger('Time-tracker')
        self.log.setLevel(logging.INFO)

        fh = logging.FileHandler('/var/log/office-man.log')
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

        self.log.addHandler(fh)

        self.log.info('--------------------------------------------------------------')


class RedmineSystem(TrackingSystem):
    """
    Implementation of tracking system for redmine
    """
    apiAccessKey = None

    def __init__(self, api_access_token):
        """
        Create a tracking system for redmine.

        :param api_access_token: API access token
        """
        TrackingSystem.__init__(self, Redmine('https://redmine.softjourn.if.ua', key=api_access_token))

    def check(self, project_id):
        """
        Check if user has vacation, day off, ....

        :param project_id: Id of project(vacation project)
        :return: 1 - user does not have any vacation, 0 - else.
        """
        self.log.info('Check if user has vacation.')
        # Get current user
        user = self.client.user.get('current')
        self.log.info('Current user(id: %s, name: %s)', user.id, user)
        # Get current date
        today = datetime.now().date()
        # Search vacations, days off, medicals, business trips
        issues = self.client.issue.filter(project_id=project_id, assigned_to_id=user.id, status_id='open')
        # Check if some issue is still open
        for issue in issues:
            if issue.start_date < today < issue.due_date:
                self.log.info('Current user has a vacation. Tracking is canceled.')
                return 0

        return 1

    def log_time(self, project_id, sub_project_id, hours):
        """
        Log time.

        :param project_id:      Id of issue or project for logging time
        :param sub_project_id:  Id of sub-project.
        :param hours:           Count of hours for logging.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        # self.client.time_entry.create(issue_id=project_id, project_sow_id=sub_project_id, spent_on=today, hours=hours, activity_id=2)
        self.log.info('Logged %s hour(s) for %s/%s at %s', hours, project_id, sub_project_id, today)


class Application:
    """
    Application entry point
    """
    system = None

    system_name = None
    api_key = None
    # Log params
    vacation_project_id = None
    project_id = None
    sub_project_id = None
    hours = None

    def __init__(self, params):
        """
        Create a new app.

        :param params: Command line args.
        """
        for param in params:
            key, value = param.split('=')

            if key == '--system':
                self.system_name = value

            if key == '--api-key':
                self.api_key = value

            if key == '--vacation-project-id':
                self.vacation_project_id = value

            if key == '--project-id':
                self.project_id = value

            if key == '--sub-project-id':
                self.sub_project_id = value

            if key == '--hours':
                self.hours = value

        if self.system_name == 'redmine':
            self.system = RedmineSystem(self.api_key)

    def run(self):
        """
        Run application.
        """
        if self.system.check(self.vacation_project_id):
            self.system.log_time(self.project_id, self.sub_project_id, self.hours)


# Start app
app = Application(sys.argv[1:])
app.run()
