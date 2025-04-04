### Запук приложения:

dev
```
uvicorn main:app --reload --port 8000
```

### Запуск celery:

```
celery -A app.celery_app.celery_app worker --loglevel=info
```