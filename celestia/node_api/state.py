from typing import Callable

from celestia._celestia import types  # noqa

from celestia.types import TxConfig, Blob, Unpack
from celestia.types.state import Balance, TXResponse, QueryUnbondingDelegationResponse, \
    QueryDelegationResponse, QueryRedelegationResponse
from ._RPC import Wrapper


class StateClient(Wrapper):
    """ Client for interacting with Celestia's State API."""

    async def account_address(self) -> str:
        """ Retrieves the address of the node's account/signer

        Returns:
            str: The address of the node's account.
        """
        return await self._rpc.call("state.AccountAddress")

    async def balance(self, *, deserializer: Callable | None = None) -> Balance:
        """ Retrieves the Celestia coin balance for the node's account/signer
        and verifies it against the corresponding block's AppHash.

        Args:
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.state.Balance.deserializer`.

        Returns:
            Balance: The balance of the node's account.
        """

        deserializer = deserializer if deserializer is not None else Balance.deserializer

        return await self._rpc.call("state.Balance", (), deserializer)

    async def balance_for_address(self, address: str, *, deserializer: Callable | None = None) -> Balance:
        """ Retrieves the Celestia coin balance for the given address and verifies the returned balance
        against the corresponding block's AppHash. NOTE: the balance returned is the balance reported
        by the block right before the node's current head (head-1). This is due to the fact that for
        block N, the block's `AppHash` is the result of applying the previous block's transaction list.

        Args:
            address (str): The address to query balance for.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.state.Balance.deserializer`.

        Returns:
            Balance: The balance of the given address.
        """

        deserializer = deserializer if deserializer is not None else Balance.deserializer

        return await self._rpc.call("state.BalanceForAddress", (address,), deserializer)

    async def begin_redelegate(self, src_val_addr: str, dst_val_addr: str, amount: int, *,
                               deserializer: Callable | None = None, **config: Unpack[TxConfig]) -> TXResponse:
        """ Sends a user's delegated tokens to a new validator for redelegation.

        Args:
            src_val_addr (str): Source validator address.
            dst_val_addr (str): Destination validator address.
            amount (int): Amount to redelegate.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.state.TXResponse.deserializer`.
            **config(TxConfig): Additional transaction configuration.

        Returns:
            TXResponse: Transaction response.
        """

        deserializer = deserializer if deserializer is not None else TXResponse.deserializer

        return await self._rpc.call("state.BeginRedelegate", (src_val_addr, dst_val_addr, str(amount), config),
                                    deserializer)

    async def cancel_unbonding_delegation(self, val_addr: str, amount: int, height: int, *,
                                          deserializer: Callable | None = None,
                                          **config: Unpack[TxConfig]) -> TXResponse:
        """ Cancels a user's pending undelegation from a validator.

        Args:
            val_addr (str): Validator address.
            amount (int): Amount to cancel unbonding.
            height (int): Block height at which unbonding was initiated.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.state.TXResponse.deserializer`.
            **config(TxConfig): Additional transaction configuration.

        Returns:
            TXResponse: Transaction response.
        """

        deserializer = deserializer if deserializer is not None else TXResponse.deserializer

        return await self._rpc.call("state.CancelUnbondingDelegation", (val_addr, str(amount), str(height), config),
                                    deserializer)

    async def delegate(self, del_addr: str, amount: int, *, deserializer: Callable | None = None,
                       **config: Unpack[TxConfig]) -> TXResponse:
        """ Sends a user's liquid tokens to a validator for delegation.

        Args:
            del_addr (str): Delegator address.
            amount (int): Amount to delegate.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.state.TXResponse.deserializer`.
            **config(TxConfig): Additional transaction configuration.

        Returns:
            TXResponse: Transaction response.
        """

        deserializer = deserializer if deserializer is not None else TXResponse.deserializer

        return await self._rpc.call("state.Delegate", (del_addr, str(amount), config), deserializer)

    async def grant_fee(self, grantee: str, amount: int, *, deserializer: Callable | None = None,
                        **config: Unpack[TxConfig]) -> TXResponse:
        """ Grants a fee allowance to the specified grantee.

        Args:
            grantee (str): Address of the grantee.
            amount (int): Amount of fee allowance.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.state.TXResponse.deserializer`.
            **config(TxConfig): Additional transaction configurations.

        Returns:
            TXResponse: Response of the grant fee transaction.
        """

        deserializer = deserializer if deserializer is not None else TXResponse.deserializer

        return await self._rpc.call("state.GrantFee", (grantee, str(amount), config), deserializer)

    async def query_delegation(self, val_addr: str, *, deserializer: Callable | None = None) -> QueryDelegationResponse:
        """ Retrieves the delegation information between a delegator and a validator.

        Args:
            val_addr (str): Validator address.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.state.QueryDelegationResponse.deserializer`.

        Returns:
            QueryDelegationResponse: Delegation information.
        """

        deserializer = deserializer if deserializer is not None else QueryDelegationResponse.deserializer

        return await self._rpc.call("state.QueryDelegation", (val_addr,), deserializer)

    async def query_redelegations(self, src_val_addr: str, dst_val_addr: str, *,
                                  deserializer: Callable | None = None) -> QueryRedelegationResponse:
        """ Retrieves the status of the redelegations between a delegator and a validator.

        Args:
            src_val_addr (str): Source validator address.
            dst_val_addr (str): Destination validator address.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.state.QueryRedelegationResponse.deserializer`.

        Returns:
            QueryRedelegationResponse: Redelegation details.
        """

        deserializer = deserializer if deserializer is not None else QueryRedelegationResponse.deserializer

        return await self._rpc.call("state.QueryRedelegations", (src_val_addr, dst_val_addr), deserializer)

    async def query_unbonding(self, val_addr: str, *,
                              deserializer: Callable | None = None) -> QueryUnbondingDelegationResponse:
        """ Retrieves the unbonding status between a delegator and a validator.

        Args:
            val_addr (str): Validator address.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.state.QueryUnbondingDelegationResponse.deserializer`.

        Returns:
           QueryUnbondingDelegationResponse: Unbonding status.
        """

        deserializer = deserializer if deserializer is not None else QueryUnbondingDelegationResponse.deserializer

        return await self._rpc.call("state.QueryUnbonding", (val_addr,), deserializer)

    async def revoke_grant_fee(self, grantee: str, *, deserializer: Callable | None = None,
                               **config: Unpack[TxConfig]) -> TXResponse:
        """ Revokes a previously granted fee allowance.

        Args:
            grantee (str): Address of the grantee whose allowance is being revoked.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.state.TXResponse.deserializer`.
            **config(TxConfig): Additional transaction configurations.

        Returns:
            TXResponse: Response of the revoke grant fee transaction.
        """

        deserializer = deserializer if deserializer is not None else TXResponse.deserializer

        return await self._rpc.call("state.RevokeGrantFee", (grantee, config), deserializer)

    async def submit_pay_for_blob(self, blob: Blob, *blobs: Blob, **config: Unpack[TxConfig]) -> int:
        """ Builds, signs and submits a PayForBlob transaction.

        Args:
            blob (Blob): The first blob to be included in the transaction.
            *blobs (Blob): Additional blobs.
            **config(TxConfig): Additional transaction configurations.

        Returns:
            int: Transaction ID of the submitted PayForBlob transaction.
        """
        blobs = tuple(types.normalize_blob(blob) if blob.commitment is None else blob for blob in (blob, *blobs))
        return await self._rpc.call("state.SubmitPayForBlob", (blobs, config))

    async def transfer(self, to: str, amount: int, *, deserializer: Callable | None = None,
                       **config: Unpack[TxConfig]) -> TXResponse:
        """ Sends the given amount of coins from default wallet of the node to the given account address.

        Args:
            to (str): Recipient address.
            amount (int): Amount to transfer.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.state.TXResponse.deserializer`.
            **config(TxConfig): Additional transaction configuration.

        Returns:
            TXResponse: Transaction response.
        """

        deserializer = deserializer if deserializer is not None else TXResponse.deserializer

        return await self._rpc.call("state.Transfer", (to, str(amount), config), deserializer)

    async def undelegate(self, del_addr: str, amount: int, *, deserializer: Callable | None = None,
                         **config: Unpack[TxConfig]) -> TXResponse:
        """ Undelegates a user's delegated tokens, unbonding them from the current validator.

        Args:
            del_addr (str): Delegator address.
            amount (int): Amount to undelegate.
            deserializer (Callable | None): Custom deserializer. Defaults to :meth:`~celestia.types.state.TXResponse.deserializer`.
            **config(TxConfig): Additional transaction configurations.

        Returns:
            TXResponse: Response of the undelegation transaction.
        """

        deserializer = deserializer if deserializer is not None else TXResponse.deserializer

        return await self._rpc.call("state.Undelegate", (del_addr, str(amount), config), deserializer)
