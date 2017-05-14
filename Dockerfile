FROM lambci/lambda:build

MAINTAINER "Andrew Krug <andrewkrug@gmail.com>

RUN yum clean all && \
    yum -y install rubygems python27-devel python27-virtualenv vim postgresql postgresql-devel mysql mysql-devel gcc libyaml-devel python27-pyOpenSSL && \
    pip install -U pip && \
    pip install -U zappa mysql-python

WORKDIR /var/task

RUN virtualenv /var/venv && \
    source /var/venv/bin/activate && \
    pip install -U pip && \
    deactivate

CMD ["zappa"]
