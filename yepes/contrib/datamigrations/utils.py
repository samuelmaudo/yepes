# -*- coding:utf-8 -*-

from collections import OrderedDict

from django.db.models import ForeignKey
from django.utils import six


def sort_dependencies(model_list):
    """
    Sorts a list of models to ensure that any model with a ForeignKey
    pointing to another model in the list is serialized after its
    dependency.
    """
    # Remove all duplicates from the list of models.
    model_set = set()
    model_list = [
        x
        for x
        in model_list
        if x not in model_set and not model_set.add(x)
    ]

    # Find any model that depends on other models in the list.
    model_dependencies = OrderedDict()
    for model in model_list:
        for field in model._meta.fields:
            if (isinstance(field, ForeignKey)
                    and field.related_model != model
                    and field.related_model in model_set):

                if model not in model_dependencies:
                    model_dependencies[model] = [field.related_model]
                else:
                    model_dependencies[model].append(field.related_model)

    # Add the models without dependencies to the final list.
    sorted_list = []
    for model in model_list:
        if model not in model_dependencies:
            sorted_list.append(model)

    # Now iterate repeatedly over the dependency list to add the models
    # whose dependencies were already added to the final list.
    # This process continues until the dependency list is empty, or we
    # do a full iteration over the model dependencies without promoting
    # a model to the final list.
    # If we do a full iteration without a promotion, that means there
    # are circular dependencies in the list.
    while model_dependencies:
        clean_models = []
        for model, dependencies in six.iteritems(model_dependencies):
            if all(d in sorted_list for d in dependencies):
                clean_models.append(model)

        if not clean_models:
            msg = "Can't resolve dependencies for {0}."
            raise RuntimeError(msg.format(', '.join(
                six.text_type(model._meta)
                for model
                in six.iterkeys(model_dependencies)
            )))

        for model in clean_models:
            del model_dependencies[model]

        sorted_list.extend(clean_models)
        del clean_models[:]

    return sorted_list

