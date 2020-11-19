FROM nikolaik/python-nodejs:latest

RUN apt-get update && \
    apt-get install --assume-yes --no-install-recommends \
            git \
            gcc \
            libffi-dev \
            libssl-dev \
            libxml2-dev \
            libxslt1-dev \
            zlib1g-dev \
            && \
    rm -rf /var/cache/apt/* /var/lib/apt/lists/* && \
    rm -rf /tmp/* /var/tmp/*

RUN python3 -m pip install --no-cache-dir --upgrade git+https://github.com/maximiliancw/scrapy-do

WORKDIR /app

COPY . /etc/scrapy-do

EXPOSE 7654

CMD scrapy-do -n scrapy-do --config /etc/scrapy-do/server.conf