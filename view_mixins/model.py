# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.types import Undefined


class ModelMixin(object):

    _model = Undefined

    def get_model(self):
        if self._model is Undefined:
            # If a model has been explicitly provided, use it.
            if getattr(self, 'model', None) is not None:
                self._model = self.model

            # If this view is operating on a single object, use the class
            # of that object.
            elif getattr(self, 'object', None) is not None:
                self._model = self.object.__class__

            # If this view is operating on a list of objects, try to get
            # the model class from that.
            elif (getattr(self, 'object_list', None) is not None
                    and getattr(self, 'model', None) is not None):
                self._model = self.object_list.model

            # Try to get a queryset and extract the model class from that.
            else:
                qs = self.get_queryset()
                if getattr(qs, 'model', None) is not None:
                    self._model = qs.model
                else:
                    self._model = None

        return self._model

