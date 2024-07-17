# Elevate-BE

This repo contains code base code for django.

## Features

- Custom User Module with Auth
- Unit Test Cases
- PostgreSQL
- Docker
- Ready to deploy configs
- Bitbucket pipelines

## Prerequisites

- Python 3.10
- Docker
- VScode

## How to use?

**To build docker image**

```bash
  docker-compose build
```

**To run app**

```bash
  docker-compose up
```

**To stop app**

```bash
  docker-compose down
```

**To create new app**

```bash
  docker-compose run --rm app sh -c "python manage.py startapp <app-name>"
```

**To migrate database schema**

```bash
  docker-compose run --rm app sh -c "python manage.py makemigrations"
  docker-compose run --rm app sh -c "python manage.py migrate"
```

**To create superuser**

```bash
  docker-compose run --rm app sh -c "python manage.py createsuperuser"
```

**To execute tests**

```bash
  docker-compose run --rm app sh -c "python manage.py test"
```

**To check linting**

```bash
  docker-compose run --rm app sh -c "flake8"
```

**To format code**

```bash
  docker-compose run --rm app sh -c "black ."
```

## Contributing

Contributions are always welcome!

- Create your Work Branch `git checkout -b dev/<task_name>`
- Commit your Changes `git commit -m '<What changes you've done>'`
- Push to the Branch `git push origin dev/<task_name>`
- Open a Pull Request

Please adhere to this project's `code of conduct`.
