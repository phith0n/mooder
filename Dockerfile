FROM grahamdumpleton/mod-wsgi-docker:python-3.5

WORKDIR /app

COPY . /app

RUN chown $MOD_WSGI_USER:$MOD_WSGI_GROUP -R .
RUN chmod +x .whiskey/action_hooks/deploy
RUN chmod +x .whiskey/action_hooks/pre-build
RUN chmod +x .whiskey/action_hooks/build
RUN chown $MOD_WSGI_USER:$MOD_WSGI_GROUP -R /data

RUN mod_wsgi-docker-build

EXPOSE 80

ENTRYPOINT [ "mod_wsgi-docker-start" ]

VOLUME ["/data"]

USER $MOD_WSGI_USER:$MOD_WSGI_GROUP