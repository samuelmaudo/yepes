# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.core.cache import cache
from django.db import models


class ParameterManager(models.Manager):

    def get_choices(self):
        cache_key = 'metrics.parameters.{0}'.format(
                        self.model.__name__.lower())
        choices = cache.get(cache_key)
        if choices is None:
            choices = []
            processed = {}
            unprocessed = list(self.all())
            pending = len(unprocessed)
            i = 0
            while pending and i < 10:
                j = 0
                while j < pending:
                    obj = unprocessed[j]
                    parent_key = obj.parent_id

                    if parent_key is None:
                        level = choices
                    elif parent_key in processed:
                        level = processed[parent_key][3]
                    else:
                        j += 1
                        continue

                    choice = (obj.pk, obj.token.lower(), obj.regex, [])
                    level.append(choice)
                    processed[obj.pk] = choice
                    del unprocessed[j]
                    pending -= 1
                    continue

                i += 1

            cache.set(cache_key, choices)
        return choices

    def detect(self, user_agent):
        return self._detect(user_agent.lower(), self.get_choices())

    def _detect(self, ua, choices):
        for pk, token, regex, children in choices:
            if regex:
                if re.search(token, ua) is not None:
                    child_pk = self._detect(ua, children)
                    return child_pk if child_pk is not None else pk
            else:
                if token in ua:
                    child_pk = self._detect(ua, children)
                    return child_pk if child_pk is not None else pk

