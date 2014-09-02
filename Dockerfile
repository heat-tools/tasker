FROM ubuntu:14.04
MAINTAINER Jason Boyles

RUN groupadd -r celery && useradd -r -g celery celery

RUN apt-get update \
    && apt-get install -y python python-pip --no-install-recommends

ADD . /usr/local/tasker

WORKDIR /usr/local/tasker

RUN chown -R celery.celery .

RUN pip install -r requirements.txt

USER celery
CMD /usr/local/bin/celery -A tasker worker -B
