import asyncio
from dataclasses import asdict

import pytest
from celestia._celestia import types as ext  # noqa

from celestia.node_api import Client
from celestia.types import Namespace
from celestia.types.blob import Blob


def test_create_blob():
    blob = Blob(b"abc", b"0123456789")
    assert dict((k, str(v)) for k, v in asdict(blob).items()) == {
        "commitment": "8M4WkNbOtjABYe0ymm4Q/BgfrBmDT4FpCXRrviKFrIE=",
        "data": "MDEyMzQ1Njc4OQ==",
        "index": "None",
        "namespace": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABhYmM=",
        "share_version": "0",
        "signer": "None",
    }

    assert Blob(**asdict(blob))

    signed_blob = Blob(
        b"abc", b"0123456789", signer="celestia1qypqxpq9qcrsszg2pvxq6rs0zqg3yyc5wgawu3"
    )
    assert dict((k, str(v)) for k, v in asdict(signed_blob).items()) == {
        "commitment": "pk39MJeTRHg0FuAZX0PKAnxQLJ/PAprwBrzgGNJ2hu0=",
        "data": "MDEyMzQ1Njc4OQ==",
        "index": "None",
        "namespace": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABhYmM=",
        "share_version": "1",
        "signer": "AQIDBAUGBwgJCgsMDQ4PEBESExQ=",
    }

    assert Blob(**asdict(signed_blob))

    assert signed_blob.commitment != blob.commitment


def test_blob_errors():
    blob = Blob(b"abc", b"0123456789")
    signed_blob = Blob(
        b"abc", b"0123456789", signer="celestia1qypqxpq9qcrsszg2pvxq6rs0zqg3yyc5wgawu3"
    )

    with pytest.raises(ValueError, match="Wrong namespaces"):
        Blob(b"abc0123456789", b"0123456789")

    with pytest.raises(ValueError, match="Invalid namespace size"):
        Blob(b"abc0123456789", b"0123456789")

    with pytest.raises(ValueError, match="Wrong commitment"):
        Blob(**dict(asdict(blob), commitment=b"0123456789"))

    with pytest.raises(ValueError, match="Invalid address"):
        Blob(b"abc", b"0123456789", signer="celestiaXXX=")

    with pytest.raises(ValueError, match="Wrong commitment"):
        Blob(**dict(asdict(signed_blob), commitment=b"0123456789"))

    with pytest.raises(ValueError, match="Wrong share version"):
        Blob(**dict(asdict(signed_blob), share_version=0))


async def test_sending_signed_blob(node_provider):
    bridge, auth_token = await node_provider("bridge-0")
    client = Client(port=bridge.port["26658/tcp"])
    async with client.connect(auth_token) as api:
        # unsigned
        blob = Blob(b"abc", b"0123456789")
        result = await api.blob.submit(blob)
        assert len(result.commitments) == 1
        assert result.commitments[0] == blob.commitment

        blobs = await api.blob.get_all(result.height, b"abc")
        assert len(blobs) == 1
        assert blobs[0].commitment == blob.commitment
        assert blobs[0].data == b"0123456789"
        assert blobs[0].share_version == 0

        # signed
        signer_address = await api.state.account_address()
        signed_blob = Blob(b"abc", b"0123456789", signer=signer_address)

        result = await api.blob.submit(signed_blob)
        assert len(result.commitments) == 1
        assert result.commitments[0] == signed_blob.commitment

        blobs = await api.blob.get_all(result.height, b"abc")
        assert blobs[0].commitment == signed_blob.commitment
        assert ext.bytes2address(blobs[0].signer) == signer_address
        assert blobs[0].data == b"0123456789"
        assert blobs[0].share_version == 1
        assert len(blobs) == 1

        # bad signer
        bad_signer_blob = Blob(
            b"abc", b"0123456789", signer="celestia1qypqxpq9qcrsszg2pvxq6rs0zqg3yyc5wgawu3"
        )
        with pytest.raises(ValueError, match="invalid blob signer"):
            await api.blob.submit(bad_signer_blob)

        # auto signer
        blob = Blob(b"abc", b"0123456789")
        assert blob.share_version == 0
        result = await api.blob.submit(blob, signer_address=True)
        assert len(result.commitments) == 1
        blobs = await api.blob.get_all(result.height, b"abc")
        assert blobs[0].commitment != blob.commitment
        assert ext.bytes2address(blobs[0].signer) == signer_address
        assert blobs[0].data == b"0123456789"
        assert blobs[0].share_version == 1
        assert len(blobs) == 1

        # bad auto signer
        bad_signer_blob = Blob(b"abc", b"0123456789")
        with pytest.raises(
            ValueError, match="`signer_address` does not match the current account address"
        ):
            await api.blob.submit(
                bad_signer_blob, signer_address="celestia1qypqxpq9qcrsszg2pvxq6rs0zqg3yyc5wgawu3"
            )

        # bad BLOB signer auto
        bad_signer_blob = Blob(
            b"abc", b"0123456789", signer="celestia1qypqxpq9qcrsszg2pvxq6rs0zqg3yyc5wgawu3"
        )
        with pytest.raises(
            ValueError, match="`signer_address` of blob does not match the current account address"
        ):
            await api.blob.submit(bad_signer_blob, signer_address=True)


async def test_blob_subscribe(node_provider):
    bridge, auth_token = await node_provider("bridge-0")
    client = Client(port=bridge.port["26658/tcp"])

    result = []

    async def submitter(api):
        for i in range(5):
            if i == 2:
                await api.blob.submit(Blob(b"abc", f"QWERTY{i}".encode()), signer_address=True)
            else:
                await api.blob.submit(Blob(b"qwe", f"QWERTY{i}".encode()), signer_address=True)

    async with client.connect(auth_token) as api:
        account_address = await api.state.account_address()
        submitter_tack = asyncio.create_task(submitter(api))
        try:
            async with asyncio.timeout(30):
                async for blob in api.blob.subscribe(b"qwe"):
                    result.append(blob)
                    if len(result) == 4:
                        break
        finally:
            submitter_tack.cancel()

    assert len(result) == 4
    assert tuple(item.blobs[0].namespace for item in result) == (Namespace(b"qwe"),) * 4
    assert (
        tuple(ext.bytes2address(item.blobs[0].signer) for item in result) == (account_address,) * 4
    )
    assert all(item.blobs[0].share_version == 1 for item in result)
