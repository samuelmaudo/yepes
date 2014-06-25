# -*- coding:utf-8 -*-

try:
    import threading
except ImportError:
    import dummy_threading as threading

from django.utils import six


class SingletonMetaclass(type):

    def __new__(mcls, name, bases, namespace):
        namespace.setdefault('__lock__', threading.RLock())
        namespace.setdefault('__instance__', None)
        sup = super(SingletonMetaclass, mcls)
        return sup.__new__(mcls, name, bases, namespace)


@six.add_metaclass(SingletonMetaclass)
class Singleton(object):

    def __new__(cls, *args, **kwargs):
        cls.__lock__.acquire()
        try:
            if cls.__instance__ is None:
                sup = super(Singleton, cls)
                cls.__instance__ = sup.__new__(cls, *args, **kwargs)
        finally:
            cls.__lock__.release()
        return cls.__instance__

