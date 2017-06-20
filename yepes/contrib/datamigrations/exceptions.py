# -*- coding:utf-8 -*-

from __future__ import unicode_literals


class DataMigrationError(Exception):
    pass


class DataExportionError(DataMigrationError):
    """
    Raised when an error occurs during export.
    """
    pass


class DataImportionError(DataMigrationError):
    """
    Raised when an error occurs during import.
    """
    pass


class UnableToCreateError(DataImportionError):
    """
    Raised when data migration does not support creating new model objects.
    """
    def __init__(self, msg='Migration does not support creating new objects.'):
        super(UnableToCreateError, self).__init__(msg)


class UnableToExportError(DataExportionError):
    """
    Raised when data migration does not allow exporting model objects.
    """
    def __init__(self, msg='Migration does not allow exports.'):
        super(UnableToExportError, self).__init__(msg)


class UnableToImportError(DataImportionError):
    """
    Raised when data migration does not allow importing model objects.
    """
    def __init__(self, msg='Migration does not allow imports.'):
        super(UnableToImportError, self).__init__(msg)


class UnableToUpdateError(DataImportionError):
    """
    Raised when data migration does not support updating model objects.
    """
    def __init__(self, msg='Migration does not support updating objects.'):
        super(UnableToUpdateError, self).__init__(msg)
