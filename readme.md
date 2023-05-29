# APOLLO Task Managment System

Project for the course of Multimedia Design and Production at the University of Florence.

## Getting Started 🚀

1. Create a .env file in the root of the project with the following variables:

```
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB=taskmanager
POSTGRES_HOST=database
POSTGRES_PORT
SECRET_KEY
```
The ones not specified are up to you. The SECRET_KEY is the Django secret key.

2. Execute the command `docker-compose up` to start the project in development mode.
