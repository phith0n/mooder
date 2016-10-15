FROM grahamdumpleton/mod-wsgi-docker:python-3.5-onbuild

RUN chown $MOD_WSGI_USER:$MOD_WSGI_GROUP -R . && chmod +x .whiskey/action_hooks/deploy && chmod +x .whiskey/action_hooks/pre-build && chown $MOD_WSGI_USER:$MOD_WSGI_GROUP -R /data

VOLUME ["/data"]

USER $MOD_WSGI_USER:$MOD_WSGI_GROUP