FROM python:latest

ARG user
ARG uid

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code
RUN pip3 install -r requirements.txt

RUN apt-get update && apt-get install docker docker-compose -y

ENV DJANGO_KEY=""
ENV BD_NAME=""
ENV BD_USER=""
ENV BD_PASSWORD=""
ENV BD_HOST=""
ENV BD_PORT=""
ENV PUBLIC_KEY=""
ENV PRIVATE_KEY="" 



ADD start.sh /code
RUN chmod +x start.sh

RUN mkdir /app
WORKDIR /app

RUN useradd $user -u $uid -s /bin/bash

RUN chown -R $user /code
RUN chmod -R 500 /code 
RUN chown -R $user /app
RUN gpasswd -a $user docker
# RUN (echo soptec1035; echo soptec1035) | passwd $user
#USER $user

CMD /bin/bash -c '/code/start.sh' && /bin/bash
