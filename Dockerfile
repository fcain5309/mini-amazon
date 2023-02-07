FROM python:3.7.3

RUN mkdir /srv/app
WORKDIR /srv/app
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .
EXPOSE 8080
CMD ["./start_production.sh"]