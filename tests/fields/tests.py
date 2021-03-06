# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals

from collections import Counter
from decimal import Decimal as dec
from unittest import skip
try:
    import cPickle as pickle
except ImportError:
    import pickle

from django import test
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import six

from yepes.contrib.registry import registry
from yepes.contrib.registry.fields import ModelChoiceField
from yepes.types import Bit, Formula

from .forms import (
    BitForm,
    BooleanForm,
    CachedForeignKeyForm,
    ColoredForm,
    CommaSeparatedForm,
    CompressedForm,
    DecimalForm,
    EmailForm,
    EncryptedForm,
    FlagForm,
    FloatForm,
    FormulaForm,
    GuidForm,
    IdentifierForm,
    IntegerForm,
    LongBitForm,
    PhoneNumberForm,
    PickledForm,
    PostalCodeForm,
    RelatedBitForm,
    RichTextForm,
    SlugForm,
    TextForm,
)
from .models import (
    BitModel,
    BooleanModel,
    CachedForeignKeyModel,
    CachedModel,
    CachedModelWithDefaultValue,
    CalculatedModel,
    ColoredModel,
    CommaSeparatedModel,
    CompressedModel,
    DecimalModel,
    EmailModel,
    EncryptedModel,
    FlagModel,
    FloatModel,
    FormulaModel,
    GuidModel,
    IdentifierModel,
    IntegerModel,
    LongBitModel,
    PhoneNumberModel,
    PickledModel,
    PostalCodeModel,
    RelatedBitModel,
    RichTextModel,
    SlugModel,
    TextModel,
)
from .models import CALCULATOR_CALLS


def skipUnlessMarkdown():
    try:
        try:
            import markdown2 as markdown
        except ImportError:
            import markdown
    except ImportError:
        return skip('Markdown could not be imported.')
    else:
        return (lambda func: func)


ascii_1 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.' \
          ' Vestibulum interdum diam felis. Quisque rutrum luctus nisl' \
          ' sit amet elementum. Aliquam porta est aliquet arcu elementum' \
          ' elementum. Nunc sed sapien felis. Suspendisse non leo eu' \
          ' metus mattis laoreet. Duis lacus purus, faucibus id suscipit' \
          ' nec, molestie ac elit. Duis dictum sapien quis sem volutpat' \
          ' fermentum. Ut vel ultricies orci.'
ascii_2 = 'Nunc cursus, mauris nec ornare sodales, lorem eros iaculis' \
          ' ligula, sed hendrerit libero purus eu nibh. Proin id' \
          ' eleifend dui. Quisque viverra quam in nunc volutpat' \
          ' convallis. Mauris convallis volutpat vulputate. Proin' \
          ' sodales neque quis sem fringilla ut lacinia sapien rutrum.' \
          ' Morbi vel elit erat, in dignissim felis. Aliquam erat' \
          ' volutpat. Nullam tristique, nisl non varius tristique, nisl' \
          ' magna posuere metus, et fermentum magna arcu a risus.'

french_1 = 'Quant à l’utilisation des accents sur les majuscules, il est' \
           ' malheureusement manifeste que l’usage est flottant. On observe' \
           ' dans les textes manuscrits une tendance certaine à l’omission' \
           ' des accents. Il en va de même dans les textes dactylographiés,' \
           ' en raison notamment des possibilités limitées qu’offrent les' \
           ' machines traditionnelles. En typographie, enfin, certains' \
           ' suppriment tous les accents sur les capitales sous prétexte de' \
           ' modernisme, en fait pour réduire les frais de composition.'
french_2 = 'Il convient cependant d’observer qu’en français, l’accent a' \
           ' pleine valeur orthographique. Son absence ralentit la lecture,' \
           ' fait hésiter sur la prononciation, et peut même induire en' \
           ' erreur. On veille donc, en bonne typographie, à utiliser' \
           ' systématiquement les capitales accentuées, y compris dans la' \
           ' préposition À, comme le font bien sûr tous les dictionnaires,' \
           ' à commencer par le Dictionnaire de l’Académie française ou' \
           ' les grammaires comme le Bon usage de Grevisse, mais aussi' \
           ' l’Imprimerie nationale, la Bibliothèque de la Pléiade, etc.'

greek_1 = 'Ο Πρόεδρος της Δημοκρατίας κ. Κάρολος Παπούλιας απέστειλε' \
          '  συλλυπητήριο τηλεγράφημα στον Πρόεδρο της Δημοκρατίας της' \
          '  Τουρκίας κ. Αμπντουλάχ Γκιούλ εκφράζοντας εκ μέρους του' \
          '  ελληνικού λαού τα ειλικρινή του συλλυπητήρια και τη βαθύτατη' \
          '  συμπάθεια στις οικογένειες των θυμάτων, καθώς και τις από' \
          '  καρδιάς ευχές για τη διάσωση των επιζώντων από την έκρηξη στο' \
          '  ανθρακωρυχείο.'
greek_2 = 'Υπάρχουν κάποιες συνεργασίες με ξένους, αλλά ουσιαστικά το' \
          ' κατασκευαστικό έργο είναι απολύτως ελληνικό και έχουν ισχυρό' \
          ' κnow-how,  έχουν εμπειρία.  Και ταυτόχρονα και παράλληλα με' \
          ' την Ολυμπία Οδό, μεταξύ Κορίνθου και Πάτρας γίνεται και η' \
          ' σιδηροδρομική γραμμή.  Να σας πω χαρακτηριστικά ότι στο τμήμα' \
          ' από την Κόρινθο-Πάτρα-Γιάννενα, μαζί με τη σιδηροδρομική γραμμή,' \
          ' εκτελούνται έργα της τάξεως  των 3,5 δις ευρώ.'

spanish_1 = 'El veloz murciélago hindú comía feliz cardillo y kiwi.'
spanish_2 = 'La cigüeña tocaba el saxofón detrás del palenque de paja.'


class BitFieldTest(test.TestCase):

    def test_basic(self):
        record = BitModel.objects.create(flags=0b0011)
        self.assertEqual(
            record.flags,
            0b0011,
        )
        self.assertEqual(
            record.flags,
            ['bin', 'dec'],
        )
        self.assertEqual(
            record.flags,
            BitModel.flags.bin | BitModel.flags.dec,
        )
        self.assertEqual(
            record.flags,
            [BitModel.flags.bin, BitModel.flags.dec],
        )
        self.assertEqual(
            repr(record.flags),
            '<Bit: 11>',
        )
        self.assertEqual(
            str(record.flags),
            'Binario, Decimal',
        )
        self.assertTrue(record.flags.bin)
        self.assertTrue(record.flags.dec)
        self.assertFalse(record.flags.hex)
        self.assertFalse(record.flags.oct)

        record = BitModel.objects.create(flags='bin')
        self.assertEqual(
            record.flags,
            0b0001,
        )
        self.assertEqual(
            record.flags,
            'bin',
        )
        self.assertEqual(
            record.flags,
            BitModel.flags.bin,
        )
        self.assertEqual(
            repr(record.flags),
            '<Bit: 1>',
        )
        self.assertEqual(
            str(record.flags),
            'Binario',
        )
        self.assertTrue(record.flags.bin)
        self.assertFalse(record.flags.dec)
        self.assertFalse(record.flags.hex)
        self.assertFalse(record.flags.oct)

        record = BitModel.objects.create(flags=['bin', 'hex'])
        self.assertEqual(
            record.flags,
            0b0101,
        )
        self.assertEqual(
            record.flags,
            ['bin', 'hex'],
        )
        self.assertEqual(
            record.flags,
            BitModel.flags.bin | BitModel.flags.hex,
        )
        self.assertEqual(
            record.flags,
            [BitModel.flags.bin, BitModel.flags.hex],
        )
        self.assertEqual(
            repr(record.flags),
            '<Bit: 101>',
        )
        self.assertEqual(
            str(record.flags),
            'Binario, Hexadecimal',
        )
        self.assertTrue(record.flags.bin)
        self.assertFalse(record.flags.dec)
        self.assertTrue(record.flags.hex)
        self.assertFalse(record.flags.oct)

        record = BitModel.objects.create(flags=BitModel.flags.oct)
        self.assertEqual(
            record.flags,
            0b1000,
        )
        self.assertEqual(
            record.flags,
            'oct',
        )
        self.assertEqual(
            record.flags,
            BitModel.flags.oct,
        )
        self.assertEqual(
            repr(record.flags),
            '<Bit: 1000>',
        )
        self.assertEqual(
            str(record.flags),
            'Octal',
        )
        self.assertFalse(record.flags.bin)
        self.assertFalse(record.flags.dec)
        self.assertFalse(record.flags.hex)
        self.assertTrue(record.flags.oct)

        record = BitModel.objects.create(flags=BitModel.flags.bin | BitModel.flags.dec)
        self.assertEqual(
            record.flags,
            0b0011,
        )
        record = BitModel.objects.create(flags=[BitModel.flags.bin, BitModel.flags.dec])
        self.assertEqual(
            record.flags,
            0b0011,
        )

    def test_default_value(self):
        record = BitModel.objects.create()
        self.assertEqual(
            record.flags,
            0b0011,
        )
        self.assertEqual(
            record.flags,
            BitModel.flags.bin | BitModel.flags.dec,
        )
        self.assertTrue(record.flags.bin)
        self.assertTrue(record.flags.dec)
        self.assertFalse(record.flags.hex)
        self.assertFalse(record.flags.oct)

    def test_value_assignment(self):
        record = BitModel.objects.create(flags=0b0011)
        self.assertTrue(record.flags.bin)
        self.assertIsInstance(record.flags.bin, bool)
        self.assertTrue(record.flags.dec)
        self.assertIsInstance(record.flags.dec, bool)
        self.assertFalse(record.flags.hex)
        self.assertIsInstance(record.flags.hex, bool)
        self.assertFalse(record.flags.oct)
        self.assertIsInstance(record.flags.oct, bool)

        value = record.flags
        value.oct = True
        self.assertTrue(value.bin)
        self.assertTrue(value.dec)
        self.assertFalse(value.hex)
        self.assertTrue(value.oct)

        value.oct = False
        self.assertTrue(value.bin)
        self.assertTrue(value.dec)
        self.assertFalse(value.hex)
        self.assertFalse(value.oct)

        value.hex = False
        self.assertTrue(value.bin)
        self.assertTrue(value.dec)
        self.assertFalse(value.hex)
        self.assertFalse(value.oct)

        record.flags.oct = True
        self.assertTrue(record.flags.bin)
        self.assertTrue(record.flags.dec)
        self.assertFalse(record.flags.hex)
        self.assertTrue(record.flags.oct)

        record.flags.oct = False
        self.assertTrue(record.flags.bin)
        self.assertTrue(record.flags.dec)
        self.assertFalse(record.flags.hex)
        self.assertFalse(record.flags.oct)

        record.flags.hex = False
        self.assertTrue(record.flags.bin)
        self.assertTrue(record.flags.dec)
        self.assertFalse(record.flags.hex)
        self.assertFalse(record.flags.oct)

        record.flags.bin = True
        self.assertTrue(record.flags.bin)
        self.assertTrue(record.flags.dec)
        self.assertFalse(record.flags.hex)
        self.assertFalse(record.flags.oct)

    def test_field_clean(self):
        record = BitModel.objects.create(flags=0b0011)
        self.assertEqual(record.flags, 0b0011)
        self.assertEqual(record.flags, 3)
        self.assertIsInstance(record.flags, Bit)

        self.assertTrue(record.flags.bin)
        self.assertIsInstance(record.flags.bin, bool)
        self.assertTrue(record.flags.dec)
        self.assertIsInstance(record.flags.dec, bool)
        self.assertFalse(record.flags.hex)
        self.assertIsInstance(record.flags.hex, bool)
        self.assertFalse(record.flags.oct)
        self.assertIsInstance(record.flags.oct, bool)

        record.clean_fields()
        self.assertEqual(record.flags, 0b0011)
        self.assertEqual(record.flags, 3)
        self.assertIsInstance(record.flags, Bit)

        self.assertTrue(record.flags.bin)
        self.assertIsInstance(record.flags.bin, bool)
        self.assertTrue(record.flags.dec)
        self.assertIsInstance(record.flags.dec, bool)
        self.assertFalse(record.flags.hex)
        self.assertIsInstance(record.flags.hex, bool)
        self.assertFalse(record.flags.oct)
        self.assertIsInstance(record.flags.oct, bool)

    def test_select(self):
        record = BitModel.objects.create(flags='hex')
        self.assertFalse(BitModel.objects.filter(flags=BitModel.flags.bin).exists())
        self.assertFalse(BitModel.objects.filter(flags=BitModel.flags.dec).exists())
        self.assertTrue(BitModel.objects.filter(flags=BitModel.flags.hex).exists())
        self.assertFalse(BitModel.objects.filter(flags=BitModel.flags.oct).exists())
        self.assertTrue(BitModel.objects.exclude(flags=BitModel.flags.bin).exists())
        self.assertTrue(BitModel.objects.exclude(flags=BitModel.flags.dec).exists())
        self.assertFalse(BitModel.objects.exclude(flags=BitModel.flags.hex).exists())
        self.assertTrue(BitModel.objects.exclude(flags=BitModel.flags.oct).exists())
        record.delete()

        record = BitModel.objects.create(flags=~BitModel.flags.hex)
        self.assertTrue(BitModel.objects.filter(flags=BitModel.flags.bin).exists())
        self.assertTrue(BitModel.objects.filter(flags=BitModel.flags.dec).exists())
        self.assertFalse(BitModel.objects.filter(flags=BitModel.flags.hex).exists())
        self.assertTrue(BitModel.objects.filter(flags=BitModel.flags.oct).exists())
        self.assertFalse(BitModel.objects.exclude(flags=BitModel.flags.bin).exists())
        self.assertFalse(BitModel.objects.exclude(flags=BitModel.flags.dec).exists())
        self.assertTrue(BitModel.objects.exclude(flags=BitModel.flags.hex).exists())
        self.assertFalse(BitModel.objects.exclude(flags=BitModel.flags.oct).exists())
        record.delete()

        BitModel.objects.create(flags=BitModel.flags.bin | BitModel.flags.dec)
        BitModel.objects.create(flags=BitModel.flags.dec)
        self.assertEqual(BitModel.objects.filter(flags=BitModel.flags.bin).count(), 1)
        self.assertEqual(BitModel.objects.filter(flags=BitModel.flags.dec).count(), 2)
        self.assertEqual(BitModel.objects.filter(flags=BitModel.flags.hex).count(), 0)
        self.assertEqual(BitModel.objects.filter(flags=BitModel.flags.oct).count(), 0)
        self.assertEqual(BitModel.objects.exclude(flags=BitModel.flags.bin).count(), 1)
        self.assertEqual(BitModel.objects.exclude(flags=BitModel.flags.dec).count(), 0)
        self.assertEqual(BitModel.objects.exclude(flags=BitModel.flags.hex).count(), 2)
        self.assertEqual(BitModel.objects.exclude(flags=BitModel.flags.oct).count(), 2)

        BitModel.objects.create(flags=BitModel.flags.oct)
        BitModel.objects.create(flags=~BitModel.flags.oct)
        self.assertEqual(
            [
                record.flags
                for record
                in BitModel.objects.all()
            ],
            [
                BitModel.flags.bin | BitModel.flags.dec,
                BitModel.flags.dec,
                BitModel.flags.oct,
                ~BitModel.flags.oct,
            ],
        )

    def test_serialization(self):
        record = BitModel.objects.create(flags=0)
        data = pickle.dumps(record)

        # ensure the flag is actually working
        self.assertFalse(record.flags.bin)

        loaded = pickle.loads(data)
        self.assertFalse(record.flags.bin)
        self.assertFalse(loaded.flags.bin)


class RelatedBitFieldTest(test.TestCase):

    def test_basic(self):
        self.assertEqual(
            list(RelatedBitModel.flags.iter_values()),
            [],
        )
        self.assertEqual(
            list(RelatedBitModel.flags.iter_verbose_names()),
            [],
        )
        self.assertEqual(
            RelatedBitModel.flags.get_max_value(),
            0,
        )
        past = FlagModel.objects.create(name='Past')
        present = FlagModel.objects.create(name='Present')
        future = FlagModel.objects.create(name='Future')
        RelatedBitModel.flags.reset()
        self.assertEqual(
            list(RelatedBitModel.flags.iter_values()),
            [0b100, 0b001, 0b010],
        )
        self.assertEqual(
            list(RelatedBitModel.flags.iter_verbose_names()),
            ['Future', 'Past', 'Present'],
        )
        self.assertEqual(
            RelatedBitModel.flags.get_max_value(),
            0b111,
        )
        record = RelatedBitModel.objects.create(flags=0b100)
        self.assertEqual(record.flags, 0b100)
        self.assertEqual(record.flags, future)
        self.assertEqual(repr(record.flags), '<Bit: 100>')
        self.assertEqual(str(record.flags), 'Future')

        record = RelatedBitModel.objects.create(flags=0b011)
        self.assertEqual(record.flags, 0b011)
        self.assertEqual(record.flags, [past, present])
        self.assertEqual(repr(record.flags), '<Bit: 11>')
        self.assertEqual(str(record.flags), 'Past, Present')

        record = RelatedBitModel.objects.create(flags=present)
        self.assertEqual(record.flags, 0b010)
        self.assertEqual(record.flags, present)
        self.assertEqual(repr(record.flags), '<Bit: 10>')
        self.assertEqual(str(record.flags), 'Present')

        record = RelatedBitModel.objects.create(flags=[present, future])
        self.assertEqual(record.flags, 0b110)
        self.assertEqual(record.flags, [present, future])
        self.assertEqual(repr(record.flags), '<Bit: 110>')
        self.assertEqual(str(record.flags), 'Future, Present')

    def test_select(self):
        past = FlagModel.objects.create(name='Past')
        present = FlagModel.objects.create(name='Present')
        future = FlagModel.objects.create(name='Future')

        record = RelatedBitModel.objects.create(flags=future)
        self.assertFalse(RelatedBitModel.objects.filter(flags=past).exists())
        self.assertFalse(RelatedBitModel.objects.filter(flags=present).exists())
        self.assertTrue(RelatedBitModel.objects.filter(flags=future).exists())
        self.assertTrue(RelatedBitModel.objects.exclude(flags=past).exists())
        self.assertTrue(RelatedBitModel.objects.exclude(flags=present).exists())
        self.assertFalse(RelatedBitModel.objects.exclude(flags=future).exists())
        record.delete()

        RelatedBitModel.objects.create(flags=[past, present])
        RelatedBitModel.objects.create(flags=present)
        self.assertEqual(RelatedBitModel.objects.filter(flags=past).count(), 1)
        self.assertEqual(RelatedBitModel.objects.filter(flags=present).count(), 2)
        self.assertEqual(RelatedBitModel.objects.filter(flags=future).count(), 0)
        self.assertEqual(RelatedBitModel.objects.exclude(flags=past).count(), 1)
        self.assertEqual(RelatedBitModel.objects.exclude(flags=present).count(), 0)
        self.assertEqual(RelatedBitModel.objects.exclude(flags=future).count(), 2)

        RelatedBitModel.objects.create(flags=future)
        RelatedBitModel.objects.create(flags=[past, present, future])
        self.assertEqual(
            [
                record.flags
                for record
                in RelatedBitModel.objects.all()
            ],
            [
                (past, present),
                present,
                future,
                (past, present, future),
            ],
        )

    def test_serialization(self):
        past = FlagModel.objects.create(name='Past')
        present = FlagModel.objects.create(name='Present')
        future = FlagModel.objects.create(name='Future')

        record = RelatedBitModel.objects.create(flags=[past, future])
        data = pickle.dumps(record)

        # ensure the flag is actually working
        self.assertEqual(record.flags, [past, future])

        loaded = pickle.loads(data)
        self.assertEqual(record.flags, [past, future])
        self.assertEqual(loaded.flags, [past, future])


class LongBitFieldTest(test.TestCase):

    def test_int_fields(self):
        obj = LongBitModel.objects.create()

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
        value_1 = Bit(9223372036854775808)    # 1 << 63
        value_2 = Bit(2147483648)             # 1 << 31
        value_3 = Bit(9223372039002259456)    # value_1 + value_2

        obj = LongBitModel()
        obj.flags = value_2
        obj.related_flags = value_3
        self.assertEqual(obj.flags_1, 2147483648)
        self.assertEqual(obj.flags_2, 0)
        self.assertEqual(obj.flags_3, 0)
        self.assertEqual(int(obj.flags), 2147483648)
        self.assertEqual(obj.related_flags_1, 2147483648)
        self.assertEqual(obj.related_flags_2, 1)
        self.assertEqual(obj.related_flags_3, 0)
        self.assertEqual(int(obj.related_flags), 9223372039002259456)

        obj = LongBitModel(flags=value_2, related_flags=value_3)
        self.assertEqual(obj.flags_1, 2147483648)
        self.assertEqual(obj.flags_2, 0)
        self.assertEqual(obj.flags_3, 0)
        self.assertEqual(int(obj.flags), 2147483648)
        self.assertEqual(obj.related_flags_1, 2147483648)
        self.assertEqual(obj.related_flags_2, 1)
        self.assertEqual(obj.related_flags_3, 0)
        self.assertEqual(int(obj.related_flags), 9223372039002259456)

        obj.save()
        obj = LongBitModel.objects.get()
        self.assertEqual(obj.flags_1, 2147483648)
        self.assertEqual(obj.flags_2, 0)
        self.assertEqual(obj.flags_3, 0)
        self.assertEqual(int(obj.flags), 2147483648)
        self.assertEqual(obj.related_flags_1, 2147483648)
        self.assertEqual(obj.related_flags_2, 1)
        self.assertEqual(obj.related_flags_3, 0)
        self.assertEqual(int(obj.related_flags), 9223372039002259456)

        obj.flags = value_3
        obj.related_flags = value_2
        self.assertEqual(obj.flags_1, 2147483648)
        self.assertEqual(obj.flags_2, 1)
        self.assertEqual(obj.flags_3, 0)
        self.assertEqual(int(obj.flags), 9223372039002259456)
        self.assertEqual(obj.related_flags_1, 2147483648)
        self.assertEqual(obj.related_flags_2, 0)
        self.assertEqual(obj.related_flags_3, 0)
        self.assertEqual(int(obj.related_flags), 2147483648)

    def test_lookup(self):
        value_1 = Bit(int('0b1'+'0'*63, 2))
        value_2 = Bit(int('0b1'+'0'*31, 2))
        value_3 = value_1 | value_2
        value_4 = 0
        obj = LongBitModel.objects.create(
            flags=value_2,
            related_flags=value_3,
        )
        self.assertQuerysetEqual(
            LongBitModel.objects.filter(flags=value_1),
            [],
        )
        self.assertQuerysetEqual(
            LongBitModel.objects.filter(related_flags=value_1),
            [repr(obj)],
        )
        self.assertQuerysetEqual(
            LongBitModel.objects.filter(flags=value_2),
            [repr(obj)],
        )
        self.assertQuerysetEqual(
            LongBitModel.objects.filter(related_flags=value_2),
            [repr(obj)],
        )
        self.assertQuerysetEqual(
            LongBitModel.objects.filter(flags=value_3),
            [],
        )
        self.assertQuerysetEqual(
            LongBitModel.objects.filter(related_flags=value_3),
            [repr(obj)],
        )
        self.assertQuerysetEqual(
            LongBitModel.objects.filter(flags=value_4),
            [],
        )
        self.assertQuerysetEqual(
            LongBitModel.objects.filter(related_flags=value_4),
            [],
        )


class CachedForeignKeyTest(test.TestCase):

    def test_custom_value(self):
        value_1 = CachedModel.objects.create()
        value_1 = CachedModel.cache.get(value_1.pk)

        value_2 = CachedModelWithDefaultValue.objects.create()
        value_2 = CachedModelWithDefaultValue.cache.get(value_2.pk)

        record_1 = CachedForeignKeyModel.objects.create(
            mandatory_key=value_1,
            optional_key=value_1,
            mandatory_key_with_default_value=value_2,
            optional_key_with_default_value=value_2,
        )
        self.assertEqual(
            record_1.mandatory_key.pk,
            value_1.pk,
        )
        self.assertIs(
            record_1.mandatory_key,
            value_1,
        )
        self.assertEqual(
            record_1.optional_key.pk,
            value_1.pk,
        )
        self.assertIs(
            record_1.optional_key,
            value_1,
        )
        self.assertEqual(
            record_1.mandatory_key_with_default_value.pk,
            value_2.pk,
        )
        self.assertIs(
            record_1.mandatory_key_with_default_value,
            value_2,
        )
        self.assertEqual(
            record_1.optional_key_with_default_value.pk,
            value_2.pk,
        )
        self.assertIs(
            record_1.optional_key_with_default_value,
            value_2,
        )

        record_2 = CachedForeignKeyModel.objects.get(pk=record_1.pk)
        self.assertEqual(
            record_2.mandatory_key.pk,
            value_1.pk,
        )
        self.assertIs(
            record_2.mandatory_key,
            value_1,
        )
        self.assertEqual(
            record_2.optional_key.pk,
            value_1.pk,
        )
        self.assertIs(
            record_2.optional_key,
            value_1,
        )
        self.assertEqual(
            record_2.mandatory_key_with_default_value.pk,
            value_2.pk,
        )
        self.assertIs(
            record_2.mandatory_key_with_default_value,
            value_2,
        )
        self.assertEqual(
            record_2.optional_key_with_default_value.pk,
            value_2.pk,
        )
        self.assertIs(
            record_2.optional_key_with_default_value,
            value_2,
        )

    def test_default_value(self):
        default = CachedModelWithDefaultValue.objects.create()
        default = CachedModelWithDefaultValue.cache.get(default.pk)
        registry.register(
            'tests:DEFAULT_CACHED_MODEL',
            ModelChoiceField(
                label = 'Default Cached Model',
                model = 'fields_tests.CachedModelWithDefaultValue',
                required = True,
        ))
        registry['tests:DEFAULT_CACHED_MODEL'] = default

        record_1 = CachedForeignKeyModel()
        with self.assertRaises(ObjectDoesNotExist):
            record_1.mandatory_key

        self.assertIsNone(record_1.optional_key)
        self.assertEqual(
            record_1.mandatory_key_with_default_value.pk,
            default.pk,
        )
        self.assertIs(
            record_1.mandatory_key_with_default_value,
            default,
        )
        self.assertIsNone(record_1.optional_key_with_default_value)

        custom = CachedModel.objects.create()
        custom = CachedModel.cache.get(custom.pk)
        record_2 = CachedForeignKeyModel.objects.create(
            mandatory_key=custom,
        )
        self.assertEqual(
            record_2.mandatory_key.pk,
            custom.pk,
        )
        self.assertIs(
            record_2.mandatory_key,
            custom,
        )
        self.assertIsNone(record_2.optional_key)
        self.assertEqual(
            record_2.mandatory_key_with_default_value.pk,
            default.pk,
        )
        self.assertIs(
            record_2.mandatory_key_with_default_value,
            default,
        )
        self.assertIsNone(record_2.optional_key_with_default_value)


class CalculatedFieldTest(test.TestCase):

    def test_descriptor(self):
        record_1 = CalculatedModel()
        record_1.pk = 0
        self.assertEqual(
            record_1.boolean,
            bool(record_1.pk % 2 == 0),
        )
        self.assertEqual(
            record_1.char,
            'even' if record_1.pk % 2 == 0 else 'odd',
        )
        self.assertEqual(
            record_1.decimal,
            dec('{0:.4}'.format(record_1.pk / 7)),
        )
        self.assertEqual(
            record_1.float,
            float(record_1.pk / 7),
        )
        self.assertEqual(
            record_1.integer,
            int(record_1.pk // 7),
        )
        self.assertEqual(
            record_1.null_boolean,
            bool(record_1.pk % 2 == 0),
        )
        self.assertEqual(
            record_1.pickled_object,
            dec('{0:.4}'.format(record_1.pk / 7)).as_tuple(),
        )
        record_2 = CalculatedModel.objects.create(pk=1)
        self.assertEqual(
            record_2.boolean,
            bool(record_2.pk % 2 == 0),
        )
        self.assertEqual(
            record_2.char,
            'even' if record_2.pk % 2 == 0 else 'odd',
        )
        self.assertEqual(
            record_2.decimal,
            dec('{0:.4}'.format(record_2.pk / 7)),
        )
        self.assertEqual(
            record_2.float,
            float(record_2.pk / 7),
        )
        self.assertEqual(
            record_2.integer,
            int(record_2.pk // 7),
        )
        self.assertEqual(
            record_2.null_boolean,
            bool(record_2.pk % 2 == 0),
        )
        self.assertEqual(
            record_2.pickled_object,
            dec('{0:.4}'.format(record_2.pk / 7)).as_tuple(),
        )

    def test_saved_values(self):
        manager = CalculatedModel.objects
        record = manager.create(pk=1)
        self.assertEqual(record.boolean, False)
        self.assertTrue(manager.filter(boolean=False).exists())
        self.assertEqual(record.char, 'odd')
        self.assertTrue(manager.filter(char='odd').exists())
        self.assertEqual(record.decimal, dec('0.1429'))
        self.assertTrue(manager.filter(decimal=dec('0.1429')).exists())
        self.assertEqual(record.float, 0.14285714285714285)
        self.assertTrue(manager.filter(float=0.14285714285714285).exists())
        self.assertEqual(record.integer, 0)
        self.assertTrue(manager.filter(integer=0).exists())
        self.assertEqual(record.null_boolean, False)
        self.assertTrue(manager.filter(null_boolean=False).exists())
        self.assertEqual(record.pickled_object, dec('0.1429').as_tuple())
        self.assertTrue(manager.filter(pickled_object=dec('0.1429').as_tuple()).exists())

    def test_calculator_calls(self):
        CALCULATOR_CALLS.clear()
        record_1 = CalculatedModel(pk=1)
        self.assertEqual(len(CALCULATOR_CALLS), 0)
        self.assertEqual(record_1.boolean, False)
        self.assertEqual(len(CALCULATOR_CALLS), 1)
        self.assertEqual(CALCULATOR_CALLS['boolean'], 1)
        self.assertEqual(record_1.boolean, False)
        self.assertEqual(record_1.boolean, False)
        self.assertEqual(record_1.boolean, False)
        self.assertEqual(len(CALCULATOR_CALLS), 1)
        self.assertEqual(CALCULATOR_CALLS['boolean'], 1)
        self.assertEqual(record_1.char, 'odd')
        self.assertEqual(len(CALCULATOR_CALLS), 2)
        self.assertEqual(CALCULATOR_CALLS['char'], 1)
        self.assertEqual(record_1.char, 'odd')
        self.assertEqual(record_1.char, 'odd')
        self.assertEqual(record_1.char, 'odd')
        self.assertEqual(len(CALCULATOR_CALLS), 2)
        self.assertEqual(CALCULATOR_CALLS['char'], 1)
        self.assertEqual(record_1.decimal, dec('0.1429'))
        self.assertEqual(len(CALCULATOR_CALLS), 3)
        self.assertEqual(CALCULATOR_CALLS['decimal'], 1)
        self.assertEqual(record_1.decimal, dec('0.1429'))
        self.assertEqual(record_1.decimal, dec('0.1429'))
        self.assertEqual(record_1.decimal, dec('0.1429'))
        self.assertEqual(len(CALCULATOR_CALLS), 3)
        self.assertEqual(CALCULATOR_CALLS['decimal'], 1)
        self.assertEqual(record_1.float, 0.14285714285714285)
        self.assertEqual(len(CALCULATOR_CALLS), 4)
        self.assertEqual(CALCULATOR_CALLS['float'], 1)
        self.assertEqual(record_1.float, 0.14285714285714285)
        self.assertEqual(record_1.float, 0.14285714285714285)
        self.assertEqual(record_1.float, 0.14285714285714285)
        self.assertEqual(len(CALCULATOR_CALLS), 4)
        self.assertEqual(CALCULATOR_CALLS['float'], 1)
        self.assertEqual(record_1.integer, 0)
        self.assertEqual(len(CALCULATOR_CALLS), 5)
        self.assertEqual(CALCULATOR_CALLS['integer'], 1)
        self.assertEqual(record_1.integer, 0)
        self.assertEqual(record_1.integer, 0)
        self.assertEqual(record_1.integer, 0)
        self.assertEqual(len(CALCULATOR_CALLS), 5)
        self.assertEqual(CALCULATOR_CALLS['integer'], 1)
        self.assertEqual(record_1.null_boolean, False)
        self.assertEqual(len(CALCULATOR_CALLS), 6)
        self.assertEqual(CALCULATOR_CALLS['null_boolean'], 1)
        self.assertEqual(record_1.null_boolean, False)
        self.assertEqual(record_1.null_boolean, False)
        self.assertEqual(record_1.null_boolean, False)
        self.assertEqual(len(CALCULATOR_CALLS), 6)
        self.assertEqual(CALCULATOR_CALLS['null_boolean'], 1)
        self.assertEqual(record_1.pickled_object, dec('0.1429').as_tuple())
        self.assertEqual(record_1.pickled_object.exponent, -4)
        self.assertEqual(len(CALCULATOR_CALLS), 7)
        self.assertEqual(CALCULATOR_CALLS['pickled_object'], 1)
        self.assertEqual(record_1.pickled_object, dec('0.1429').as_tuple())
        self.assertEqual(record_1.pickled_object.exponent, -4)
        self.assertEqual(record_1.pickled_object, dec('0.1429').as_tuple())
        self.assertEqual(record_1.pickled_object.exponent, -4)
        self.assertEqual(record_1.pickled_object, dec('0.1429').as_tuple())
        self.assertEqual(record_1.pickled_object.exponent, -4)
        self.assertEqual(len(CALCULATOR_CALLS), 7)
        self.assertEqual(CALCULATOR_CALLS['pickled_object'], 1)
        record_1.save()
        self.assertEqual(len(CALCULATOR_CALLS), 7)
        self.assertEqual(CALCULATOR_CALLS['boolean'], 2)
        self.assertEqual(CALCULATOR_CALLS['char'], 2)
        self.assertEqual(CALCULATOR_CALLS['decimal'], 2)
        self.assertEqual(CALCULATOR_CALLS['float'], 2)
        self.assertEqual(CALCULATOR_CALLS['integer'], 2)
        self.assertEqual(CALCULATOR_CALLS['null_boolean'], 2)
        self.assertEqual(CALCULATOR_CALLS['pickled_object'], 2)
        CALCULATOR_CALLS.clear()
        record_2 = CalculatedModel.objects.get(pk=1)
        self.assertEqual(len(CALCULATOR_CALLS), 0)
        self.assertEqual(record_2.boolean, False)
        self.assertEqual(record_2.char, 'odd')
        self.assertEqual(record_2.decimal, dec('0.1429'))
        self.assertEqual(record_2.float, 0.14285714285714285)
        self.assertEqual(record_2.integer, 0)
        self.assertEqual(record_2.null_boolean, False)
        self.assertEqual(record_2.pickled_object, dec('0.1429').as_tuple())
        self.assertEqual(record_2.pickled_object.exponent, -4)
        self.assertEqual(len(CALCULATOR_CALLS), 0)


class CharFieldTest(test.TestCase):

    def test_cleaning(self):
        record = SlugModel(title='\tLorem  Ipsum\nDolor ')
        record.full_clean()
        self.assertEqual(
            record.title,
            'Lorem Ipsum Dolor',
        )


class ColorFieldTest(test.TestCase):

    def test_cleaning(self):
        record = ColoredModel()
        record.color = 'red'
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.color = '#5DC1B9'
        record.full_clean()
        self.assertEqual(record.color, '#5DC1B9')
        record.color = '#5dc1b9'
        record.full_clean()
        self.assertEqual(record.color, '#5DC1B9')
        record.color = '5dc1b9'
        record.full_clean()
        self.assertEqual(record.color, '#5DC1B9')
        record.color = '#fff'
        record.full_clean()
        self.assertEqual(record.color, '#FFFFFF')
        record.color = 'fff'
        record.full_clean()
        self.assertEqual(record.color, '#FFFFFF')


class CommaSeparatedFieldTest(test.TestCase):

    def test_separation(self):
        record_1 = CommaSeparatedModel()
        record_1.default_separator = 'a, b, c'
        record_1.custom_separator = 'a|b|c'
        record_1.full_clean()
        self.assertEqual(record_1.default_separator, ['a', 'b', 'c'])
        self.assertEqual(record_1.custom_separator, ['a', 'b', 'c'])
        record_1.full_clean()
        self.assertEqual(record_1.default_separator, ['a', 'b', 'c'])
        self.assertEqual(record_1.custom_separator, ['a', 'b', 'c'])
        record_1.save()

        record_2 = CommaSeparatedModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default_separator, ['a', 'b', 'c'])
        self.assertEqual(record_2.custom_separator, ['a', 'b', 'c'])

        record_3 = CommaSeparatedModel()
        record_3.default_separator = 'a, b, c'
        record_3.custom_separator = 'a|b|c'
        record_3.save()

        record_4 = CommaSeparatedModel.objects.get(pk=record_3.pk)
        self.assertEqual(record_4.default_separator, ['a', 'b', 'c'])
        self.assertEqual(record_4.custom_separator, ['a', 'b', 'c'])


class CompressedTextFieldTest(test.TestCase):

    def checkCompressedField(self, field_name, string):
        field = CompressedModel._meta.get_field(field_name)
        compressed = field.compress(string)
        decompressed = field.decompress(compressed)
        self.assertIsInstance(string, six.text_type)
        self.assertIsInstance(compressed, six.binary_type)
        self.assertIsInstance(decompressed, six.text_type)
        self.assertEqual(decompressed, string)

    def test_compression(self):
        self.checkCompressedField('default', ascii_1)
        self.checkCompressedField('level_3', ascii_2)
        self.checkCompressedField('level_6', ascii_2)
        self.checkCompressedField('level_9', ascii_2)

    def test_compression_french(self):
        self.checkCompressedField('default', french_1)
        self.checkCompressedField('level_3', french_2)
        self.checkCompressedField('level_6', french_2)
        self.checkCompressedField('level_9', french_2)

    def test_compression_greek(self):
        self.checkCompressedField('default', greek_1)
        self.checkCompressedField('level_3', greek_2)
        self.checkCompressedField('level_6', greek_2)
        self.checkCompressedField('level_9', greek_2)

    def test_compression_spanish(self):
        self.checkCompressedField('default', spanish_1)
        self.checkCompressedField('level_3', spanish_2)
        self.checkCompressedField('level_6', spanish_2)
        self.checkCompressedField('level_9', spanish_2)

    def test_database(self):
        record_1 = CompressedModel()
        record_1.default = ascii_1
        record_1.level_3 = ascii_2
        record_1.level_6 = ascii_2
        record_1.level_9 = ascii_2
        record_1.save()

        self.assertEqual(record_1.default, ascii_1)
        self.assertEqual(record_1.level_3, ascii_2)
        self.assertEqual(record_1.level_6, ascii_2)
        self.assertEqual(record_1.level_9, ascii_2)

        record_2 = CompressedModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, ascii_1)
        self.assertEqual(record_2.level_3, ascii_2)
        self.assertEqual(record_2.level_6, ascii_2)
        self.assertEqual(record_2.level_9, ascii_2)

    def test_database_french(self):
        record_1 = CompressedModel()
        record_1.default = french_1
        record_1.level_3 = french_2
        record_1.level_6 = french_2
        record_1.level_9 = french_2
        record_1.full_clean()
        record_1.save()

        record_2 = CompressedModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, french_1)
        self.assertEqual(record_2.level_3, french_2)
        self.assertEqual(record_2.level_6, french_2)
        self.assertEqual(record_2.level_9, french_2)

    def test_database_greek(self):
        record_1 = CompressedModel()
        record_1.default = greek_1
        record_1.level_3 = greek_2
        record_1.level_6 = greek_2
        record_1.level_9 = greek_2
        record_1.full_clean()
        record_1.save()

        record_2 = CompressedModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, greek_1)
        self.assertEqual(record_2.level_3, greek_2)
        self.assertEqual(record_2.level_6, greek_2)
        self.assertEqual(record_2.level_9, greek_2)

    def test_database_spanish(self):
        record_1 = CompressedModel()
        record_1.default = spanish_1
        record_1.level_3 = spanish_2
        record_1.level_6 = spanish_2
        record_1.level_9 = spanish_2
        record_1.full_clean()
        record_1.save()

        record_2 = CompressedModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, spanish_1)
        self.assertEqual(record_2.level_3, spanish_2)
        self.assertEqual(record_2.level_6, spanish_2)
        self.assertEqual(record_2.level_9, spanish_2)


class DecimalFieldTest(test.TestCase):

    def test_defaults(self):
        record = DecimalModel()
        self.assertEqual(record.decimal, dec('0'))
        self.assertIsInstance(record.decimal, dec)
        self.assertIsNone(record.null_decimal)
        self.assertEqual(record.positive_decimal, dec('0'))
        self.assertIsInstance(record.positive_decimal, dec)

    def test_validators(self):
        record = DecimalModel()

        # DECIMAL
        record.decimal = None
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.decimal = dec('10000.00')
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.decimal = dec('-10000.00')
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.decimal = dec('100.00')
        record.full_clean()
        record.decimal = dec('-100.00')
        record.full_clean()

        # NULL DECIMAL
        record.null_decimal = None
        record.full_clean()

        record.null_decimal = dec('10000.00')
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.null_decimal = dec('-10000.00')
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.null_decimal = dec('100.00')
        record.full_clean()
        record.null_decimal = dec('-100.00')
        record.full_clean()

        # POSITIVE DECIMAL
        record.positive_decimal = None
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.positive_decimal = dec('10000.00')
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.positive_decimal = dec('-10000.00')
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.positive_decimal = dec('100.00')
        record.full_clean()
        record.positive_decimal = dec('-100.00')
        with self.assertRaises(ValidationError):
            record.full_clean()


class EmailFieldTest(test.TestCase):

    def test_cleaning(self):
        record = EmailModel()
        record.email = 'abc'
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.email = 'user@domain.com'
        record.full_clean()
        self.assertEqual(record.email, 'user@domain.com')
        record.email = 'USER@DOMAIN.COM'
        record.full_clean()
        self.assertEqual(record.email, 'user@domain.com')
        record.email = 'USER@domain.com'
        record.full_clean()
        self.assertEqual(record.email, 'USER@domain.com')
        record.email = 'User@Domain.Com'
        record.full_clean()
        self.assertEqual(record.email, 'User@domain.com')
        record.email = '\tuser@domain.com  '
        record.full_clean()
        self.assertEqual(record.email, 'user@domain.com')


class EncryptedTextFieldTest(test.TestCase):

    def checkEncryptedField(self, field_name, string):
        field = EncryptedModel._meta.get_field(field_name)
        encrypted = field.encrypt(string)
        decrypted = field.decrypt(encrypted)
        self.assertIsInstance(string, six.text_type)
        self.assertIsInstance(encrypted, six.binary_type)
        self.assertIsInstance(decrypted, six.text_type)
        self.assertEqual(decrypted, string)

    def test_encryptation(self):
        self.checkEncryptedField('default', ascii_1)
        self.checkEncryptedField('aes', ascii_2)
        self.checkEncryptedField('arc2', ascii_2)
        #self.checkEncryptedField('arc4', ascii_2)
        self.checkEncryptedField('blowfish', ascii_2)
        self.checkEncryptedField('cast', ascii_2)
        self.checkEncryptedField('des', ascii_2)
        self.checkEncryptedField('des3', ascii_2)
        #self.checkEncryptedField('xor', ascii_2)

    def test_encryptation_french(self):
        self.checkEncryptedField('default', french_1)
        self.checkEncryptedField('aes', french_2)
        self.checkEncryptedField('arc2', french_2)
        #self.checkEncryptedField('arc4', french_2)
        self.checkEncryptedField('blowfish', french_2)
        self.checkEncryptedField('cast', french_2)
        self.checkEncryptedField('des', french_2)
        self.checkEncryptedField('des3', french_2)
        #self.checkEncryptedField('xor', french_2)

    def test_encryptation_greek(self):
        self.checkEncryptedField('default', greek_1)
        self.checkEncryptedField('aes', greek_2)
        self.checkEncryptedField('arc2', greek_2)
        #self.checkEncryptedField('arc4', greek_2)
        self.checkEncryptedField('blowfish', greek_2)
        self.checkEncryptedField('cast', greek_2)
        self.checkEncryptedField('des', greek_2)
        self.checkEncryptedField('des3', greek_2)
        #self.checkEncryptedField('xor', greek_2)

    def test_encryptation_spanish(self):
        self.checkEncryptedField('default', spanish_1)
        self.checkEncryptedField('aes', spanish_2)
        self.checkEncryptedField('arc2', spanish_2)
        #self.checkEncryptedField('arc4', spanish_2)
        self.checkEncryptedField('blowfish', spanish_2)
        self.checkEncryptedField('cast', spanish_2)
        self.checkEncryptedField('des', spanish_2)
        self.checkEncryptedField('des3', spanish_2)
        #self.checkEncryptedField('xor', spanish_2)

    def test_database(self):
        record_1 = EncryptedModel()
        record_1.default = ascii_1
        record_1.aes = ascii_2
        record_1.arc2 = ascii_2
        #record_1.arc4 = ascii_2
        record_1.blowfish = ascii_2
        record_1.cast = ascii_2
        record_1.des = ascii_2
        record_1.des3 = ascii_2
        #record_1.xor = ascii_2
        record_1.save()

        self.assertEqual(record_1.default, ascii_1)
        self.assertEqual(record_1.aes, ascii_2)
        self.assertEqual(record_1.arc2, ascii_2)
        #self.assertEqual(record_1.arc4, ascii_2)
        self.assertEqual(record_1.blowfish, ascii_2)
        self.assertEqual(record_1.cast, ascii_2)
        self.assertEqual(record_1.des, ascii_2)
        self.assertEqual(record_1.des3, ascii_2)
        #self.assertEqual(record_1.xor, ascii_2)

        record_2 = EncryptedModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, ascii_1)
        self.assertEqual(record_2.aes, ascii_2)
        self.assertEqual(record_2.arc2, ascii_2)
        #self.assertEqual(record_2.arc4, ascii_2)
        self.assertEqual(record_2.blowfish, ascii_2)
        self.assertEqual(record_2.cast, ascii_2)
        self.assertEqual(record_2.des, ascii_2)
        self.assertEqual(record_2.des3, ascii_2)
        #self.assertEqual(record_2.xor, ascii_2)

    def test_database_french(self):
        record_1 = EncryptedModel()
        record_1.default = french_1
        record_1.aes = french_2
        record_1.arc2 = french_2
        #record_1.arc4 = french_2
        record_1.blowfish = french_2
        record_1.cast = french_2
        record_1.des = french_2
        record_1.des3 = french_2
        #record_1.xor = french_2
        record_1.full_clean()
        record_1.save()

        record_2 = EncryptedModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, french_1)
        self.assertEqual(record_2.aes, french_2)
        self.assertEqual(record_2.arc2, french_2)
        #self.assertEqual(record_2.arc4, french_2)
        self.assertEqual(record_2.blowfish, french_2)
        self.assertEqual(record_2.cast, french_2)
        self.assertEqual(record_2.des, french_2)
        self.assertEqual(record_2.des3, french_2)
        #self.assertEqual(record_2.xor, french_2)

    def test_database_greek(self):
        record_1 = EncryptedModel()
        record_1.default = greek_1
        record_1.aes = greek_2
        record_1.arc2 = greek_2
        #record_1.arc4 = greek_2
        record_1.blowfish = greek_2
        record_1.cast = greek_2
        record_1.des = greek_2
        record_1.des3 = greek_2
        #record_1.xor = greek_2
        record_1.full_clean()
        record_1.save()

        record_2 = EncryptedModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, greek_1)
        self.assertEqual(record_2.aes, greek_2)
        self.assertEqual(record_2.arc2, greek_2)
        #self.assertEqual(record_2.arc4, greek_2)
        self.assertEqual(record_2.blowfish, greek_2)
        self.assertEqual(record_2.cast, greek_2)
        self.assertEqual(record_2.des, greek_2)
        self.assertEqual(record_2.des3, greek_2)
        #self.assertEqual(record_2.xor, greek_2)

    def test_database_spanish(self):
        record_1 = EncryptedModel()
        record_1.default = spanish_1
        record_1.aes = spanish_2
        record_1.arc2 = spanish_2
        #record_1.arc4 = spanish_2
        record_1.blowfish = spanish_2
        record_1.cast = spanish_2
        record_1.des = spanish_2
        record_1.des3 = spanish_2
        #record_1.xor = spanish_2
        record_1.full_clean()
        record_1.save()

        record_2 = EncryptedModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, spanish_1)
        self.assertEqual(record_2.aes, spanish_2)
        self.assertEqual(record_2.arc2, spanish_2)
        #self.assertEqual(record_2.arc4, spanish_2)
        self.assertEqual(record_2.blowfish, spanish_2)
        self.assertEqual(record_2.cast, spanish_2)
        self.assertEqual(record_2.des, spanish_2)
        self.assertEqual(record_2.des3, spanish_2)
        #self.assertEqual(record_2.xor, spanish_2)


class FloatFieldTest(test.TestCase):

    def test_defaults(self):
        record = FloatModel()
        self.assertEqual(record.float, 0.0)
        self.assertIsInstance(record.float, float)
        self.assertIsNone(record.null_float)
        self.assertEqual(record.positive_float, 0.0)
        self.assertIsInstance(record.positive_float, float)

    def test_validators(self):
        record = FloatModel()

        # FLOAT
        record.float = None
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.float = 100.00
        record.full_clean()
        record.float = -100.00
        record.full_clean()

        # NULL FLOAT
        record.null_float = None
        record.full_clean()

        record.null_float = 100.00
        record.full_clean()
        record.null_float = -100.00
        record.full_clean()

        # POSITIVE FLOAT
        record.positive_float = None
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.positive_float = 100.00
        record.full_clean()
        record.positive_float = -100.00
        with self.assertRaises(ValidationError):
            record.full_clean()


class FormulaFieldTest(test.TestCase):

    def test_permissive_formula(self):
        record = FormulaModel()
        record.permissive_formula = '1 * 3 ** 5'
        self.assertIsInstance(
            record.permissive_formula,
            Formula,
        )
        self.assertEqual(
            record.permissive_formula.calculate(),
            243,
        )
        record.full_clean()
        self.assertIsInstance(
            record.permissive_formula,
            Formula,
        )
        self.assertEqual(
            record.permissive_formula.calculate(),
            243,
        )
        record.permissive_formula = 'x * y ** z'
        record.full_clean()
        record.permissive_formula = 'a * b ** c'
        record.full_clean()

    def test_restricted_formula(self):
        record = FormulaModel()
        record.restricted_formula = '1 * 3 ** 5'
        self.assertIsInstance(
            record.restricted_formula,
            Formula,
        )
        self.assertEqual(
            record.restricted_formula.calculate(),
            243,
        )
        record.full_clean()
        self.assertIsInstance(
            record.restricted_formula,
            Formula,
        )
        self.assertEqual(
            record.restricted_formula.calculate(),
            243,
        )
        record.restricted_formula = 'x * y ** z'
        record.full_clean()
        record.restricted_formula = 'a * b ** c'
        with self.assertRaises(ValidationError):
            record.full_clean()


class GuidFieldTest(test.TestCase):

    def test_default_value(self):
        default_guids = []
        custom_guids = []
        for i in range(10):
            record = GuidModel()
            self.assertRegexpMatches(record.default_charset, '^[0-9a-f]+$')
            self.assertRegexpMatches(record.custom_charset, '^[z%,#8+ç@]+$')
            default_guids.append(record.default_charset)
            custom_guids.append(record.custom_charset)

        counter = Counter(default_guids)
        self.assertEqual(counter.most_common(1)[0][1], 1)
        counter = Counter(custom_guids)
        self.assertEqual(counter.most_common(1)[0][1], 1)


class IdentifierFieldTest(test.TestCase):

    def test_validation(self):
        record = IdentifierModel()
        record.key = 'variable'
        record.full_clean()
        record.key = 'variable_123'
        record.full_clean()
        record.key = '123_variable'
        with self.assertRaises(ValidationError):
            record.full_clean()
        record.key = 'z%.# +ç@'
        with self.assertRaises(ValidationError):
            record.full_clean()


class IntegerFieldTest(test.TestCase):

    def test_defaults(self):
        record = IntegerModel()
        self.assertEqual(record.integer, 0)
        self.assertIsInstance(record.integer, int)
        self.assertIsNone(record.null_integer)
        self.assertEqual(record.positive_integer, 0)
        self.assertIsInstance(record.positive_integer, int)
        self.assertEqual(record.big_integer, 0)
        self.assertIsInstance(record.big_integer, int)
        self.assertIsNone(record.null_big_integer)
        self.assertEqual(record.positive_big_integer, 0)
        self.assertIsInstance(record.positive_big_integer, int)
        self.assertEqual(record.small_integer, 0)
        self.assertIsInstance(record.small_integer, int)
        self.assertIsNone(record.null_small_integer)
        self.assertEqual(record.positive_small_integer, 0)
        self.assertIsInstance(record.positive_small_integer, int)

    def test_validators(self):
        record = IntegerModel()

        # INTEGER
        record.integer = None
        with self.assertRaises(ValidationError):
            record.full_clean()

        #record.integer = 10000
        #with self.assertRaises(ValidationError):
            #record.full_clean()

        #record.integer = -10000
        #with self.assertRaises(ValidationError):
            #record.full_clean()

        record.integer = 100
        record.full_clean()
        record.integer = -100
        record.full_clean()

        # NULL INTEGER
        record.null_integer = None
        record.full_clean()

        #record.null_integer = 10000
        #with self.assertRaises(ValidationError):
            #record.full_clean()

        #record.null_integer = -10000
        #with self.assertRaises(ValidationError):
            #record.full_clean()

        record.null_integer = 100
        record.full_clean()
        record.null_integer = -100
        record.full_clean()

        # POSITIVE INTEGER
        record.positive_integer = None
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.positive_integer = 10000
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.positive_integer = -10000
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.positive_integer = 100
        record.full_clean()
        record.positive_integer = -100
        with self.assertRaises(ValidationError):
            record.full_clean()


class PhoneNumberFieldTest(test.TestCase):

    def test_cleaning(self):
        record = PhoneNumberModel()
        record.phone = 'abc'
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.phone = '+99 (9999) 9999 9999'
        record.full_clean()
        self.assertEqual(record.phone, '+99 (9999) 9999 9999')
        record.phone = '   +99 (9999) 9999 9999'
        record.full_clean()
        self.assertEqual(record.phone, '+99 (9999) 9999 9999')
        record.phone = '+99 (9999) 9999 9999   '
        record.full_clean()
        self.assertEqual(record.phone, '+99 (9999) 9999 9999')
        record.phone = '+99  (9999)  9999  9999'
        record.full_clean()
        self.assertEqual(record.phone, '+99 (9999) 9999 9999')


class PickledObjectFieldTest(test.TestCase):

    def checkPickledField(self, field_name, obj):
        field = PickledModel._meta.get_field(field_name)
        dumped = field.dump(obj)
        loaded = field.load(dumped)
        self.assertIsInstance(obj, six.text_type)
        self.assertIsInstance(dumped, six.binary_type)
        self.assertIsInstance(loaded, six.text_type)
        self.assertEqual(loaded, obj)

    def test_compression(self):
        self.checkPickledField('default', ascii_1)
        self.checkPickledField('protocol_0', ascii_2)
        self.checkPickledField('protocol_1', ascii_2)
        self.checkPickledField('protocol_2', ascii_2)

    def test_compression_french(self):
        self.checkPickledField('default', french_1)
        self.checkPickledField('protocol_0', french_2)
        self.checkPickledField('protocol_1', french_2)
        self.checkPickledField('protocol_2', french_2)

    def test_compression_greek(self):
        self.checkPickledField('default', greek_1)
        self.checkPickledField('protocol_0', greek_2)
        self.checkPickledField('protocol_1', greek_2)
        self.checkPickledField('protocol_2', greek_2)

    def test_compression_spanish(self):
        self.checkPickledField('default', spanish_1)
        self.checkPickledField('protocol_0', spanish_2)
        self.checkPickledField('protocol_1', spanish_2)
        self.checkPickledField('protocol_2', spanish_2)

    def test_database(self):
        record_1 = PickledModel()
        record_1.default = ascii_1
        record_1.protocol_0 = ascii_2
        record_1.protocol_1 = ascii_2
        record_1.protocol_2 = ascii_2
        record_1.save()

        self.assertEqual(record_1.default, ascii_1)
        self.assertEqual(record_1.protocol_0, ascii_2)
        self.assertEqual(record_1.protocol_1, ascii_2)
        self.assertEqual(record_1.protocol_2, ascii_2)

        record_2 = PickledModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, ascii_1)
        self.assertEqual(record_2.protocol_0, ascii_2)
        self.assertEqual(record_2.protocol_1, ascii_2)
        self.assertEqual(record_2.protocol_2, ascii_2)

    def test_database_french(self):
        record_1 = PickledModel()
        record_1.default = french_1
        record_1.protocol_0 = french_2
        record_1.protocol_1 = french_2
        record_1.protocol_2 = french_2
        record_1.full_clean()
        record_1.save()

        record_2 = PickledModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, french_1)
        self.assertEqual(record_2.protocol_0, french_2)
        self.assertEqual(record_2.protocol_1, french_2)
        self.assertEqual(record_2.protocol_2, french_2)

    def test_database_greek(self):
        record_1 = PickledModel()
        record_1.default = greek_1
        record_1.protocol_0 = greek_2
        record_1.protocol_1 = greek_2
        record_1.protocol_2 = greek_2
        record_1.full_clean()
        record_1.save()

        record_2 = PickledModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, greek_1)
        self.assertEqual(record_2.protocol_0, greek_2)
        self.assertEqual(record_2.protocol_1, greek_2)
        self.assertEqual(record_2.protocol_2, greek_2)

    def test_database_spanish(self):
        record_1 = PickledModel()
        record_1.default = spanish_1
        record_1.protocol_0 = spanish_2
        record_1.protocol_1 = spanish_2
        record_1.protocol_2 = spanish_2
        record_1.full_clean()
        record_1.save()

        record_2 = PickledModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, spanish_1)
        self.assertEqual(record_2.protocol_0, spanish_2)
        self.assertEqual(record_2.protocol_1, spanish_2)
        self.assertEqual(record_2.protocol_2, spanish_2)


class PostalCodeFieldTest(test.TestCase):

    def test_cleaning(self):
        record = PostalCodeModel()
        record.code = 'abc'
        with self.assertRaises(ValidationError):
            record.full_clean()

        record.code = '9999 AA'
        record.full_clean()
        self.assertEqual(record.code, '9999 AA')
        record.code = '9999 aa'
        record.full_clean()
        self.assertEqual(record.code, '9999 AA')
        record.code = '  9999 AA'
        record.full_clean()
        self.assertEqual(record.code, '9999 AA')
        record.code = '9999 AA  '
        record.full_clean()
        self.assertEqual(record.code, '9999 AA')
        record.code = '9999   AA'
        record.full_clean()
        self.assertEqual(record.code, '9999 AA')


@skipUnlessMarkdown()
class RichTextFieldTest(test.TestCase):

    def test_markdown(self):
        record = RichTextModel.objects.create(
            text='This is **important.**',
        )
        self.assertEqual(
            record.text,
            'This is **important.**',
        )
        self.assertEqual(
            record.text_html,
            '<p>This is <strong>important.</strong></p>\n',
        )

    def test_processors(self):
        record = RichTextModel.objects.create(
            upper_text='This is **important.**',
        )
        self.assertEqual(
            record.upper_text,
            'This is **important.**',
        )
        self.assertEqual(
            record.upper_text_html,
            '<P>THIS IS <STRONG>IMPORTANT.</STRONG></P>\n',
        )

    def test_saved_values(self):
        record_1 = RichTextModel()
        record_1.text = 'This is **important.**'
        record_1.upper_text = 'This is **not** important.'
        self.assertEqual(
            record_1.text_html,
            '',
        )
        self.assertEqual(
            record_1.upper_text_html,
            '<P>THIS IS <STRONG>NOT</STRONG> IMPORTANT.</P>\n',
        )
        record_1.save()
        self.assertEqual(
            record_1.text_html,
            '<p>This is <strong>important.</strong></p>\n',
        )
        self.assertEqual(
            record_1.upper_text_html,
            '<P>THIS IS <STRONG>NOT</STRONG> IMPORTANT.</P>\n',
        )
        record_2 = RichTextModel.objects.get(pk=record_1.pk)
        self.assertEqual(
            record_2.text_html,
            '<p>This is <strong>important.</strong></p>\n',
        )
        self.assertEqual(
            record_2.upper_text_html,
            '<P>THIS IS <STRONG>NOT</STRONG> IMPORTANT.</P>\n',
        )
        record_2.text = 'This is **irrelevant.**'
        record_2.upper_text = 'This is **not** irrelevant.'
        self.assertEqual(
            record_2.text_html,
            '<p>This is <strong>important.</strong></p>\n',
        )
        self.assertEqual(
            record_2.upper_text_html,
            '<P>THIS IS <STRONG>NOT</STRONG> IRRELEVANT.</P>\n',
        )
        record_2.save()
        self.assertEqual(
            record_2.text_html,
            '<p>This is <strong>irrelevant.</strong></p>\n',
        )
        self.assertEqual(
            record_2.upper_text_html,
            '<P>THIS IS <STRONG>NOT</STRONG> IRRELEVANT.</P>\n',
        )
        record_3 = RichTextModel.objects.get(pk=record_2.pk)
        self.assertEqual(
            record_3.text_html,
            '<p>This is <strong>irrelevant.</strong></p>\n',
        )
        self.assertEqual(
            record_3.upper_text_html,
            '<P>THIS IS <STRONG>NOT</STRONG> IRRELEVANT.</P>\n',
        )


class SlugFieldTest(test.TestCase):

    def test_slugify_on_clean(self):
        record = SlugModel(title='Lorem Ipsum')
        record.full_clean()
        self.assertEqual(
            record.slug,
            'lorem-ipsum',
        )
        record = SlugModel(title='Ñandúes')
        record.full_clean()
        self.assertEqual(
            record.slug,
            'nandues',
        )
        record = SlugModel(title='Ελληνικά')
        record.full_clean()
        self.assertEqual(
            record.slug,
            'ellenika',
        )

    def test_slugify_on_save(self):
        record = SlugModel(title='Lorem Ipsum')
        record.save()
        self.assertEqual(
            record.slug,
            'lorem-ipsum',
        )
        record = SlugModel(title='Ñandúes')
        record.save()
        self.assertEqual(
            record.slug,
            'nandues',
        )
        record = SlugModel(title='Ελληνικά')
        record.save()
        self.assertEqual(
            record.slug,
            'ellenika',
        )

    def test_avoid_duplicates(self):
        record = SlugModel.objects.create(title='Lorem Ipsum')
        self.assertEqual(record.slug, 'lorem-ipsum')
        self.assertEqual(record.unique_slug, 'lorem-ipsum')
        self.assertEqual(record.relatively_unique_slug, 'lorem-ipsum')

        record = SlugModel.objects.create(title='Lorem Ipsum')
        self.assertEqual(record.slug, 'lorem-ipsum')
        self.assertEqual(record.unique_slug, 'lorem-ipsum-2')
        self.assertEqual(record.relatively_unique_slug, 'lorem-ipsum-2')

        record = SlugModel.objects.create(title='Lorem Ipsum', filter_field=True)
        self.assertEqual(record.slug, 'lorem-ipsum')
        self.assertEqual(record.unique_slug, 'lorem-ipsum-3')
        self.assertEqual(record.relatively_unique_slug, 'lorem-ipsum')

        record = SlugModel.objects.create(title='Lorem Ipsum', filter_field=True)
        self.assertEqual(record.slug, 'lorem-ipsum')
        self.assertEqual(record.unique_slug, 'lorem-ipsum-4')
        self.assertEqual(record.relatively_unique_slug, 'lorem-ipsum-2')


class TextFieldTest(test.TestCase):

    def test_validators(self):
        record = TextModel()
        record.limited_text = ''
        with self.assertRaises(ValidationError):
            record.full_clean()
        record.limited_text = 'abcde'
        with self.assertRaises(ValidationError):
            record.full_clean()
        record.limited_text = 'abcde' * 20
        with self.assertRaises(ValidationError):
            record.full_clean()
        record.limited_text = 'abcde' * 5
        record.full_clean()

