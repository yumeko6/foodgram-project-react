## Проект Foodgram. Продуктовый помощник

[![Python](https://img.shields.io/badge/-Python_3.7.9-464646??style=flat-square&logo=Python)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/-Django-464646??style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django](https://img.shields.io/badge/-Django_rest_framework_3.12.4-464646??style=flat-square&logo=Django)](https://www.django-rest-framework.org)
[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/yumeko1/foodgram-backend?label=docker&logo=docker)](https://hub.docker.com/r/yumeko1/api_yamdb/tags)
![Yamdb CI](https://github.com/yumeko6/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

### Foodgram - сервис, где каждый может публиковать свои самые вкусные рецепты, подписываться на других авторов и добавлять рецепты в избранное и список покупок.

### Проверить работу можно по адресу http://51.250.29.115/



#### Подготовка и запуск проекта

##### Клонируйте репозиторий
`https://github.com/yumeko6/foodgram-project-react`

##### Создайте и активируйте виртуальное окружение
```python
python -m venv venv
source venv/Scripts/activate
```

##### Перейдите в папку infra
`cd infra/`

##### Запустите команду для сборки контейнеров
`docker-compose up -d`

##### Внутри контейнера web примените миграции, соберите статику, загрузите ингредиенты и создайте суперпользователя
```python
docker-compose exec web bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py load_ingredients
python manage.py createsuperuser
```
##### Теперь сайт доступен по адресу localhost
#### Дополнительно
##### Чтобы иметь возможность создавать свои рецепты, создайте необходимые вам теги для рецептов в админ-панели Django