# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from datetime import date, datetime, time
from decimal import Decimal

from django import test
from django.utils.timezone import utc as UTC

from yepes import admin
from yepes.admin.operations import (
    Set, SetNull,
    Add, Sub, Mul, Div,
    Swap,
    Lower, Upper, Capitalize, Title, SwapCase, Strip
)
from yepes.admin.views import MassUpdateView
from yepes.tests.admin.admin import MassUpdateAdmin
from yepes.tests.admin.models import MassUpdateModel


class MassUpdateTest(test.TestCase):

    def setUp(self):
        self.record_1 = MassUpdateModel.objects.create()
        self.record_2 = MassUpdateModel.objects.create()
        self.record_3 = MassUpdateModel.objects.create()
        self.model_admin = MassUpdateAdmin(MassUpdateModel, admin.site)
        self.model_fields = {
            field.name: field
            for field
            in MassUpdateModel._meta.fields
        }
        self.view = MassUpdateView.as_view(model_admin=self.model_admin)

    def test_assignment_operations(self):
        for obj in MassUpdateModel.objects.all():
            #self.assertEqual(obj.binary, b'abc')
            self.assertEqual(obj.boolean, False)
            self.assertEqual(obj.char, 'abc def')
            self.assertEqual(obj.date, date(1986, 9, 25))
            self.assertEqual(obj.date_time, datetime(1986, 9, 25, 12, 0, 0, tzinfo=UTC))
            self.assertEqual(obj.decimal, Decimal('10.0'))
            self.assertEqual(obj.float, 10.0)
            self.assertEqual(obj.integer, 10)
            self.assertEqual(obj.null_boolean, False)
            self.assertEqual(obj.text, 'abc def ghi')
            self.assertEqual(obj.time, time(12, 0, 0))

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Set(self.model_fields['binary'], b'ABC'),
                Set(self.model_fields['boolean'], True),
                Set(self.model_fields['char'], 'ABC DEF'),
                Set(self.model_fields['date'], date(2014, 10, 17)),
                Set(self.model_fields['date_time'], datetime(2014, 10, 17, 8, 30, 30, tzinfo=UTC)),
                Set(self.model_fields['decimal'], Decimal('5.0')),
                Set(self.model_fields['float'], 5.0),
                Set(self.model_fields['integer'], 5),
                Set(self.model_fields['null_boolean'], True),
                Set(self.model_fields['text'], 'ABC DEF GHI'),
                Set(self.model_fields['time'], time(8, 30, 30)),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            #self.assertEqual(obj.binary, b'ABC')
            self.assertEqual(obj.boolean, True)
            self.assertEqual(obj.char, 'ABC DEF')
            self.assertEqual(obj.date, date(2014, 10, 17))
            self.assertEqual(obj.date_time, datetime(2014, 10, 17, 8, 30, 30, tzinfo=UTC))
            self.assertEqual(obj.decimal, Decimal('5.0'))
            self.assertEqual(obj.float, 5.0)
            self.assertEqual(obj.integer, 5)
            self.assertEqual(obj.null_boolean, True)
            self.assertEqual(obj.text, 'ABC DEF GHI')
            self.assertEqual(obj.time, time(8, 30, 30))

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                SetNull(self.model_fields['null_boolean']),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.null_boolean, None)

    def test_assignment_operations_in_bulk(self):
        for obj in MassUpdateModel.objects.all():
            #self.assertEqual(obj.binary, b'abc')
            self.assertEqual(obj.boolean, False)
            self.assertEqual(obj.char, 'abc def')
            self.assertEqual(obj.date, date(1986, 9, 25))
            self.assertEqual(obj.date_time, datetime(1986, 9, 25, 12, 0, 0, tzinfo=UTC))
            self.assertEqual(obj.decimal, Decimal('10.0'))
            self.assertEqual(obj.float, 10.0)
            self.assertEqual(obj.integer, 10)
            self.assertEqual(obj.null_boolean, False)
            self.assertEqual(obj.text, 'abc def ghi')
            self.assertEqual(obj.time, time(12, 0, 0))

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Set(self.model_fields['binary'], b'ABC'),
                Set(self.model_fields['boolean'], True),
                Set(self.model_fields['char'], 'ABC DEF'),
                Set(self.model_fields['date'], date(2014, 10, 17)),
                Set(self.model_fields['date_time'], datetime(2014, 10, 17, 8, 30, 30, tzinfo=UTC)),
                Set(self.model_fields['decimal'], Decimal('5.0')),
                Set(self.model_fields['float'], 5.0),
                Set(self.model_fields['integer'], 5),
                Set(self.model_fields['null_boolean'], True),
                Set(self.model_fields['text'], 'ABC DEF GHI'),
                Set(self.model_fields['time'], time(8, 30, 30)),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            #self.assertEqual(obj.binary, b'ABC')
            self.assertEqual(obj.boolean, True)
            self.assertEqual(obj.char, 'ABC DEF')
            self.assertEqual(obj.date, date(2014, 10, 17))
            self.assertEqual(obj.date_time, datetime(2014, 10, 17, 8, 30, 30, tzinfo=UTC))
            self.assertEqual(obj.decimal, Decimal('5.0'))
            self.assertEqual(obj.float, 5.0)
            self.assertEqual(obj.integer, 5)
            self.assertEqual(obj.null_boolean, True)
            self.assertEqual(obj.text, 'ABC DEF GHI')
            self.assertEqual(obj.time, time(8, 30, 30))

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                SetNull(self.model_fields['null_boolean']),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.null_boolean, None)

    def test_mathematical_operations(self):
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.decimal, Decimal('10.0'))
            self.assertEqual(obj.float, 10.0)
            self.assertEqual(obj.integer, 10)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Add(self.model_fields['decimal'], 5),
                Add(self.model_fields['float'], 5),
                Add(self.model_fields['integer'], 5),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.decimal, Decimal('15.0'))
            self.assertEqual(obj.float, 15.0)
            self.assertEqual(obj.integer, 15)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Sub(self.model_fields['decimal'], 5),
                Sub(self.model_fields['float'], 5),
                Sub(self.model_fields['integer'], 5),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.decimal, Decimal('10.0'))
            self.assertEqual(obj.float, 10.0)
            self.assertEqual(obj.integer, 10)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Mul(self.model_fields['decimal'], 2),
                Mul(self.model_fields['float'], 2),
                Mul(self.model_fields['integer'], 2),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.decimal, Decimal('20.0'))
            self.assertEqual(obj.float, 20.0)
            self.assertEqual(obj.integer, 20)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Div(self.model_fields['decimal'], 2),
                Div(self.model_fields['float'], 2),
                Div(self.model_fields['integer'], 2),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.decimal, Decimal('10.0'))
            self.assertEqual(obj.float, 10.0)
            self.assertEqual(obj.integer, 10)

    def test_mathematical_operations_in_bulk(self):
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.decimal, Decimal('10.0'))
            self.assertEqual(obj.float, 10.0)
            self.assertEqual(obj.integer, 10)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Add(self.model_fields['decimal'], 5),
                Add(self.model_fields['float'], 5),
                Add(self.model_fields['integer'], 5),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.decimal, Decimal('15.0'))
            self.assertEqual(obj.float, 15.0)
            self.assertEqual(obj.integer, 15)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Sub(self.model_fields['decimal'], 5),
                Sub(self.model_fields['float'], 5),
                Sub(self.model_fields['integer'], 5),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.decimal, Decimal('10.0'))
            self.assertEqual(obj.float, 10.0)
            self.assertEqual(obj.integer, 10)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Mul(self.model_fields['decimal'], 2),
                Mul(self.model_fields['float'], 2),
                Mul(self.model_fields['integer'], 2),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.decimal, Decimal('20.0'))
            self.assertEqual(obj.float, 20.0)
            self.assertEqual(obj.integer, 20)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Div(self.model_fields['decimal'], 2),
                Div(self.model_fields['float'], 2),
                Div(self.model_fields['integer'], 2),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.decimal, Decimal('10.0'))
            self.assertEqual(obj.float, 10.0)
            self.assertEqual(obj.integer, 10)

    def test_logical_operations(self):
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.boolean, False)
            self.assertEqual(obj.null_boolean, False)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Swap(self.model_fields['boolean']),
                Swap(self.model_fields['null_boolean']),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.boolean, True)
            self.assertEqual(obj.null_boolean, True)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Swap(self.model_fields['boolean']),
                Swap(self.model_fields['null_boolean']),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.boolean, False)
            self.assertEqual(obj.null_boolean, False)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Set(self.model_fields['null_boolean'], None),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.null_boolean, None)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Swap(self.model_fields['null_boolean']),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.null_boolean, None)

    def test_logical_operations_in_bulk(self):
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.boolean, False)
            self.assertEqual(obj.null_boolean, False)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Swap(self.model_fields['boolean']),
                Swap(self.model_fields['null_boolean']),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.boolean, True)
            self.assertEqual(obj.null_boolean, True)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Swap(self.model_fields['boolean']),
                Swap(self.model_fields['null_boolean']),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.boolean, False)
            self.assertEqual(obj.null_boolean, False)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Set(self.model_fields['null_boolean'], None),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.null_boolean, None)

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Swap(self.model_fields['null_boolean']),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.null_boolean, None)

    def test_string_operations(self):
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'abc def')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Upper(self.model_fields['char']),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'ABC DEF')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Lower(self.model_fields['char']),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'abc def')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Capitalize(self.model_fields['char']),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'Abc def')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Title(self.model_fields['char']),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'Abc Def')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                SwapCase(self.model_fields['char']),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'aBC dEF')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Set(self.model_fields['char'], '  abc def\t'),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, '  abc def\t')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Strip(self.model_fields['char']),
            ],
            in_bulk=False,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'abc def')

    def test_string_operations_in_bulk(self):
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'abc def')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Upper(self.model_fields['char']),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'ABC DEF')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Lower(self.model_fields['char']),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'abc def')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Capitalize(self.model_fields['char']),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'Abc def')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Title(self.model_fields['char']),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'Abc Def')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                SwapCase(self.model_fields['char']),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'aBC dEF')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Set(self.model_fields['char'], '  abc def\t'),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, '  abc def\t')

        self.model_admin.update_queryset(
            request=None,
            queryset=MassUpdateModel.objects.all(),
            ops=[
                Strip(self.model_fields['char']),
            ],
            in_bulk=True,
        )
        for obj in MassUpdateModel.objects.all():
            self.assertEqual(obj.char, 'abc def')

