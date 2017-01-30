FROM ubuntu:16.04
RUN apt-get update 
RUN apt-get install -y python git libpq-dev python-pip python-dateutil python-tk postgresql-client
RUN pip install --upgrade pip
RUN pip install requests psycopg2 numpy requests_oauthlib selenium BeautifulSoup bs4 matplotlib
WORKDIR /root/app/
