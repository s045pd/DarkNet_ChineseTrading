kill -9 `ps -ef|grep celery|grep -v grep|awk '{print $2}'`
celery -B -A task worker -l info

