import typing as t
from dataclasses import dataclass

from celestia._celestia import types as ext  # noqa


@dataclass
class Balance:
    """ Represents the balance of a particular denomination.

    Attributes:
        amount (int): The amount of the balance.
        denom (str): The denomination of the balance.
    """
    amount: int
    denom: str

    def __init__(self, amount: int, denom: str):
        self.amount = int(amount)
        self.denom = denom

    @staticmethod
    def deserializer(result: dict) -> 'Balance':
        """ Deserialize a result dictionary into a Balance object.

        Args:
            result (dict): The dictionary representation of a Balance.

        Returns:
            Balance: The deserialized Balance object.
        """
        if result is not None:
            return Balance(**result)


@dataclass
class TXResponse:
    """ Represents the response for a transaction.

    Attributes:
        height (int): The block height of the transaction.
        txhash (str): The transaction hash.
        logs (tuple[t.Any] | None): Logs associated with the transaction, if any.
        events (tuple[t.Any, ...] | None): Events triggered by the transaction, if any.
    """
    height: int
    txhash: str
    logs: tuple[t.Any] | None = None
    events: tuple[t.Any, ...] | None = None

    def __init__(self, height, txhash, logs, events):
        self.height = int(height)
        self.txhash = txhash
        self.logs = tuple(log for log in logs) if logs else None
        self.events = tuple(event for event in events) if events else None

    @staticmethod
    def deserializer(result: dict) -> 'TXResponse':
        """ Deserialize a result dictionary into a TXResponse object.

        Args:
            result (dict): The dictionary representation of a TXResponse.

        Returns:
            TXResponse: The deserialized TXResponse object.
        """
        if result is not None:
            return TXResponse(**result)


@dataclass
class Delegation:
    """ Represents a delegation of tokens to a validator.

    Attributes:
        delegator_address (str): The address of the delegator.
        validator_address (str): The address of the validator.
        shares (float): The amount of shares in the delegation.
    """
    delegator_address: str
    validator_address: str
    shares: float

    def __init__(self, delegator_address, validator_address, shares):
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.shares = float(shares)


@dataclass
class DelegationResponse:
    """ Represents the response for a delegation query.

    Attributes:
       delegation (Delegation): The delegation details.
       balance (Balance): The balance associated with the delegation.
    """
    delegation: Delegation
    balance: Balance

    def __init__(self, delegation, balance):
        self.delegation = Delegation(**delegation)
        self.balance = Balance(**balance)


@dataclass
class QueryDelegationResponse:
    """ Represents the response for a delegation query.

    Attributes:
        delegation_response (DelegationResponse): The delegation response details.
    """
    delegation_response: DelegationResponse

    def __init__(self, delegation_response):
        self.delegation_response = DelegationResponse(**delegation_response)

    @staticmethod
    def deserializer(result: dict) -> 'QueryDelegationResponse':
        """ Deserialize a result dictionary into a QueryDelegationResponse object.

        Args:
            result (dict): The dictionary representation of a QueryDelegationResponse.

        Returns:
            QueryDelegationResponse: The deserialized QueryDelegationResponse object.
        """
        if result is not None:
            return QueryDelegationResponse(**result)


@dataclass
class RedelegationEntry:
    """ Represents a redelegation entry.

    Attributes:
       creation_height (int): The block height when the redelegation was created.
       completion_time (str): The completion time of the redelegation.
       initial_balance (int): The initial balance of the redelegation.
       shares_dst (float): The amount of shares transferred to the destination validator.
    """
    creation_height: int
    completion_time: str
    initial_balance: int
    shares_dst: float

    def __init__(self, creation_height, completion_time, initial_balance, shares_dst):
        self.creation_height = creation_height
        self.completion_time = completion_time
        self.initial_balance = int(initial_balance)
        self.shares_dst = float(shares_dst)


@dataclass
class Redelegation:
    """ Represents a redelegation of tokens from one validator to another.

    Attributes:
        delegator_address (str): The address of the delegator.
        validator_src_address (str): The address of the source validator.
        validator_dst_address (str): The address of the destination validator.
        entries (tuple[RedelegationEntry, ...]): A list of redelegation entries.
    """
    delegator_address: str
    validator_src_address: str
    validator_dst_address: str
    entries: tuple[RedelegationEntry, ...]

    def __init__(self, delegator_address, validator_src_address, validator_dst_address, entries):
        self.delegator_address = delegator_address
        self.validator_src_address = validator_src_address
        self.validator_dst_address = validator_dst_address
        self.entries = tuple(RedelegationEntry(**entry) for entry in entries) if entries is not None else []


@dataclass
class RedelegationResponseEntry:
    """ Represents a redelegation response entry.

    Attributes:
        redelegation_entry (RedelegationEntry): The redelegation entry details.
        balance (int): The balance of the redelegation entry.
    """
    redelegation_entry: RedelegationEntry
    balance: int

    def __init__(self, redelegation_entry, balance):
        self.redelegation_entry = RedelegationEntry(**redelegation_entry)
        self.balance = int(balance)


@dataclass
class RedelegationResponse:
    """ Represents the response for a redelegation query.

    Attributes:
        redelegation (Redelegation): The redelegation details.
        entries (tuple[RedelegationResponseEntry, ...]): A list of redelegation response entries.
    """
    redelegation: Redelegation
    entries: tuple[RedelegationResponseEntry, ...]

    def __init__(self, redelegation, entries):
        self.redelegation = Redelegation(**redelegation)
        self.entries = tuple(RedelegationResponseEntry(**entry) for entry in entries)


@dataclass
class Pagination:
    """ Represents pagination information.

    Attributes:
        next_key (str | None): The key for the next page of results.
        total (int | None): The total number of results.
    """
    next_key: str = None
    total: int = None


@dataclass
class QueryRedelegationResponse:
    """ Represents the response for a query to retrieve redelegations.

    Attributes:
        redelegation_responses (tuple[RedelegationResponse, ...]): A list of redelegation responses.
        pagination (Pagination): Pagination information for the query results.
    """
    redelegation_responses: tuple[RedelegationResponse, ...]
    pagination: Pagination

    def __init__(self, redelegation_responses, pagination=None):
        self.redelegation_responses = tuple(
            RedelegationResponse(**redelegation_response) for redelegation_response in redelegation_responses)
        self.pagination = Pagination(**pagination) if pagination else None

    @staticmethod
    def deserializer(result: dict) -> 'QueryRedelegationResponse':
        """ Deserialize a result dictionary into a QueryRedelegationResponse object.

        Args:
            result (dict): The dictionary representation of a QueryRedelegationResponse.

        Returns:
            QueryRedelegationResponse: The deserialized QueryRedelegationResponse object.
        """
        if result is not None:
            return QueryRedelegationResponse(**result)


@dataclass
class UnbondEntry:
    """ Represents an unbonding entry for a validator.

    Attributes:
        creation_height (int): The block height when the unbonding was created.
        completion_time (str): The completion time of the unbonding.
        initial_balance (int): The initial balance of the unbonding.
        balance (int): The current balance after unbonding.
    """
    creation_height: int
    completion_time: str
    initial_balance: int
    balance: int

    def __init__(self, creation_height, completion_time, initial_balance, balance):
        self.creation_height = creation_height
        self.completion_time = completion_time
        self.initial_balance = int(initial_balance)
        self.balance = int(balance)


@dataclass
class Unbond:
    """ Represents an unbonding of tokens from a validator.

    Attributes:
        delegator_address (str): The address of the delegator.
        validator_address (str): The address of the validator.
        entries (tuple[UnbondEntry, ...]): A list of unbonding entries.
    """
    delegator_address: str
    validator_address: str
    entries: tuple[UnbondEntry, ...]

    def __init__(self, delegator_address, validator_address, entries):
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.entries = tuple(UnbondEntry(**entry) for entry in entries)


@dataclass
class QueryUnbondingDelegationResponse:
    """ Represents the response for a query to retrieve unbonding delegations.

    Attributes:
        unbond (Unbond): The unbonding details.
    """
    unbond: Unbond

    def __init__(self, unbond):
        self.unbond = Unbond(**unbond)

    @staticmethod
    def deserializer(result: dict) -> 'QueryUnbondingDelegationResponse':
        """ Deserialize a result dictionary into a QueryUnbondingDelegationResponse object.

        Args:
            result (dict): The dictionary representation of a QueryUnbondingDelegationResponse.

        Returns:
            QueryUnbondingDelegationResponse: The deserialized QueryUnbondingDelegationResponse object.
        """
        if result is not None:
            return QueryUnbondingDelegationResponse(**result)
