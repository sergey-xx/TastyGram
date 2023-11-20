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
- Frontend: React
- Backand: Django REST API

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone git@github.com:sergey-xx/foodgram-project-react.git
```

### Локальный запуск проекта:
- установить Docker,
- в корневой папке проекта выполнить:
```bash
docker compose up
```
Выполнить в консоли команду:
```bash
docker container exec foodgram-project-react-backend-1 python manage.py migrate
```
Для создания суперпользователя выполнить команду:
```bash
docker container exec -it  foodgram-project-react-backend-1 python manage.py createsuperuser --username admin --email admin@admin.ru
```
Для импорта базы ингредиентов выполнить команду:
```bash
docker container exec foodgram-project-react-backend-1 python manage.py import
```


- Фронт будет доступен по адресу: http://localhost:8021/
-  Админка: http://localhost:8021/admin/
-  API: http://localhost:8021/api/

### Отдельный запуск Backend:
- В папке /backend создать и активировать виртуальное окружение:

```bash
python3 -m venv env
```

```bash
source env/bin/activate
```

- Установить зависимости из файла requirements.txt:

```bash
python3 -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```
- Закомментировать postgres DB в settyngs.py, добавить дефолтную SQLite:
```python
      'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
- Выполнить миграции:

```bash
python3 manage.py migrate
```
- Запуск сервера:

```bash
python3 manage.py runserver
```
### Frontend и документация
- Находясь в директории infra, выполнить команду:

```bash
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
```bash
sudo docker compose -f docker-compose.production.yml up -d
```
Настройка внешнего Nginx для этого проекта:

```bash
sudo nano /etc/nginx/sites-enabled/default 
```

```
server {
  server_name 111.111.111.111; # IP-адрес вашего сервера
  listen 80;

  location / {
    proxy_set_header Host $http_host;
    proxy_set_header        X-Real-IP $remote_addr;
    proxy_set_header        X-Forwarded-Proto $scheme;
    proxy_pass http://localhost:8031;
  }
}
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
- github_username: sergey-xx
- fodmram_domain: https://tastygram.ddns.net
- dockerhub_username: sergeyxx
