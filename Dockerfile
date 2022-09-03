FROM python:3.9-buster

ADD requirements.txt .

RUN python --version
#RUN pip3 install -r requirements.txt