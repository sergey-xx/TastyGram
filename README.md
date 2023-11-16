# Foodgram-docker

### Описание проекта:
Проект сайта для размещения рецептов.

### Возможности
- cоздавать рецепт;
- добавлять ингредиенты из БД;
- добавлять понравившиеся рецептыв Избранное;
- подписываться на Авторов;
- добавлять рецепты в Корзину;
- скачивать список ингредиентов, добавленных в корзину рецептов.

### Технологии
Frontend: React
Backand: Django REST API

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:sergey-xx/foodgram-project-react.git
```

### Локальный запуск проекта:
- установить Docker,
- в корневой папке проекта выполнить:
```
docker compose up
```
Выполнить в консоли команду:
```
docker container exec foodgram-project-react-backend-1 python manage.py migrate
```
Для создания суперпользователя выполнить команду:
```
docker container exec -it  foodgram-project-react-backend-1 python manage.py createsuperuser --username admin --email admin@admin.ru
```
Для импорта базы ингредиентов выполнить команду:
```
docker container exec foodgram-project-react-backend-1 python manage.py import
```


- Фронт будет доступен по адресу: http://localhost:8021/
-  Админка: http://localhost:8021/admin/
-  API: http://localhost:8021/api/

### Отдельный запуск Backend:
- Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

- Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
- Закомментировать postgres DB в settyngs.py, добавить дефолтную SQLite:
```
      'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
- Выполнить миграции:

```
python3 manage.py migrate
```
- Запуск сервера:

```
python3 manage.py runserver
```
### Frontend и документация
- Находясь в директории infra, выполнить команду:

```
docker compose up
```
После запуска контейнера nginx Фронт будет доступен по адресу: http://localhost
Документацию на API можно будет увидеть по адресу: http://localhost/api/docs/redoc.html

### Для запуска на сервере :

- Установить Docker
- Установить Веб-сервер: Nginx
- Создать файл .env (см. образец env.example)
- загрузить в ту же папку docker-compose.production.yml
- выполнить 
```
sudo docker compose -f docker-compose.production.yml up -d
```

## Проект при деплое на Git/master пушится в Docker-контейнеры и разворачивается на VPS.
### В состав проекта входят 4 контейнера:
- foodgram_gateway - Nginx Web-сервер.
- foodgram_backend - Gunicorn-сервер.
- postgres:13.10 - Сервер базы данных.
- foodgram_frontend - Сборщик статики Node.js.

## Для успешного выполнение Action на GitHub должны быть добавлены следующие переменные:
- DOCKER_USERNAME (имя пользователя DockerHub)
- DOCKER_PASSWORD (пароль DockerHub)
- HOST (IP VPS-сервера)
- USER (Имя пользователя VPS-сервера)
- SSH_KEY (Закрытый ключ VPS-сервера)
- SSH_PASSPHRASE (Пароль VPS-сервера)
- TELEGRAM_TOKEN (Токен Телеграм-канала для уведомлений)
- TELEGRAM_TO (ID пользователя Телеграм)

## Данные о деплое проекта:
- repo_owner: sergey-xx
- fodmram_domain: https://tastygram.ddns.net
- dockerhub_username: sergeyxx
