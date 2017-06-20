# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections
import io
import os
import re
import shutil
import tempfile
import warnings

from django.utils import six

from yepes.apps import apps
from yepes.contrib.datamigrations import ModelMigration
from yepes.contrib.datamigrations.importation_plans import importation_plans
from yepes.contrib.datamigrations.serializers import serializers
from yepes.contrib.datamigrations.utils import sort_dependencies

TITLE_RE = re.compile(r'^-- Name: ([.\w]+); Type: ([.\w]+); Serializer: ([.\w]+)')
HEADER_LINES = ['\n', '--\n', TITLE_RE, '--\n', '\n']
FILE_NAME_RE = re.compile(r'^(\w+)\.(\w+)\.(\w+)$')


class MultipleExportFacade(object):

    # PUBLIC METHODS

    @classmethod
    def to_directory(cls, dir, **options):
        if not os.path.exists(dir):
            os.makedirs(dir)

        migration_kwargs, export_kwargs = cls._clean_options(options)

        model_list = sort_dependencies(migration_kwargs.pop('models'))
        model_list.reverse()

        serializer = export_kwargs.pop('serializer')
        for model in model_list:
            migration = ModelMigration(model, **migration_kwargs)
            migration_serializer = migration.get_serializer(serializer)
            file_name = '{0}.{1}.{2}'.format(
                    model._meta.app_label,
                    model._meta.model_name,
                    migration_serializer.name)

            file_path = os.path.join(dir, file_name)
            with migration_serializer.open_to_dump(file_path) as file:
                migration.export_data(file, migration_serializer, **export_kwargs)

    @classmethod
    def to_compressed_file(cls, file, **options):
        temp_dir = tempfile.mkdtemp(prefix='export_')
        cls.to_directory(temp_dir, **options)
        cls._compress_directory(temp_dir, file)
        try:
            shutil.rmtree(six.text_type(temp_dir))
        except OSError:
            msg = 'Failed to remove temp directory: {0}'
            warnings.warn(msg.format(temp_dir), RuntimeWarning)

    @classmethod
    def to_compressed_file_path(cls, file_path, **options):
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with io.open(file_path, 'wb') as file:
            cls.to_compressed_file(file, **options)

    @classmethod
    def to_file(cls, file, **options):
        temp_dir = tempfile.mkdtemp(prefix='export_')
        cls.to_directory(temp_dir, **options)
        cls._join_directory(temp_dir, file)
        try:
            shutil.rmtree(six.text_type(temp_dir))
        except OSError:
            msg = 'Failed to remove temp directory: {0}'
            warnings.warn(msg.format(temp_dir), RuntimeWarning)

    @classmethod
    def to_file_path(cls, file_path, **options):
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with io.open(file_path, 'wt') as file:
            cls.to_file(file, **options)

    # PRIVATE METHODS

    @classmethod
    def _clean_options(cls, opts):
        selected_models = opts.pop('models', None)
        if not selected_models:
            model_list = apps.get_models(include_auto_created=True)
        else:
            model_list = []
            for model in selected_models:
                if not isinstance(model, six.string_types):
                    model_list.append(model)
                elif '.' in model:
                    model = apps.get_model(model)
                    model_list.append(model)
                else:
                    app_config = apps.get_app_config(model)
                    model_list.extend(app_config.get_models(include_auto_created=True))

        use_natural_keys = opts.pop('use_natural_keys', False)

        migration_kwargs = {
            'models': model_list,
            'use_natural_primary_keys': use_natural_keys,
            'use_natural_foreign_keys': use_natural_keys,
            'use_base_manager': opts.pop('use_base_manager', False),
        }
        serializer = opts.pop('serializer', None)

        if isinstance(serializer, six.string_types):
            serializer = serializers.get_serializer(serializer)

        if isinstance(serializer, collections.Callable):
            serializer = serializer(**opts)

        export_kwargs = {
            'serializer': serializer,
        }
        return migration_kwargs, export_kwargs

    @classmethod
    def _compress_directory(cls, input_dir, output_file):
        raise NotImplementedError

    @classmethod
    def _join_directory(self, input_dir, output_file):
        input_files = os.listdir(input_dir)
        input_files.sort()
        for file_name in input_files:
            matchobj = FILE_NAME_RE.search(file_name)
            if matchobj is not None:
                output_file.write('\n')
                output_file.write('--\n')
                output_file.write('-- Name: {0}.{1}; Type: MODEL; Serializer: {2}\n'.format(
                                                        matchobj.group(1),
                                                        matchobj.group(2),
                                                        matchobj.group(3)))
                output_file.write('--\n')
                output_file.write('\n')
                file_path = os.path.join(input_dir, file_name)
                with io.open(file_path, 'rt') as input_file:
                    for line in input_file:
                        output_file.write(line)

                output_file.write('\n')


class MultipleImportFacade(object):

    # PUBLIC METHODS

    @classmethod
    def from_directory(cls, dir, **options):
        if not os.path.exists(dir):
            raise AttributeError("Directory '{0}' does not exit.".format(dir))

        migration_kwargs, import_kwargs = cls._clean_options(options)
        selected_models = migration_kwargs.pop('models')
        selected_serializer = import_kwargs.pop('serializer')

        found_models = []
        files_and_serializers = {}
        for file_name in os.listdir(dir):
            matchobj = FILE_NAME_RE.search(file_name)
            if matchobj is None:
                continue

            app_config = apps.get_app_config(matchobj.group(1))
            model = app_config.get_model(matchobj.group(2))
            if selected_models and model not in selected_models:
                continue

            serializer = (selected_serializer
                          or serializers.get_serializer(matchobj.group(3))())

            found_models.append(model)
            files_and_serializers[model] = (file_name, serializer)

        model_list = sort_dependencies(found_models)
        for model in model_list:
            migration = ModelMigration(model, **migration_kwargs)
            file_name, serializer = files_and_serializers[model]
            file_path = os.path.join(dir, file_name)
            with serializer.open_to_load(file_path) as file:
                migration.import_data(file, serializer, **import_kwargs)

    @classmethod
    def from_compressed_file(cls, file, **options):
        temp_dir = tempfile.mkdtemp(prefix='import_')
        cls._uncompress_directory(file, temp_dir)
        cls.from_directory(temp_dir, **options)
        try:
            shutil.rmtree(six.text_type(temp_dir))
        except OSError:
            msg = 'Failed to remove temp directory: {0}'
            warnings.warn(msg.format(temp_dir), RuntimeWarning)

    @classmethod
    def from_compressed_file_path(cls, file_path, **options):
        if not os.path.exists(file_path):
            raise AttributeError("File '{0}' does not exit.".format(file_path))

        with io.open(file_path, 'rb') as file:
            cls.from_compressed_file(file, **options)

    @classmethod
    def from_file(cls, file, **options):
        temp_dir = tempfile.mkdtemp(prefix='import_')
        cls._split_file(file, temp_dir)
        cls.from_directory(temp_dir, **options)
        try:
            shutil.rmtree(six.text_type(temp_dir))
        except OSError:
            msg = 'Failed to remove temp directory: {0}'
            warnings.warn(msg.format(temp_dir), RuntimeWarning)

    @classmethod
    def from_file_path(cls, file_path, **options):
        if not os.path.exists(file_path):
            raise AttributeError("File '{0}' does not exit.".format(file_path))

        with io.open(file_path, 'rt') as file:
            cls.from_file(file, **options)

    # PRIVATE METHODS

    @classmethod
    def _clean_options(cls, opts):
        selected_models = opts.pop('models', None)
        model_list = []
        if selected_models:
            for model in selected_models:
                if not isinstance(model, six.string_types):
                    model_list.append(model)
                elif '.' in model:
                    model = apps.get_model(model)
                    model_list.append(model)
                else:
                    app_config = apps.get_app_config(model)
                    model_list.extend(app_config.get_models(include_auto_created=True))

        use_natural_keys = opts.pop('use_natural_keys', False)

        migration_kwargs = {
            'models': model_list,
            'use_natural_primary_keys': use_natural_keys,
            'use_natural_foreign_keys': use_natural_keys,
            'ignore_missing_foreign_keys': opts.pop('ignore_missing_foreign_keys', False),
        }
        serializer = opts.pop('serializer', None)
        plan = opts.pop('plan', None)
        batch_size = opts.pop('batch_size', 100)

        if isinstance(serializer, six.string_types):
            serializer = serializers.get_serializer(serializer)

        if isinstance(serializer, collections.Callable):
            serializer = serializer(**opts)

        if isinstance(plan, six.string_types):
            plan = importation_plans.get_plan(plan)

        import_kwargs = {
            'serializer': serializer,
            'plan': plan,
            'batch_size': batch_size,
        }
        return migration_kwargs, import_kwargs

    @classmethod
    def _split_file(cls, input_file, output_dir):
        buffer = []
        header_found = False
        output_file = None
        model_name = None
        serializer_name = None
        next_model = None
        next_serializer = None
        try:
            for line in input_file:
                expected_line = HEADER_LINES[len(buffer)]
                if expected_line == TITLE_RE:
                    buffer.append(line)
                    matchobj = TITLE_RE.search(line)
                    if matchobj is not None:
                        if matchobj.group(2).upper() == 'MODEL':
                            next_model = matchobj.group(1)
                            next_serializer = matchobj.group(3)
                        else:
                            next_model = None
                            next_serializer = None

                elif line == expected_line:
                    buffer.append(line)
                    if len(buffer) == len(HEADER_LINES):
                        header_found = True
                        if output_file is not None:
                            output_file.close()
                            output_file = None

                        model_name = next_model
                        next_model = None
                        serializer_name = next_serializer
                        next_serializer = None
                        if model_name is not None:
                            file_name = model_name + '.' + serializer_name
                            file_path = os.path.join(output_dir, file_name)
                            output_file = io.open(file_path, 'wt')

                        del buffer[:]

                else:
                    if buffer:
                        if output_file is not None:
                            output_file.writelines(buffer)

                        del buffer[:]

                    if output_file is not None:
                        output_file.write(line)

            if buffer:
                if output_file is not None:
                    output_file.writelines(buffer)

                del buffer[:]

        finally:
            if output_file is not None:
                output_file.close()
                output_file = None

        if not header_found:
            raise ValueError('Invalid file format.')

    @classmethod
    def _uncompress_directory(cls, input_file, output_dir):
        raise NotImplementedError


class SingleExportFacade(object):

    # PUBLIC METHODS

    @classmethod
    def to_compressed_file(cls, file, **options):
        temp_dir = tempfile.mkdtemp(prefix='export_')

        migration_kwargs, export_kwargs = cls._clean_options(options)
        model = migration_kwargs['model']
        serializer = export_kwargs['serializer']
        temp_file_name = '{0}.{1}.{2}'.format(
                model._meta.app_label,
                model._meta.model_name,
                serializer.name)

        temp_file_path = os.path.join(temp_dir, temp_file_name)
        cls.to_file_path(temp_file_path, **options)
        with io.open(temp_file_path, 'rb') as temp_file:
            cls._compress_file(temp_file, file)

        try:
            shutil.rmtree(six.text_type(temp_dir))
        except OSError:
            msg = 'Failed to remove temp directory: {0}'
            warnings.warn(msg.format(temp_dir), RuntimeWarning)

    @classmethod
    def to_compressed_file_path(cls, file_path, **options):
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with io.open(file_path, 'wb') as file:
            cls.to_compressed_file(file, **options)

    @classmethod
    def to_file(cls, file, **options):
        migration_kwargs, export_kwargs = cls._clean_options(options)
        migration = ModelMigration(**migration_kwargs)
        migration.export_data(file, **export_kwargs)

    @classmethod
    def to_file_path(cls, file_path, **options):
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        if not options.get('model'):
            _, file_name = os.path.split(file_path)
            matchobj = FILE_NAME_RE.search(file_name)
            if matchobj is not None:
                app_label = matchobj.group(1)
                model_name = matchobj.group(2)
                if app_label in apps.app_configs:
                    app_config = apps.get_app_config(app_label)
                    if model_name in app_config.models:
                        options['model'] = app_config.get_model(model_name)

        if not options.get('serializer'):
            _, file_ext = os.path.splitext(file_path)
            serializer_name = file_ext.lstrip('.')
            if serializers.has_serializer(serializer_name):
                options['serializer'] = serializer_name

        migration_kwargs, export_kwargs = cls._clean_options(options)
        options = migration_kwargs.copy()
        options.update(export_kwargs)

        serializer = export_kwargs['serializer']
        with serializer.open_to_dump(file_path) as file:
            cls.to_file(file, **options)

    # PRIVATE METHODS

    @classmethod
    def _clean_options(cls, opts):
        if 'model' not in opts:
            raise AttributeError('You must give a model.')

        model = opts.pop('model')
        if isinstance(model, six.string_types):
            model = apps.get_model(model)

        migration_kwargs = {
            'model': model,
            'fields': opts.pop('fields', None),
            'exclude': opts.pop('exclude', None),
            'use_natural_primary_keys': opts.pop('use_natural_primary_keys', False),
            'use_natural_foreign_keys': opts.pop('use_natural_foreign_keys', False),
            'use_base_manager': opts.pop('use_base_manager', False),
        }
        serializer = opts.pop('serializer', None)

        if isinstance(serializer, six.string_types):
            serializer = serializers.get_serializer(serializer)

        if isinstance(serializer, collections.Callable):
            serializer = serializer()

        export_kwargs = {
            'serializer': serializer,
        }
        return migration_kwargs, export_kwargs

    @classmethod
    def _compress_file(cls, input_file, output_file):
        raise NotImplementedError


class SingleImportFacade(object):

    # PUBLIC METHODS

    @classmethod
    def from_compressed_file(cls, file, **options):
        temp_dir = tempfile.mkdtemp(prefix='import_')

        migration_kwargs, import_kwargs = cls._clean_options(options)
        model = migration_kwargs['model']
        serializer = import_kwargs['serializer']
        temp_file_name = '{0}.{1}.{2}'.format(
                model._meta.app_label,
                model._meta.model_name,
                serializer.name)

        temp_file_path = os.path.join(temp_dir, temp_file_name)
        with io.open(temp_file_path, 'wb') as temp_file:
            cls._uncompress_file(file, temp_file)

        cls.from_file_path(temp_file_path, **options)

        try:
            shutil.rmtree(six.text_type(temp_dir))
        except OSError:
            msg = 'Failed to remove temp directory: {0}'
            warnings.warn(msg.format(temp_dir), RuntimeWarning)

    @classmethod
    def from_compressed_file_path(cls, file_path, **options):
        if not os.path.exists(file_path):
            raise AttributeError("File '{0}' does not exit.".format(file_path))

        with io.open(file_path, 'rb') as file:
            cls.from_compressed_file(file, **options)

    @classmethod
    def from_file(cls, file, **options):
        migration_kwargs, import_kwargs = cls._clean_options(options)
        migration = ModelMigration(**migration_kwargs)
        migration.import_data(file, **import_kwargs)

    @classmethod
    def from_file_path(cls, file_path, **options):
        if not os.path.exists(file_path):
            raise AttributeError("File '{0}' does not exit.".format(file_path))

        if not options.get('model'):
            _, file_name = os.path.split(file_path)
            matchobj = FILE_NAME_RE.search(file_name)
            if matchobj is not None:
                app_label = matchobj.group(1)
                model_name = matchobj.group(2)
                if app_label in apps.app_configs:
                    app_config = apps.get_app_config(app_label)
                    if model_name in app_config.models:
                        options['model'] = app_config.get_model(model_name)

        if not options.get('serializer'):
            _, file_ext = os.path.splitext(file_path)
            serializer_name = file_ext.lstrip('.')
            if serializers.has_serializer(serializer_name):
                options['serializer'] = serializer_name

        migration_kwargs, import_kwargs = cls._clean_options(options)
        options = migration_kwargs.copy()
        options.update(import_kwargs)

        serializer = import_kwargs['serializer']
        with serializer.open_to_load(file_path) as file:
            cls.from_file(file, **options)

    # PRIVATE METHODS

    @classmethod
    def _clean_options(cls, opts):
        if 'model' not in opts:
            raise AttributeError('You must give a model.')

        model = opts.pop('model')
        if isinstance(model, six.string_types):
            model = apps.get_model(model)

        migration_kwargs = {
            'model': model,
            'fields': opts.pop('fields', None),
            'exclude': opts.pop('exclude', None),
            'use_natural_primary_keys': opts.pop('use_natural_primary_keys', False),
            'use_natural_foreign_keys': opts.pop('use_natural_foreign_keys', False),
            'ignore_missing_foreign_keys': opts.pop('ignore_missing_foreign_keys', False),
        }
        serializer = opts.pop('serializer', None)
        plan = opts.pop('plan', None)
        batch_size = opts.pop('batch_size', 100)

        if isinstance(serializer, six.string_types):
            serializer = serializers.get_serializer(serializer)

        if isinstance(serializer, collections.Callable):
            serializer = serializer(**opts)

        if isinstance(plan, six.string_types):
            plan = importation_plans.get_plan(plan)

        import_kwargs = {
            'serializer': serializer,
            'plan': plan,
            'batch_size': batch_size,
        }
        return migration_kwargs, import_kwargs

    @classmethod
    def _uncompress_file(cls, input_file, output_file):
        raise NotImplementedError

