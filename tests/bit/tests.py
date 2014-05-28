# -*- coding:utf-8 -*-

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django import test

from yepes.tests.bit.models import (
    BitTestModel as Model,
    FlagTestModel as FlagModel,
    LongBitTestModel as LongModel,
    RelatedBitTestModel as RelatedModel,
)
from yepes.types import Bit


class BitTest(test.SimpleTestCase):

    def test_int(self):
        bit = Bit(0)
        self.assertEqual(int(bit), 0)
        self.assertEqual(bool(bit), False)
        self.assertTrue(not bit)
        self.assertEqual(str(bit), '0')
        self.assertEqual(repr(bit), '<Bit: 0>')
        bit = Bit(0b1100)
        self.assertEqual(int(bit), 0b1100)
        self.assertEqual(bool(bit), True)
        self.assertFalse(not bit)
        self.assertEqual(str(bit), '1100')
        self.assertEqual(repr(bit), '<Bit: 1100>')

    def test_comparison(self):
        self.assertEqual(Bit(0), Bit(0))
        self.assertNotEquals(Bit(1), Bit(0))
        self.assertEqual(Bit(0), 0)
        self.assertNotEquals(Bit(1), 0)

    def test_and(self):
        self.assertEqual(1 & Bit(0), 0)
        self.assertEqual(1 & Bit(1), 1)
        self.assertEqual(0b0110 & Bit(0b1100), 0b0100)
        self.assertEqual(Bit(1) & Bit(0), 0)
        self.assertEqual(Bit(1) & Bit(1), 1)
        self.assertEqual(Bit(0b0110) & Bit(0b1100), 0b0100)

    def test_or(self):
        self.assertEqual(1 | Bit(0), 1)
        self.assertEqual(1 | Bit(1), 1)
        self.assertEqual(0b0110 | Bit(0b1100), 0b1110)
        self.assertEqual(Bit(1) | Bit(0), 1)
        self.assertEqual(Bit(1) | Bit(1), 1)
        self.assertEqual(Bit(0b0110) | Bit(0b1100), 0b1110)

    def test_xor(self):
        self.assertEqual(1 ^ Bit(0), 1)
        self.assertEqual(1 ^ Bit(1), 0)
        self.assertEqual(0b0110 ^ Bit(0b1100), 0b1010)
        self.assertEqual(Bit(1) ^ Bit(0), 1)
        self.assertEqual(Bit(1) ^ Bit(1), 0)
        self.assertEqual(Bit(0b0110) ^ Bit(0b1100), 0b1010)

    def test_invert(self):
        self.assertEqual(~Bit(1), 0)
        self.assertEqual(~Bit(0), 1)
        self.assertEqual(~Bit(0b100110), 0b011001)


class BitFieldTest(test.TestCase):

    def test_basic(self):
        instance = Model.objects.create(flags=0b0011)
        self.assertEqual(instance.flags, 0b0011)
        self.assertEqual(instance.flags, ['bin', 'dec'])
        self.assertEqual(instance.flags, Model.flags.bin | Model.flags.dec)
        self.assertEqual(instance.flags, [Model.flags.bin, Model.flags.dec])
        self.assertEqual(repr(instance.flags), '<Bit: 11>')
        self.assertEqual(str(instance.flags), 'Binario, Decimal')
        self.assertTrue(instance.flags.bin)
        self.assertTrue(instance.flags.dec)
        self.assertFalse(instance.flags.hex)
        self.assertFalse(instance.flags.oct)

        instance = Model.objects.create(flags='bin')
        self.assertEqual(instance.flags, 0b0001)
        self.assertEqual(instance.flags, 'bin')
        self.assertEqual(instance.flags, Model.flags.bin)
        self.assertEqual(repr(instance.flags), '<Bit: 1>')
        self.assertEqual(str(instance.flags), 'Binario')
        self.assertTrue(instance.flags.bin)
        self.assertFalse(instance.flags.dec)
        self.assertFalse(instance.flags.hex)
        self.assertFalse(instance.flags.oct)

        instance = Model.objects.create(flags=['bin', 'hex'])
        self.assertEqual(instance.flags, 0b0101)
        self.assertEqual(instance.flags, ['bin', 'hex'])
        self.assertEqual(instance.flags, Model.flags.bin | Model.flags.hex)
        self.assertEqual(instance.flags, [Model.flags.bin, Model.flags.hex])
        self.assertEqual(repr(instance.flags), '<Bit: 101>')
        self.assertEqual(str(instance.flags), 'Binario, Hexadecimal')
        self.assertTrue(instance.flags.bin)
        self.assertFalse(instance.flags.dec)
        self.assertTrue(instance.flags.hex)
        self.assertFalse(instance.flags.oct)

        instance = Model.objects.create(flags=Model.flags.oct)
        self.assertEqual(instance.flags, 0b1000)
        self.assertEqual(instance.flags, 'oct')
        self.assertEqual(instance.flags, Model.flags.oct)
        self.assertEqual(repr(instance.flags), '<Bit: 1000>')
        self.assertEqual(str(instance.flags), 'Octal')
        self.assertFalse(instance.flags.bin)
        self.assertFalse(instance.flags.dec)
        self.assertFalse(instance.flags.hex)
        self.assertTrue(instance.flags.oct)

        instance = Model.objects.create(flags=Model.flags.bin | Model.flags.dec)
        self.assertEqual(instance.flags, 0b0011)
        instance = Model.objects.create(flags=[Model.flags.bin, Model.flags.dec])
        self.assertEqual(instance.flags, 0b0011)

    def test_default_value(self):
        instance = Model.objects.create()
        self.assertEqual(instance.flags, 0b0011)
        self.assertEqual(instance.flags, Model.flags.bin | Model.flags.dec)
        self.assertTrue(instance.flags.bin)
        self.assertTrue(instance.flags.dec)
        self.assertFalse(instance.flags.hex)
        self.assertFalse(instance.flags.oct)

    def test_select(self):
        instance = Model.objects.create(flags='hex')
        self.assertFalse(Model.objects.filter(flags=Model.flags.bin).exists())
        self.assertFalse(Model.objects.filter(flags=Model.flags.dec).exists())
        self.assertTrue(Model.objects.filter(flags=Model.flags.hex).exists())
        self.assertFalse(Model.objects.filter(flags=Model.flags.oct).exists())
        self.assertTrue(Model.objects.exclude(flags=Model.flags.bin).exists())
        self.assertTrue(Model.objects.exclude(flags=Model.flags.dec).exists())
        self.assertFalse(Model.objects.exclude(flags=Model.flags.hex).exists())
        self.assertTrue(Model.objects.exclude(flags=Model.flags.oct).exists())
        instance.delete()

        instance = Model.objects.create(flags=~Model.flags.hex)
        self.assertTrue(Model.objects.filter(flags=Model.flags.bin).exists())
        self.assertTrue(Model.objects.filter(flags=Model.flags.dec).exists())
        self.assertFalse(Model.objects.filter(flags=Model.flags.hex).exists())
        self.assertTrue(Model.objects.filter(flags=Model.flags.oct).exists())
        self.assertFalse(Model.objects.exclude(flags=Model.flags.bin).exists())
        self.assertFalse(Model.objects.exclude(flags=Model.flags.dec).exists())
        self.assertTrue(Model.objects.exclude(flags=Model.flags.hex).exists())
        self.assertFalse(Model.objects.exclude(flags=Model.flags.oct).exists())
        instance.delete()

        Model.objects.create(flags=Model.flags.bin | Model.flags.dec)
        Model.objects.create(flags=Model.flags.dec)
        self.assertEqual(Model.objects.filter(flags=Model.flags.bin).count(), 1)
        self.assertEqual(Model.objects.filter(flags=Model.flags.dec).count(), 2)
        self.assertEqual(Model.objects.filter(flags=Model.flags.hex).count(), 0)
        self.assertEqual(Model.objects.filter(flags=Model.flags.oct).count(), 0)
        self.assertEqual(Model.objects.exclude(flags=Model.flags.bin).count(), 1)
        self.assertEqual(Model.objects.exclude(flags=Model.flags.dec).count(), 0)
        self.assertEqual(Model.objects.exclude(flags=Model.flags.hex).count(), 2)
        self.assertEqual(Model.objects.exclude(flags=Model.flags.oct).count(), 2)

        Model.objects.create(flags=Model.flags.oct)
        Model.objects.create(flags=~Model.flags.oct)
        values = [instance.flags for instance in Model.objects.all()]
        self.assertEqual(values, [
                Model.flags.bin | Model.flags.dec,
                Model.flags.dec,
                Model.flags.oct,
                ~Model.flags.oct,
            ])

    def test_serialization(self):
        instance = Model.objects.create(flags=0)
        data = pickle.dumps(instance)

        # ensure the flag is actually working
        self.assertFalse(instance.flags.bin)

        loaded = pickle.loads(data)
        self.assertFalse(instance.flags.bin)
        self.assertFalse(loaded.flags.bin)


class RelatedBitFieldTest(test.TestCase):

    def test_basic(self):
        self.assertEqual(tuple(RelatedModel.flags.iter_values()), ())
        self.assertEqual(tuple(RelatedModel.flags.iter_verbose_names()), ())
        self.assertEqual(RelatedModel.flags.get_max_value(), 0)

        past = FlagModel.objects.create(name='Past')
        present = FlagModel.objects.create(name='Present')
        future = FlagModel.objects.create(name='Future')
        self.assertEqual(
                tuple(RelatedModel.flags.iter_verbose_names()),
                ('Future', 'Past', 'Present'))
        self.assertEqual(
                tuple(RelatedModel.flags.iter_values()),
                (0b100, 0b001, 0b010))
        self.assertEqual(RelatedModel.flags.get_max_value(), 0b111)

        instance = RelatedModel.objects.create(flags=0b100)
        self.assertEqual(instance.flags, 0b100)
        self.assertEqual(instance.flags, future)
        self.assertEqual(repr(instance.flags), '<Bit: 100>')
        self.assertEqual(str(instance.flags), 'Future')

        instance = RelatedModel.objects.create(flags=0b011)
        self.assertEqual(instance.flags, 0b011)
        self.assertEqual(instance.flags, [past, present])
        self.assertEqual(repr(instance.flags), '<Bit: 11>')
        self.assertEqual(str(instance.flags), 'Past, Present')

        instance = RelatedModel.objects.create(flags=present)
        self.assertEqual(instance.flags, 0b010)
        self.assertEqual(instance.flags, present)
        self.assertEqual(repr(instance.flags), '<Bit: 10>')
        self.assertEqual(str(instance.flags), 'Present')

        instance = RelatedModel.objects.create(flags=[present, future])
        self.assertEqual(instance.flags, 0b110)
        self.assertEqual(instance.flags, [present, future])
        self.assertEqual(repr(instance.flags), '<Bit: 110>')
        self.assertEqual(str(instance.flags), 'Future, Present')

    def test_select(self):
        past = FlagModel.objects.create(name='Past')
        present = FlagModel.objects.create(name='Present')
        future = FlagModel.objects.create(name='Future')

        instance = RelatedModel.objects.create(flags=future)
        self.assertFalse(RelatedModel.objects.filter(flags=past).exists())
        self.assertFalse(RelatedModel.objects.filter(flags=present).exists())
        self.assertTrue(RelatedModel.objects.filter(flags=future).exists())
        self.assertTrue(RelatedModel.objects.exclude(flags=past).exists())
        self.assertTrue(RelatedModel.objects.exclude(flags=present).exists())
        self.assertFalse(RelatedModel.objects.exclude(flags=future).exists())
        instance.delete()

        RelatedModel.objects.create(flags=[past, present])
        RelatedModel.objects.create(flags=present)
        self.assertEqual(RelatedModel.objects.filter(flags=past).count(), 1)
        self.assertEqual(RelatedModel.objects.filter(flags=present).count(), 2)
        self.assertEqual(RelatedModel.objects.filter(flags=future).count(), 0)
        self.assertEqual(RelatedModel.objects.exclude(flags=past).count(), 1)
        self.assertEqual(RelatedModel.objects.exclude(flags=present).count(), 0)
        self.assertEqual(RelatedModel.objects.exclude(flags=future).count(), 2)

        RelatedModel.objects.create(flags=future)
        RelatedModel.objects.create(flags=[past, present, future])
        values = [instance.flags for instance in RelatedModel.objects.all()]
        self.assertEqual(values, [
                (past, present),
                present,
                future,
                (past, present, future),
            ])

    def test_serialization(self):
        past = FlagModel.objects.create(name='Past')
        present = FlagModel.objects.create(name='Present')
        future = FlagModel.objects.create(name='Future')

        instance = RelatedModel.objects.create(flags=[past, future])
        data = pickle.dumps(instance)

        # ensure the flag is actually working
        self.assertEqual(instance.flags, [past, future])

        loaded = pickle.loads(data)
        self.assertEqual(instance.flags, [past, future])
        self.assertEqual(loaded.flags, [past, future])


class LongBitFieldTest(test.TestCase):

    def test_int_fields(self):
        obj = LongModel.objects.create()
        self.assertEqual(obj.flags, 0)
        self.assertEqual(obj.flags_1, 0)
        self.assertEqual(obj.flags_2, 0)
        self.assertEqual(obj.flags_3, 0)
        with self.assertRaises(AttributeError):
            obj.flags_4
        self.assertEqual(obj.related_flags, 0)
        self.assertEqual(obj.related_flags_1, 0)
        self.assertEqual(obj.related_flags_2, 0)
        self.assertEqual(obj.related_flags_3, 0)
        with self.assertRaises(AttributeError):
            obj.related_flags_4

    def test_int_fields_values(self):
        value_1 = 9223372036854775808L    # 1 << 63
        value_2 = 2147483648L             # 1 << 31
        value_3 = 9223372039002259456L    # value_1 + value_2

        obj = LongModel()
        obj.flags = value_2
        obj.related_flags = value_3
        self.assertEqual(obj.flags_1, 2147483648L)
        self.assertEqual(obj.flags_2, 0L)
        self.assertEqual(obj.flags_3, 0L)
        self.assertEqual(int(obj.flags), 2147483648L)
        self.assertEqual(obj.related_flags_1, 2147483648L)
        self.assertEqual(obj.related_flags_2, 1L)
        self.assertEqual(obj.related_flags_3, 0L)
        self.assertEqual(int(obj.related_flags), 9223372039002259456L)

        obj = LongModel(flags=value_2, related_flags=value_3)
        self.assertEqual(obj.flags_1, 2147483648L)
        self.assertEqual(obj.flags_2, 0L)
        self.assertEqual(obj.flags_3, 0L)
        self.assertEqual(int(obj.flags), 2147483648L)
        self.assertEqual(obj.related_flags_1, 2147483648L)
        self.assertEqual(obj.related_flags_2, 1L)
        self.assertEqual(obj.related_flags_3, 0L)
        self.assertEqual(int(obj.related_flags), 9223372039002259456L)

        obj.save()
        obj = LongModel.objects.get()
        self.assertEqual(obj.flags_1, 2147483648L)
        self.assertEqual(obj.flags_2, 0L)
        self.assertEqual(obj.flags_3, 0L)
        self.assertEqual(int(obj.flags), 2147483648L)
        self.assertEqual(obj.related_flags_1, 2147483648L)
        self.assertEqual(obj.related_flags_2, 1L)
        self.assertEqual(obj.related_flags_3, 0L)
        self.assertEqual(int(obj.related_flags), 9223372039002259456L)

        obj.flags = value_3
        obj.related_flags = value_2
        self.assertEqual(obj.flags_1, 2147483648L)
        self.assertEqual(obj.flags_2, 1L)
        self.assertEqual(obj.flags_3, 0L)
        self.assertEqual(int(obj.flags), 9223372039002259456L)
        self.assertEqual(obj.related_flags_1, 2147483648L)
        self.assertEqual(obj.related_flags_2, 0L)
        self.assertEqual(obj.related_flags_3, 0L)
        self.assertEqual(int(obj.related_flags), 2147483648L)

    def test_lookup(self):
        value_1 = int('0b1'+'0'*63, 2)
        value_2 = int('0b1'+'0'*31, 2)
        value_3 = value_1 + value_2
        value_4 = 0
        obj = LongModel.objects.create(flags=value_2, related_flags=value_3)
        self.assertQuerysetEqual(
                LongModel.objects.filter(flags=value_1),
                [])
        self.assertQuerysetEqual(
                LongModel.objects.filter(related_flags=value_1),
                [repr(obj)])
        self.assertQuerysetEqual(
                LongModel.objects.filter(flags=value_2),
                [repr(obj)])
        self.assertQuerysetEqual(
                LongModel.objects.filter(related_flags=value_2),
                [repr(obj)])
        self.assertQuerysetEqual(
                LongModel.objects.filter(flags=value_3),
                [])
        self.assertQuerysetEqual(
                LongModel.objects.filter(related_flags=value_3),
                [repr(obj)])
        self.assertQuerysetEqual(
                LongModel.objects.filter(flags=value_4),
                [])
        self.assertQuerysetEqual(
                LongModel.objects.filter(related_flags=value_4),
                [])

