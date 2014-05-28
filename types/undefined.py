# -*- coding:utf-8 -*-

from django.utils import six

from yepes.types.singleton import SingletonMetaclass


@six.add_metaclass(SingletonMetaclass)
class UndefinedType(object):

    __slots__ = ()

    def __bool__(self):
        return False

    def __nonzero__(self):
        return self.__bool__()

    def __repr__(self):
        return 'Undefined'


Undefined = UndefinedType()

