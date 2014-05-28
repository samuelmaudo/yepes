# -*- coding:utf-8 -*-

try:
    import threading
except ImportError:
    import dummy_threading as threading


class SingletonMetaclass(type):

    def __new__(mcls, name, bases, namespace):
        namespace.setdefault('__lock__', threading.RLock())
        namespace.setdefault('__instance__', None)
        sup = super(SingletonMetaclass, mcls)
        return sup.__new__(mcls, name, bases, namespace)

    def __call__(cls, *args, **kw):
        cls.__lock__.acquire()
        try:
            if cls.__instance__ is None:
                instance = cls.__new__(cls, *args, **kw)
                instance.__init__(*args, **kw)
                cls.__instance__ = instance
        finally:
            cls.__lock__.release()
        return cls.__instance__

