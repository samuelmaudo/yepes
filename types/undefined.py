# -*- coding:utf-8 -*-

from yepes.types.singleton import Singleton


class UndefinedType(Singleton):

    __slots__ = ()

    def __bool__(self):
        return False

    __nonzero__ = __bool__

    def __repr__(self):
        return 'Undefined'


Undefined = UndefinedType()

