Office-man
=========================================
Tools for automatization of office routine.

Getting started
-----------------------------------------
Update crontab file. 
Replace `{VACATION_PROJECT_ID}`, `{PROJECT_ID}`, `{SUB_PROJECT_ID}` and `{COUNT_OF_HOURS}`
with your params.

 * `{VACATION_PROJECT_ID}` Id of project where you track vacations. Used for check if user has vacation at the logging time.
 * `{PROJECT_ID}` Id of project for logging time.
 * `{SUB_PROJECT_ID}` Id of sub project for logging time.
 * `{COUNT_OF_HOURS}` Count of hours for tracking.

```bash
docker build --rm -t officeman .
docker run --restart=always -d officeman
```

Also you can check logs.
```bash
docker ps -a
docker exec -i -t {CONTAINER_ID} bash
tail -f /var/log/office-man.log
```

## License

### MIT License