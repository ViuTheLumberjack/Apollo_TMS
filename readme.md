# APOLLO Task Managment System

Project for the course of Multimedia Design and Production at the University of Florence.

## Built with 🛠️

* [Django](https://www.djangoproject.com/) - The web framework used
* [Django REST Framework](https://www.django-rest-framework.org/) - The REST framework used

## Getting Started 🚀

0. Create a postgres database with the name `taskmanager`.
1. Create a .env file in the root of the project, as specified in the next section, with the following variables:

```
DEBUG = True
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB=taskmanager
POSTGRES_HOST=database
POSTGRES_PORT
SECRET_KEY
ALLOWED_HOSTS=*
```
The ones not specified are up to you. The SECRET_KEY is the Django secret key. The host is the name of the database service in the docker-compose file.

2. Execute the command `docker-compose up` to start the project in development mode.

## Structure 📁

The project is structured in the following way:

```
.
├── apollo_tms
│   ├── apollo_account
│   ├── apollo_tms
│   ├── dockerfile
│   ├── manage.py
│   ├── notifications
│   ├── requirements.txt
│   └── tasks
├── docker-compose.yml
├── dockerfile.production
├── pyvenv.cfg
├── readme.md
├── .env
└── taskmanagment

```

The `apollo_tms` folder contains the Django project. The `apollo_account` folder contains the app for the account management. The `apollo_tms` folder contains the settings for the project. The `tasks` folder contains the app for the task managment. The `notifications` folder contains the app for the notifications management.

The `taskmanagment` folder can be ignored because is just an empty Vue project created to complete the stack in the `docker-compose.yml` file.

## Deployment 📦

The project has been deployed on Railway.
The API Documentation can be accessed at [ApolloTMS/Swagger](https://apollotms-production.up.railway.app/swagger/).
You can also find the Redoc Documentation under [ApolloTMS/Redoc](https://apollotms-production.up.railway.app/redoc/).

## Documentation 📖

The documentation is available at [Documentation](https://apollotms-production.up.railway.app/swagger).
To set a token, perform a registration and a login, then copy the token received as response and click on the `Authorize` button on the top right corner of the page. Paste the token in the `Value` field as `Token {{key}}`. Now you can access the API.

## Authors ✒️

* Silviu Leonard Vatamanelu - [ViuTheLumberjack](https://www.github.com/ViuTheLumberjack)
