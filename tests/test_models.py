import pytest
from celestia._celestia import types  # noqa

from celestia.types.common import Namespace


@pytest.mark.asyncio
async def test_namespace():
    namespace = Namespace(b"Alesh")
    assert namespace == b"\x00" * 24 + b"Alesh"
    assert str(namespace) == "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQWxlc2g="
    assert namespace == Namespace("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQWxlc2g=")
    with pytest.raises(ValueError):
        Namespace(b"111111111111111111111111111111111")
    with pytest.raises(ValueError):
        Namespace(b"1111111111111111111111111111111111111111111111111111111111")


@pytest.mark.asyncio
async def test_blob():
    blob = types.normalize_blob(b"Alesh", b"0123456789ABCDEF")
    assert blob == {
        "namespace": b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Alesh",
        "commitment": b"\x88e\rh\xc1\x02\xbd\xfc\xbcc\xa3\xcc\x10\n5\xdf\xcbCh\xa3m\x04\xe1\xeds(\xdf}j>\xab/",
        "data": b"0123456789ABCDEF",
        "index": None,
        "share_version": 0,
    }
