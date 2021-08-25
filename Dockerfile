FROM ubuntu:20.04


RUN apt update && apt install --no-install-recommends -y procps gcc tor python3-dev python3-pip

WORKDIR /opt/darknet

COPY darknet ./darknet
COPY requirements.txt .
COPY grafana.sql .
COPY entrypoints.sh /

RUN pip install  --no-cache-dir -r  /opt/darknet/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/


RUN rm -rf /var/lib/apt/lists/* 

EXPOSE 80 

CMD ["/bin/sh", "/entrypoints.sh"]
