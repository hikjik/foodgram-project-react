![Foodgram Workflow](https://github.com/hikjik/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Продуктовый помощник Foodgram

## Содержание

- [Продуктовый помощник Foodgram](#продуктовый-помощник-foodgram)
  - [Содержание](#содержание)
  - [Стек технологий](#стек-технологий)
  - [О проекте](#о-проекте)
  - [Структура проекта](#структура-проекта)
  - [Запуск проекта](#запуск-проекта)
  - [Примеры запросов к API](#примеры-запросов-к-api)
  - [Ссылки](#ссылки)

## Стек технологий

 - Django
 - Django REST Framework
 - PostgreSQL
 - Nginx
 - Gunicorn
 - Docker
 - Yandex.Cloud
 - React

## О проекте

Сервис Foodgram позволяет зарегистрированным пользователям публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

В зависимости от уровня доступа, пользователи сервиса Foodgram могут выполнять следующие действия:

- **Неавторизованные пользователи**

  - создать аккаунт;
  - просматривать рецепты на главной;
  - просматривать отдельные страницы рецептов;
  - просматривать страницы пользователей;
  - фильтровать рецепты по тегам.

- **Авторизованные пользователи**

  - входить в систему под своим логином и паролем;
  - выходить из системы;
  - менять свой пароль;
  - создавать/редактировать/удалять собственные рецепты;
  - просматривать рецепты на главной;
  - просматривать страницы пользователей;
  - просматривать отдельные страницы рецептов;
  - фильтровать рецепты по тегам;
  - работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов;
  - работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл со количеством необходимых ингридиентов для рецептов из списка покупок;
  - подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.

- **Администратор через панель Django**

  * изменять пароль любого пользователя;
  * создавать/блокировать/удалять аккаунты пользователей;
  * редактировать/удалять любые рецепты;
  * добавлять/удалять/редактировать ингредиенты;
  * добавлять/удалять/редактировать теги.

## Структура проекта

В репозитории проекта находятся следующие папки:
 - *frontend* — папка с файлами, необходимыми для сборки фронтенда сервиса;
 - *infra* — содержит конфигурационный файл nginx и docker-compose.yml для запуска сервиса;
 - *backend* — реализация бэкенда продуктового помощника;
 - *data* — содержит тестовые данные для загрузки в базу;
 - *docs*  — файлы спецификации API.

## Запуск проекта

Для запуска проекта на удаленном сервере необходимо выполнить следующие действия:

1. Установить docker и docker-compose согласно [инструкции](https://docs.docker.com/engine/install/).

2. Клонировать репозиторий и перейти в директорию развёртывания инфраструктуры:

```
git clone git@github.com:hikjik/foodgram-project-react.git
cd infra
```

3. Создать файл .env с настройками базы данных и django. Пример заполнения:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET_KEY=secret_key
```

4. Запустить контейнеры:

```
docker-compose up -d
```

5. Выполнить миграции, создать суперпользователя и собрать статику с помощью следующих команд:

```
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```

6. (Опционально) Загрузить резервную копию базы данных:

```
docker-compose run web python manage.py loaddata /data/db.json
docker-compose exec backend cp -r  /data/media/recipes /app/media
```

## Примеры запросов к API

1. Регистрация пользователя

```
POST https://foodgram.zapto.org/api/users/
```

Тело запроса:

```json
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "password": "Qwerty123"
}
```

Пример ответа:

```json
{
  "id": 0,
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин"
}
```

2. Получение токена

```
POST https://foodgram.zapto.org/api/auth/token/login/
```

Тело запроса:

```json
{
  "email": "vpupkin@yandex.ru",
  "password": "Qwerty123"
}
```

Пример ответа:

```json
{
  "auth_token": "string"
}
```

3. Список рецептов

```
GET https://foodgram.zapto.org/api/recipes/
```

Заголовок запроса может содержать токен:
```
{
    "Authorization" : "Token string"
}
```


Пример ответа:

```json
{
  "count": 123,
  "next": "https://foodgram.zapto.org/api/recipes/?page=4",
  "previous": "https://foodgram.zapto.org/api/recipes//?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "https://foodgram.zapto.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```

## Ссылки

- [Сервис Foodgram][1]
- [Спецификация API][2]
- [Административная панель Django][3]
- [Дизайн-проект в Figma][4]

[1]: https://foodgram.zapto.org/
[2]: https://foodgram.zapto.org/api/docs/
[3]: https://foodgram.zapto.org/admin/
[4]: https://www.figma.com/file/HHEJ68zF1bCa7Dx8ZsGxFh/Продуктовый-помощник-Final?node-id=0%3A
