FROM grahamdumpleton/mod-wsgi-docker:python-3.5

WORKDIR /app

COPY . /app

RUN mod_wsgi-docker-build

EXPOSE 80

ENTRYPOINT [ "docker-start.sh" ]

CMD [ "mooder/wsgi.py" ]