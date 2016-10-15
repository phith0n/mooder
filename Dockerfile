FROM grahamdumpleton/mod-wsgi-docker:python-3.5-onbuild

RUN chown $MOD_WSGI_USER:$MOD_WSGI_GROUP -R .

USER $MOD_WSGI_USER:$MOD_WSGI_GROUP