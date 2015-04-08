FROM gliderlabs/alpine:3.1
MAINTAINER Jason Boyles

RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base \
 && rm -rf /var/cache/apk/*

ADD . /usr/local/tasker

WORKDIR /usr/local/tasker

RUN pip install -r requirements.txt

USER celery
CMD /usr/local/bin/celery -A tasker worker -B --loglevel=info
