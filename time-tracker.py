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

    def __init__(self, url, api_access_token):
        """
        Create a tracking system for redmine.

        :param api_access_token: API access token
        """
        TrackingSystem.__init__(self, Redmine(url, key=api_access_token))

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

    def log_time(self, project_id, project_sow_id, hours, role_id):
        """
        Log time.

        :param project_id:      Id of issue or project for logging time
        :param project_sow_id:  Id of project sow
        :param hours:           Count of hours for logging
        :param role_id:         Role id for logging
        """
        today = datetime.now().strftime("%Y-%m-%d")
        self.client.time_entry.create(project_id=project_id, project_sow_id=project_sow_id, spent_on=today, hours=hours, activity_id=2, role_id=role_id)
        self.log.info('Logged %s hour(s) for %s at %s. RoleId: %s', hours, project_id, today, role_id)


class Application:
    """
    Application entry point
    """
    system = None

    url = None
    system_name = None
    api_key = None
    # Log params
    vacation_project_id = None
    project_id = None
    project_sow_id = None
    hours = None
    role_id = None

    def __init__(self, params):
        """
        Create a new app.

        :param params: Command line args.
        """
        for param in params:
            key, value = param.split('=')

            if key == '--url':
                self.url = value

            if key == '--system':
                self.system_name = value

            if key == '--api-key':
                self.api_key = value

            if key == '--vacation-project-id':
                self.vacation_project_id = value

            if key == '--project-id':
                self.project_id = value

            if key == '--project-sow-id':
                self.project_sow_id = value

            if key == '--hours':
                self.hours = value

            if key == '--role_id':
                self.role_id = value

        if self.system_name == 'redmine':
            self.system = RedmineSystem(self.url, self.api_key)

    def run(self):
        """
        Run application.
        """
        if self.system.check(self.vacation_project_id):
            self.system.log_time(self.project_id, self.project_sow_id, self.hours, self.role_id)


# Start app
app = Application(sys.argv[1:])
app.run()
