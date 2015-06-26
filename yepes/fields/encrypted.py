# -*- coding:utf-8 -*-

from base64 import b64decode, b64encode

from Crypto.Cipher import AES, ARC2, ARC4, Blowfish, CAST, DES, DES3, XOR

from django import forms
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import six
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _

from yepes.conf import settings
from yepes.exceptions import LookupTypeError
from yepes.fields.char import CharField
from yepes.utils.deconstruct import clean_keywords
from yepes.utils.properties import cached_property

__all__ = ('EncryptedCharField', 'EncryptedTextField',
           'InvalidLengthError', 'TooShortError')

CIPHER_KEY_LENGTHS = {
    AES: (32, 24, 16),
    ARC2: (16, 8),
    ARC4: (256, 248, 128, 120, 64, 56, 32, 24, 16, 8),
    Blowfish: (56, 32, 24, 16, 8),
    CAST: (16, 8),
    DES: (8, ),
    DES3: (24, 16),
    XOR: (32, 24, 16, 8),
}


class InvalidLengthError(ValueError):

    def __init__(self, valid_lengths):
        msg = 'Key length must be: {0}'
        msg = msg.format(str(tuple(valid_lengths))[1:-1])
        super(InvalidLengthError, self).__init__(msg)


class TooShortError(ValueError):

    def __init__(self):
        msg = 'Too short secret key.'
        super(TooShortError, self).__init__(msg)


@six.add_metaclass(models.SubfieldBase)
class EncryptedTextField(models.BinaryField):

    description = _('Encrypted text')

    _pad = six.int2byte(0)
    _prefix = '[{(#'
    _suffix = '#)}]'

    @cached_property
    def _cipher(self):
        key = self.get_secret_key()
        return self.cipher.new(key)

    @cached_property
    def _prefix_len(self):
        return len(self._prefix)

    @cached_property
    def _suffix_len(self):
        return len(self._suffix)

    def __init__(self, *args, **kwargs):
        self.cipher = kwargs.pop('cipher', AES)
        editable = kwargs.pop('editable', True)
        self.secret_key = kwargs.pop('secret_key', None)
        super(EncryptedTextField, self).__init__(*args, **kwargs)
        self.editable = editable

    def deconstruct(self):
        name, path, args, kwargs = super(EncryptedTextField, self).deconstruct()
        path = path.replace('yepes.fields.encrypted', 'yepes.fields')
        clean_keywords(self, kwargs, defaults={
            'cipher': AES,
            'editable': True,
            'secret_key': None,
        })
        return name, path, args, kwargs

    def decrypt(self, encrypted):
        decrypted = self._cipher.decrypt(force_bytes(encrypted))
        return decrypted.lstrip(self._pad).decode('utf-8')

    def encrypt(self, text):
        bytes = force_text(text).encode('utf-8')
        up_to_sixteen = 16 - ((len(bytes) % 16) or 16)
        bytes = (self._pad * up_to_sixteen) + bytes
        return self._cipher.encrypt(bytes)

    def formfield(self, **kwargs):
        kwargs.setdefault('widget', forms.Textarea)
        kwargs.setdefault('max_length', self.max_length)
        return super(EncryptedTextField, self).formfield(**kwargs)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise LookupTypeError(lookup_type)

    def get_prep_value(self, value):
        if value is not None:
            return self.encrypt(value)
        else:
            return value

    def get_secret_key(self):
        if self.secret_key:
            key = force_bytes(self.secret_key)
            if self.cipher in CIPHER_KEY_LENGTHS:
                valid_lengths = CIPHER_KEY_LENGTHS[self.cipher]
                if len(key) not in valid_lengths:
                    raise InvalidLengthError(reversed(valid_lengths))
            return key
        else:
            key = force_bytes(settings.SECRET_KEY)
            key_length = len(key)
            if self.cipher in CIPHER_KEY_LENGTHS:
                # Try to return the longest valid key.
                for length in CIPHER_KEY_LENGTHS[self.cipher]:
                    if key_length >= length:
                        return key[-length:]
                else:
                    raise TooShortError()
            else:
                return key[0:16]   # Cut key to most common length.

    def to_python(self, value):
        if isinstance(value, six.binary_type):
            return self.decrypt(value)
        elif isinstance(value, buffer if six.PY2 else memoryview):
            return self.decrypt(six.binary_type(value))
        elif (isinstance(value, six.text_type)
                and value.startswith(self._prefix)
                and value.endswith(self._suffix)):
            return self.value_from_string()
        else:
            return value

    def value_from_string(self, string):
        encrypted_value = string[self._prefix_len:-self._suffix_len]
        return self.decrypt(b64decode(encrypted_value.encode('ascii')))

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        encrypted_value = b64encode(self.encrypt(value)).decode('ascii')
        return ''.join(self._prefix, encrypted_value, self._suffix)


class EncryptedCharField(EncryptedTextField):

    def __init__(self, *args, **kwargs):
        self.min_length = kwargs.pop('min_length', None)
        super(EncryptedCharField, self).__init__(*args, **kwargs)
        if self.min_length is not None:
            self.validators.append(MinLengthValidator(self.min_length))

    def check(self, **kwargs):
        errors = super(EncryptedCharField, self).check(**kwargs)
        errors.extend(self._check_max_length_attribute(**kwargs))
        errors.extend(self._check_min_length_attribute(**kwargs))
        return errors

    #_check_max_length_attribute = CharField._check_max_length_attribute
    _check_min_length_attribute = CharField._check_min_length_attribute

    def deconstruct(self):
        name, path, args, kwargs = super(EncryptedCharField, self).deconstruct()
        clean_keywords(self, kwargs, defaults={
            'min_length': None,
        })
        return (name, path, args, kwargs)

    def formfield(self, **kwargs):
        kwargs.setdefault('widget', forms.TextInput)
        kwargs.setdefault('min_length', self.min_length)
        kwargs.setdefault('max_length', self.max_length)
        return super(EncryptedCharField, self).formfield(**kwargs)

