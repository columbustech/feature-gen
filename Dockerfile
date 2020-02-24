FROM python:3

RUN mkdir /api
WORKDIR /api
COPY requirements.txt /api/
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY ./api/ /api/

RUN apt-get update && apt-get install -y vim nginx
COPY nginx.conf /etc/nginx/
COPY frontend.conf /etc/nginx/conf.d/
COPY ./ui/build/ /var/www/frontend/

CMD service nginx start && python manage.py migrate && python manage.py runserver 0.0.0.0:8001
