FROM python:latest

RUN mkdir /code
COPY ./requirements.txt /code
WORKDIR /code
RUN pip install -r requirements.txt


RUN mkdir /start
COPY ./start.sh /start
RUN chmod +x /start/start.sh

RUN useradd limitado -s /bin/bash
USER limitado

CMD /start/start.sh


