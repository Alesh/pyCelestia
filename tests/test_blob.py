import asyncio

import pytest

from celestia.node_api import Client
from celestia.types.common_types import Namespace, Blob


@pytest.mark.asyncio
async def test_send_blobs(node_provider):
    bridge, auth_token = await node_provider('bridge-0')
    client = Client(port=bridge.port['26658/tcp'])
    async with client.connect(auth_token) as api:
        blobs = await api.blob.get_all(1, b'abc')
        assert blobs == []

        result = await api.blob.submit(
            Blob(b'abc', b'0123456789'),
            Blob(b'abc', b'QWERTYUIOP'),
            Blob(b'xyz', b'ASDFGHJKL'),
        )

        assert len(result.commitments) == 3

        blobs = await api.blob.get_all(result.height, b'abc')
        assert len(blobs) == 2
        assert blobs[0].data == b'0123456789'
        assert blobs[0].commitment == result.commitments[0]

        assert blobs[1].data == b'QWERTYUIOP'
        assert blobs[1].commitment == result.commitments[1]

        blobs = await api.blob.get_all(result.height, b'xyz')
        assert len(blobs) == 1
        assert blobs[0].data == b'ASDFGHJKL'
        assert blobs[0].commitment == result.commitments[2]

        blob = await api.blob.get(1, b'abc', b'ASDFGHJKL')
        assert blob is None

        blob = await api.blob.get(result.height, b'abc', result.commitments[1])
        assert len(blobs) == 1
        assert blob.data == b'QWERTYUIOP'

        proof = await api.blob.get_proof(1, b'abc', b'ASDFGHJKL')
        assert proof == []

        proof = await api.blob.get_proof(result.height, b'abc', result.commitments[1])
        assert proof

        included = await api.blob.included(result.height, b'xyz', proof, result.commitments[1])
        assert not included

        included = await api.blob.included(result.height, b'abc', proof, result.commitments[1])
        assert included

        com_proof = await api.blob.get_commitment_proof(result.height, b'abc', result.commitments[1])
        assert com_proof is not None

        com_proof = await api.blob.get_commitment_proof(result.height, b'abc', result.commitments[1])
        assert com_proof is not None


@pytest.mark.asyncio
async def test_blob_exceptions(node_provider):
    bridge, auth_token = await node_provider('bridge-0')
    client = Client(port=bridge.port['26658/tcp'])
    async with client.connect(auth_token) as api:
        with pytest.raises(ValueError):
            await api.blob.get_all(18446744073709551615, b'abc')
        with pytest.raises(ValueError):
            await api.blob.get_all(0, b'abc')
        with pytest.raises(ValueError):
            await api.blob.get_all(-1, b'abc')

        with pytest.raises(ValueError):
            await api.blob.get(18446744073709551615, b'abc', b'ASDFGHJKL')
        with pytest.raises(ValueError):
            await api.blob.get(0, b'abc', b'ASDFGHJKL')
        with pytest.raises(ValueError):
            await api.blob.get(-1, b'abc', b'ASDFGHJKL')

        with pytest.raises(ValueError):
            await api.blob.get_proof(18446744073709551615, b'abc', b'ASDFGHJKL')
        with pytest.raises(ValueError):
            await api.blob.get_proof(0, b'abc', b'ASDFGHJKL')
        with pytest.raises(ValueError):
            await api.blob.get_proof(-1, b'abc', b'ASDFGHJKL')

        with pytest.raises(TypeError):
            Blob(b'abc', None)
        with pytest.raises(ValueError):
            Blob(123, b'ASDFGHJKL')


@pytest.mark.asyncio
async def test_blob_subscribe(node_provider):
    bridge, auth_token = await node_provider('bridge-0')
    client = Client(port=bridge.port['26658/tcp'])

    result = []

    async def submitter(api):
        for i in range(5):
            if i == 2:
                await api.blob.submit(Blob(b'abc', f'QWERTY{i}'.encode()))
            else:
                await api.blob.submit(Blob(b'qwe', f'QWERTY{i}'.encode()))

    async with client.connect(auth_token) as api:
        submitter_tack = asyncio.create_task(submitter(api))
        try:
            async with asyncio.timeout(30):
                async for blob in api.blob.subscribe(b'qwe'):
                    result.append(blob)
                    if len(result) == 4:
                        break
        finally:
            submitter_tack.cancel()

    assert len(result) == 4
    assert tuple(item.blobs[0].namespace for item in result) == (Namespace(b'qwe'),) * 4
