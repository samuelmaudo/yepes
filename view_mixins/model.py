# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.types import Undefined


class ModelMixin(object):

    _model = Undefined

    def get_model(self):
        if self._model is Undefined:

            try:
                # If model has been explicitly provided, use it.
                self._model = self.model
            except AttributeError:
                self._model = None

            if self._model is None:
                try:
                    # If this view is operating on a single object, use the
                    # class of that object.
                    self._model = self.object.__class__
                except AttributeError:
                    try:
                        # If this view is operating on a list of objects, try
                        # to get the model class from that.
                        self._model = self.object_list.model
                    except AttributeError:
                        try:
                            # Try to get a queryset and extract the model class
                            # from that.
                            self._model = self.get_queryset().model
                        except AttributeError:
                            pass

        return self._model

