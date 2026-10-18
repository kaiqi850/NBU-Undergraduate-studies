from celery.schedules import crontab

broker_url = 'redis://127.0.0.1:6379/1'
result_backend = 'redis://127.0.0.1:6379/2'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Shanghai'
enable_utc = True

include = ['tasks']


beat_schedule = {
    'update': {
        'task': 'tasks.update',
        # 定时时间
        'schedule': crontab(minute=10),
        # 执行的函数需要的参数
        'args': ()
    }
}