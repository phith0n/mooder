FROM grahamdumpleton/mod-wsgi-docker:python-3.5-onbuild

USER $MOD_WSGI_USER:$MOD_WSGI_GROUP

RUN chown $MOD_WSGI_USER:$MOD_WSGI_GROUP -R .