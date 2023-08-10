FROM python:3.10

RUN apt-get update && apt-get -y install cron

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN crontab crontab

CMD ["crond", "-f"]