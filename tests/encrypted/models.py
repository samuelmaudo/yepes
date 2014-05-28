# -*- coding:utf-8 -*-

from Crypto.Cipher import AES, ARC2, ARC4, Blowfish, CAST, DES, DES3, XOR

from django.db import models

from yepes.fields import EncryptedTextField


class TestModel(models.Model):

    default = EncryptedTextField()
    aes = EncryptedTextField(cipher=AES)
    arc2 = EncryptedTextField(cipher=ARC2)
    #arc4 = EncryptedTextField(cipher=ARC4)
    blowfish = EncryptedTextField(cipher=Blowfish)
    cast = EncryptedTextField(cipher=CAST)
    des = EncryptedTextField(cipher=DES)
    des3 = EncryptedTextField(cipher=DES3)
    xor = EncryptedTextField(cipher=XOR)

