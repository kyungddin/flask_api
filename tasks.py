from celery_app import celery

@celery.task
def slow_add(a, b):
    return a + b

