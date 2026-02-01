from celery import Celery
from app.config import settings

celery_app = Celery(
    "speech_practice",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    task_routes={
        'app.tasks.stt.*': {'queue': 'stt'},
        'app.tasks.prosody.*': {'queue': 'prosody'},
        'app.tasks.llm.*': {'queue': 'llm'}
    }
)
