import functools

from django.core.cache import cache


def cache_using_pk(func):
    """
    Given a model instance, cache the value from an instance method using the primary key
    """

    @functools.wraps(func)
    def wrapper(instance, *args, **kwargs):
        cache_key = '{func_name}-{pk}'.format(func_name=func.func_name, pk=instance.pk)
        return cache.get_or_set(cache_key, functools.partial(func, instance, *args, **kwargs))

    return wrapper
