# -*- coding:utf-8 -*-

from base64 import b64decode, b64encode

from Crypto.Cipher import AES, ARC2, ARC4, Blowfish, CAST, DES, DES3, XOR

from django.db import models
from django.utils import six
from django.utils.encoding import force_bytes, force_text

from yepes.conf import settings
from yepes.exceptions import LookupTypeError
from yepes.utils.properties import cached_property

__all__ = ('EncryptedTextField', 'InvalidLengthError', 'TooShortError')


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

    def decrypt(self, encrypted):
        decrypted = self._cipher.decrypt(force_bytes(encrypted))
        return decrypted.lstrip(self._pad).decode('utf-8')

    def encrypt(self, text):
        bytes = force_text(text).encode('utf-8')
        up_to_sixteen = 16 - ((len(bytes) % 16) or 16)
        bytes = (self._pad * up_to_sixteen) + bytes
        return self._cipher.encrypt(bytes)

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

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.BinaryField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

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

