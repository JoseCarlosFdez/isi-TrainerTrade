FROM python:3.11.6

RUN mkdir /trainer-trade
WORKDIR /trainer-trade
ADD . /trainer-trade
RUN pip install -r requirements.txt

EXPOSE 8000

