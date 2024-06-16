# ML_Service
Сервис детектирования и классификации сварных швов

## Запуск сервиса
### На локальной машине

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
