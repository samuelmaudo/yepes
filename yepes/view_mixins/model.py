# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.types import Undefined


class ModelMixin(object):
    """
    Adds a convenience method for easily obtain the model of the view object.
    """

    _model = Undefined

    def get_model(self):
        """
        Returns the model of the view object.

        First looks for ``self.model``. If it is not set, looks for
        ``self.object``. If it is also not set, looks for ``self.object_list``.
        And finally tries with ``self.get_queryset()``.
        """
        if self._model is Undefined:

            try:
                # If model has been explicitly provided, use it.
                self._model = self.model
            except AttributeError:
                self._model = None

            if self._model is None:
                try:
                    # If this view is operating on a single object,  use the
                    # class of that object.
                    self._model = self.object.__class__
                except AttributeError:
                    try:
                        # If this view is operating on a list of objects, try
                        # to get the model class from that.
                        self._model = self.object_list.model
                    except AttributeError:
                        try:
                            # Try to get a queryset and extract the model
                            # class from that.
                            self._model = self.get_queryset().model
                        except AttributeError:
                            pass

        return self._model

