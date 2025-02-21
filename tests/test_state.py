import asyncio

import pytest

from celestia.node_api import Client
from celestia.node_api.blob import Blob


@pytest.mark.asyncio
async def test_account_address(node_provider, bridge_addresses):
    bridge, auth_token = await node_provider('bridge-0')
    client = Client(port=bridge.port['26658/tcp'])
    async with client.connect(auth_token) as api:
        address = await api.state.account_address()
        assert address in bridge_addresses


@pytest.mark.asyncio
async def test_account_balance(node_provider):
    bridge, auth_token = await node_provider('bridge-0')
    client = Client(port=bridge.port['26658/tcp'])
    async with client.connect(auth_token) as api:
        balance = await api.state.balance()
        assert balance.amount > 100000000000000
        assert balance.denom == 'utia'
        address = await api.state.account_address()
        address_balance = await api.state.balance_for_address(address)
        assert address_balance == balance


@pytest.mark.asyncio
async def test_transfer(node_provider):
    bridge1, auth_token1 = await node_provider('bridge-0')
    client1 = Client(port=bridge1.port['26658/tcp'])
    bridge2, auth_token2 = await node_provider('bridge-1')
    client2 = Client(port=bridge2.port['26658/tcp'])
    bridge3, auth_token3 = await node_provider('bridge-2')
    client3 = Client(port=bridge3.port['26658/tcp'])

    async with client3.connect(auth_token3) as api:
        address3 = await api.state.account_address()
        start_balance3 = await api.state.balance()
        await api.blob.submit(Blob(b'abc', b'client3'))

    async with client2.connect(auth_token2) as api:
        address2 = await api.state.account_address()
        start_balance2 = await api.state.balance()
        await api.blob.submit(Blob(b'abc', b'client2'))

    async with client1.connect(auth_token1) as api:
        start_balance1 = await api.state.balance()
        await api.blob.submit(Blob(b'abc', b'client1'))
        await asyncio.sleep(5)
        new_balance3 = await api.state.balance_for_address(address3)
        new_balance2 = await api.state.balance_for_address(address2)
        new_balance1 = await api.state.balance()

        assert new_balance3.amount < start_balance3.amount
        assert new_balance2.amount < start_balance2.amount
        assert new_balance1.amount < start_balance1.amount

        await api.state.transfer(address3, 20)
        await api.state.transfer(address2, 20)

        await asyncio.sleep(5)
        assert (await api.state.balance()).amount < new_balance1.amount - 40
        assert (await api.state.balance_for_address(address2)).amount == new_balance2.amount + 20
        assert (await api.state.balance_for_address(address3)).amount == new_balance3.amount + 20

        await api.state.grant_fee(address2, 10000)
        await api.state.revoke_grant_fee(address2)


@pytest.mark.asyncio
async def test_undelegate(node_provider, validator_addresses):
    bridge, auth_token = await node_provider('bridge-0')
    client = Client(port=bridge.port['26658/tcp'])
    validator1 = validator_addresses[0]
    try:
        async with client.connect(auth_token) as api:
            await api.blob.submit(Blob(b'abc', b'client3'))

            try:
                amount_before_delegation = (
                    await api.state.query_delegation(validator1)).delegation_response.balance.amount
            except ValueError:
                amount_before_delegation = 0

            await api.state.delegate(validator1, 10000)
            await api.state.undelegate(validator1, 1000)
            assert (await api.state.query_delegation(
                validator1)).delegation_response.balance.amount == amount_before_delegation + 9000

            query_unbonding1 = await api.state.query_unbonding(validator1)
            undelegate = await api.state.undelegate(validator1, 9000)
            query_unbonding2 = await api.state.query_unbonding(validator1)
            assert len(query_unbonding1.unbond.entries) + 1 == len(query_unbonding2.unbond.entries)

            await api.state.cancel_unbonding_delegation(validator1, 3000, undelegate.height)
            query_unbonding3 = await api.state.query_unbonding(validator1)
            assert query_unbonding2.unbond.entries[-1].balance - 3000 == query_unbonding3.unbond.entries[-1].balance

            query_delegation = await api.state.query_delegation(validator1)
            with pytest.raises(ValueError):
                await api.state.undelegate(validator1, query_delegation.delegation_response.balance.amount + 1000)
            await api.state.undelegate(validator1, query_delegation.delegation_response.balance.amount)

    except ValueError as e:
        if 'too many unbonding delegation entries for' in e.args[0]:
            print(""" The unbound pool is full. To test the functions undelegate, query_unbonding,
                  cancel_unbonding_delegation the network needs to be recreated
                  """)
        else:
            raise e


@pytest.mark.asyncio
async def test_delegating(node_provider, validator_addresses):
    bridge, auth_token = await node_provider('bridge-0')
    client = Client(port=bridge.port['26658/tcp'])
    validator1, validator2, validator3 = validator_addresses
    try:
        async with client.connect(auth_token) as api:
            await api.blob.submit(Blob(b'abc', b'client3'))

            try:
                amount_validator1_before_delegation = (
                    await api.state.query_delegation(validator1)).delegation_response.balance.amount
            except ValueError:
                amount_validator1_before_delegation = 0
            try:
                amount_validator2_before_delegation = (
                    await api.state.query_delegation(validator2)).delegation_response.balance.amount
            except ValueError:
                amount_validator2_before_delegation = 0

            await api.state.delegate(validator1, 10000)
            assert (await api.state.query_delegation(
                validator1)).delegation_response.balance.amount == amount_validator1_before_delegation + 10000

            await api.state.begin_redelegate(validator1, validator2, 9999)
            await asyncio.sleep(5)
            assert (await api.state.query_delegation(
                validator1)).delegation_response.balance.amount == amount_validator1_before_delegation + 1
            assert (await api.state.query_delegation(
                validator2)).delegation_response.balance.amount == amount_validator2_before_delegation + 9999
            querry = await api.state.query_redelegations(validator1, validator2)
            assert querry.redelegation_responses[0].entries[-1].balance == 9999

            with pytest.raises(ValueError):
                await api.state.begin_redelegate(validator1, validator1, 3000)
            with pytest.raises(ValueError):
                await api.state.query_redelegations(validator1, validator1)
            with pytest.raises(ValueError):
                await api.state.query_redelegations(validator2, validator1)
    except ValueError as e:
        if 'too many redelegation entries for (delegator, src-validator, dst-validator)' in e.args[0]:
            print(""" The redelegation entries is full. To test the functions query_delegation, delegate,
                  begin_redelegate the network needs to be recreated
                  """)
        else:
            raise e
