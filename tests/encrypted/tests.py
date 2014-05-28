# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import test
from django.utils import six

from .models import TestModel


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


class EncryptedTest(test.TestCase):

    def checkEncryptedField(self, field_name, string):
        field = TestModel._meta.get_field(field_name, False)
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
        self.checkEncryptedField('xor', ascii_2)

    def test_encryptation_french(self):
        self.checkEncryptedField('default', french_1)
        self.checkEncryptedField('aes', french_2)
        self.checkEncryptedField('arc2', french_2)
        #self.checkEncryptedField('arc4', french_2)
        self.checkEncryptedField('blowfish', french_2)
        self.checkEncryptedField('cast', french_2)
        self.checkEncryptedField('des', french_2)
        self.checkEncryptedField('des3', french_2)
        self.checkEncryptedField('xor', french_2)

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
        self.checkEncryptedField('xor', spanish_2)

    def test_database(self):
        record_1 = TestModel()
        record_1.default = ascii_1
        record_1.aes = ascii_2
        record_1.arc2 = ascii_2
        #record_1.arc4 = ascii_2
        record_1.blowfish = ascii_2
        record_1.cast = ascii_2
        record_1.des = ascii_2
        record_1.des3 = ascii_2
        record_1.xor = ascii_2
        record_1.save()

        self.assertEqual(record_1.default, ascii_1)
        self.assertEqual(record_1.aes, ascii_2)
        self.assertEqual(record_1.arc2, ascii_2)
        #self.assertEqual(record_1.arc4, ascii_2)
        self.assertEqual(record_1.blowfish, ascii_2)
        self.assertEqual(record_1.cast, ascii_2)
        self.assertEqual(record_1.des, ascii_2)
        self.assertEqual(record_1.des3, ascii_2)
        self.assertEqual(record_1.xor, ascii_2)

        record_2 = TestModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, ascii_1)
        self.assertEqual(record_2.aes, ascii_2)
        self.assertEqual(record_2.arc2, ascii_2)
        #self.assertEqual(record_2.arc4, ascii_2)
        self.assertEqual(record_2.blowfish, ascii_2)
        self.assertEqual(record_2.cast, ascii_2)
        self.assertEqual(record_2.des, ascii_2)
        self.assertEqual(record_2.des3, ascii_2)
        self.assertEqual(record_2.xor, ascii_2)

    def test_database_french(self):
        record_1 = TestModel()
        record_1.default = french_1
        record_1.aes = french_2
        record_1.arc2 = french_2
        #record_1.arc4 = french_2
        record_1.blowfish = french_2
        record_1.cast = french_2
        record_1.des = french_2
        record_1.des3 = french_2
        record_1.xor = french_2
        record_1.full_clean()
        record_1.save()

        record_2 = TestModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, french_1)
        self.assertEqual(record_2.aes, french_2)
        self.assertEqual(record_2.arc2, french_2)
        #self.assertEqual(record_2.arc4, french_2)
        self.assertEqual(record_2.blowfish, french_2)
        self.assertEqual(record_2.cast, french_2)
        self.assertEqual(record_2.des, french_2)
        self.assertEqual(record_2.des3, french_2)
        self.assertEqual(record_2.xor, french_2)

    def test_database_greek(self):
        record_1 = TestModel()
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

        record_2 = TestModel.objects.get(pk=record_1.pk)
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
        record_1 = TestModel()
        record_1.default = spanish_1
        record_1.aes = spanish_2
        record_1.arc2 = spanish_2
        #record_1.arc4 = spanish_2
        record_1.blowfish = spanish_2
        record_1.cast = spanish_2
        record_1.des = spanish_2
        record_1.des3 = spanish_2
        record_1.xor = spanish_2
        record_1.full_clean()
        record_1.save()

        record_2 = TestModel.objects.get(pk=record_1.pk)
        self.assertEqual(record_2.default, spanish_1)
        self.assertEqual(record_2.aes, spanish_2)
        self.assertEqual(record_2.arc2, spanish_2)
        #self.assertEqual(record_2.arc4, spanish_2)
        self.assertEqual(record_2.blowfish, spanish_2)
        self.assertEqual(record_2.cast, spanish_2)
        self.assertEqual(record_2.des, spanish_2)
        self.assertEqual(record_2.des3, spanish_2)
        self.assertEqual(record_2.xor, spanish_2)

