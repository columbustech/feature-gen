FROM python:3

RUN apt-get update && apt-get install -y vim nginx
COPY nginx.conf /etc/nginx/
COPY frontend.conf /etc/nginx/conf.d/

RUN wget https://nodejs.org/dist/v12.13.1/node-v12.13.1-linux-x64.tar.xz
RUN mkdir -p /usr/local/lib/nodejs
RUN tar -xJf node-v12.13.1-linux-x64.tar.xz -C /usr/local/lib/nodejs
ENV PATH="/usr/local/lib/nodejs/node-v12.13.1-linux-x64/bin:${PATH}"

WORKDIR /ui
COPY ui/package.json .
COPY ui/package-lock.json .
COPY ui/src/ ./src/
COPY ui/public/ ./public/
RUN npm install
RUN npm run build
RUN mkdir /var/www/frontend
RUN cp -r build/* /var/www/frontend

WORKDIR /api
COPY requirements.txt /api/
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY ./api/ /api/

CMD service nginx start && python manage.py migrate && python manage.py runserver 0.0.0.0:8001
