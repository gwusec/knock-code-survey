# Django Installation Notes

## Packages needed

### django-user-agent

Source Page

https://github.com/selwin/django-user_agents

Install via `pip` 

```
pip install pyyaml ua-parser user-agents python-memcached
pip install django-user-agents
```

Add to `settings.py`

```
INSTALLED_APPS = (
    # Other apps...
    'django_user_agents',
)

# Cache backend is optional, but recommended to speed up user agent parsing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# Name of cache backend to cache user agents. If it not specified default
# cache alias will be used. Set to `None` to disable caching.
USER_AGENTS_CACHE = 'default'

MIDDLEWARE_CLASSES = (
    # other middlewares...
    'django_user_agents.middleware.UserAgentMiddleware',
)
```

Then you can use like:
