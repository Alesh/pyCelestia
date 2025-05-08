import pytest
from dataclasses import asdict

from celestia.types import Blob


def test_create_blob():
    blob = Blob(b'abc', b'0123456789')
    assert dict((k, str(v)) for k, v in asdict(blob).items()) == {
        'commitment': '8M4WkNbOtjABYe0ymm4Q/BgfrBmDT4FpCXRrviKFrIE=',
        'data': 'MDEyMzQ1Njc4OQ==',
        'index': 'None',
        'namespace': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABhYmM=',
        'share_version': '0'
    }

def test_blob_errors():
    with pytest.raises(ValueError, match='Wrong namespaces'):
        Blob(b'abc0123456789', b'0123456789')
    with pytest.raises(ValueError, match='Invalid namespace size'):
        Blob(b'abc0123456789', b'0123456789')
