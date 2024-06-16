# ML_Service
Сервис детектирования и классификации сварных швов

## Запуск сервиса
### На локальной машине

Скачать код из репозитория:

```bash
$ git clone https://github.com/AtomHackPaws/ML_Service.git
```

Заходим в папку:

```bash
$ cd ML_Service/
```

Заполнить файл в корне .env:

```
POSTGRES_HOST=hostname
POSTGRES_PORT=5431
POSTGRES_DATABASE=database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=qweFgHqdsHz
MINIO_LINK=http://hostname:9200
KAFKA_URL=hostname:9093
MINIO_ROOT_USER=minio_user
MINIO_ROOT_PASSWORD=minio_pass
MINIO_BUCKET=bucket_name
```

Установка локального окружения:

```bash
$ python3 -m venv venv 
```

Активация локального окружения:

```bash
$ source venv/bin/activate 
```

Установка необходимых зависимостей:

```bash
$ pip intall -r requirements.txt 
```

Запуск сервиса:

```bash
$ faststream run app.main:app --reload
```

### В docker

Установка через docker:

```bash
$ docker-compose up -d --build 
```
