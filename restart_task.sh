kill -9 `ps -ef|grep celery|grep -v grep|awk '{print $2}'`
nohup celery -B -A task worker -l info >> celery.info &

