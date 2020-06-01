from django.db.backends.mysql.base import DatabaseWrapper
from django.db.backends.mysql.compiler import SQLUpdateCompiler
from django.db.models.expressions import Col
from django.db.models.fields import BinaryField, CharField

'This works only with MySQL/MariaDB for now.'

DatabaseWrapper.data_types['CharBinaryField'] = 'VARBINARY(%(max_length)s)'
DatabaseWrapper.data_types['Sha512Field'] = 'BINARY(64)'


class CharBinaryField(CharField):
    """
    `VARBINARY` stored CharField that has no collation, hence is case
    sensitive.
    """
    get_db_prep_value = BinaryField.get_db_prep_value

    def get_internal_type(self) -> str:
        return 'CharBinaryField'

    def to_python(self, value: str) -> bytes:
        'Convert to bytes to store in DB.'
        if isinstance(value, bytes) or value is None:
            return value
        return value.encode('utf-8')

    def from_db_value(
        self, value: bytes, expression: Col, connection: DatabaseWrapper,
    ) -> str:
        'Convert back to `str` from the DB stored `bytes`.'
        return value.decode('utf-8')

    def get_db_prep_value(
        self, value: str, connection: DatabaseWrapper, prepared: bool = False
    ):
        'Get a binary representation from the DB itself for storage.'
        value = super().get_db_prep_value(
            value=value, connection=connection, prepared=prepared)
        if value is not None:
            return connection.Database.Binary(value)
        return value

    def get_placeholder(
        self, value: bytes, compiler: SQLUpdateCompiler,
        connection: DatabaseWrapper
    ) -> str:
        'Note the DB we want to store binary data.'
        return BinaryField.get_placeholder(
            self=self, value=value, compiler=compiler, connection=connection)


class Sha512Field(BinaryField):
    '`BINARY(64)` stored field for 64 bytes of binary data in MariaDB.'

    def get_internal_type(self) -> str:
        return 'Sha512Field'
