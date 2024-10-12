FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["scrapy", "crawl", "vnexpress", "-o", "data/docker.json"]