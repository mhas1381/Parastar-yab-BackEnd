# Nurse Finder Backend

## Introduction

Nurse Finder is an online platform designed to help clients find professional nurses for their caregiving needs. This project includes user management, nurse profiles, service requests, and feedback systems.

## Features

- User authentication and authorization (clients, nurses, and admin)
- Nurse profile management
- Service request management
- Rating and feedback system
- Admin panel for managing users and requests

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

```Shell
git clone https://github.com/mhas1381/Parastar-yab-BackEnd
```

### 📋 Running project with docker ⛴

```Shell
docker compose up
```



### 🔧 Running project with virtual env

```Shell
pip install virtualenv
```
Windows setup:
```Shell
#creating the enviroment
python -m venv venv

#activating the enviroment
venv\Scripts\activate

#deactivating enviroment
deactivate
```
Linux and Mac setup:
```Shell
#creating the enviroment
python -m venv venv

#activating the enviroment
source venv/bin/activate

#deactivating enviroment
deactivate
```

then installing the requirements:

```Shell
pip install -r requirements.txt
```
### Running the Project
in order to run the project you need to use either ways below

default and development settings
```Shell
python manage.py runserver 
```

## 🛠️ Built With

* ![django](https://img.icons8.com/material-outlined/24/django.png) - Django framework
* ![nginx](https://img.icons8.com/color/48/nginx.png) - Nginx
* ![posgressql](https://img.icons8.com/color/48/postgreesql.png) - Posgres sql for database

## 📚 Tecknology Stack

- Setting up project with Docker (dockerfile/docker-compose)
- Setup Django Model for a Blog and AbstractBaseUser
- Implement Class Based Views
- Django RestFramework and Serializers (FBV)
- ClassBasedViews in RestFramework (views,generic,viewset)
- Api Documentation with swagger and redoc
- Authentication API (Token/JWT)
- Reformat and Lint (flake8,black)
- Django TestCase and PyTest
- Django CI with github actions
- Populate Database with Faker and Django Commands
- Cores Headers
- Get ready for deploy (gunicorn/nginx)
- Use postgres sql as a database
- Use Kaveh Negar send sms service

## 📐 Model Schema


