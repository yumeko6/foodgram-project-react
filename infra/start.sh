#!/usr/bin/env bash
docker-compose stop
docker container prune -f
docker volume prune -f
docker image prune -fa
docker build -t test ../backend
docker-compose up -d
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic
docker-compose exec web python manage.py load_ingredients