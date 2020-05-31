from django.db.backends.mysql.base import DatabaseWrapper
from django.db.models.fields import BinaryField

DatabaseWrapper.data_types['Sha512Field'] = 'BINARY(64)'


class Sha512Field(BinaryField):
    '`BINARY(64)` stored field for 64 bytes of binary data in MariaDB.'

    def get_internal_type(self) -> str:
        return 'Sha512Field'
