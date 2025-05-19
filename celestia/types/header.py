from dataclasses import dataclass

from celestia._celestia import types as ext  # noqa

from celestia.types.common import Base64


@dataclass
class ConsensusVersion:
    """Represents the version information for the consensus.

    Attributes:
        block (str): The block version.
        app (str): The application version.
    """

    block: str
    app: str


@dataclass
class Parts:
    """Represents the parts of the block.

    Attributes:
        total (int): The total number of parts.
        hash (str): The hash of the parts.
    """

    total: int
    hash: str


@dataclass
class BlockId:
    """Represents a block identifier, which includes a hash and parts.

    Attributes:
        hash (str): The hash of the block.
        parts (Parts): The parts information of the block.
    """

    hash: str
    parts: Parts

    def __init__(self, hash, parts):
        self.hash = hash
        self.parts = Parts(**parts)


@dataclass
class Header:
    """Represents the header information for the block.

    Attributes:
        version (ConsensusVersion): The consensus version.
        chain_id (str): The chain identifier.
        height (str): The height of the block.
        time (str): The time the block was created.
        last_block_id (BlockId): The identifier of the last block.
        last_commit_hash (str): The hash of the last commit.
        data_hash (str): The hash of the block data.
        validators_hash (str): The hash of the validators.
        next_validators_hash (str): The hash of the next validators.
        consensus_hash (str): The consensus hash.
        app_hash (str): The application hash.
        last_results_hash (str): The hash of the last results.
        evidence_hash (str): The hash of the evidence.
        proposer_address (str): The address of the proposer.
    """

    version: ConsensusVersion
    chain_id: str
    height: str
    time: str
    last_block_id: BlockId
    last_commit_hash: str
    data_hash: str
    validators_hash: str
    next_validators_hash: str
    consensus_hash: str
    app_hash: str
    last_results_hash: str
    evidence_hash: str
    proposer_address: str

    def __init__(
        self,
        version,
        chain_id,
        height,
        time,
        last_block_id,
        last_commit_hash,
        data_hash,
        validators_hash,
        next_validators_hash,
        consensus_hash,
        app_hash,
        last_results_hash,
        evidence_hash,
        proposer_address,
    ):
        self.version = ConsensusVersion(**version)
        self.chain_id = chain_id
        self.height = height
        self.time = time
        self.last_block_id = BlockId(**last_block_id)
        self.last_commit_hash = last_commit_hash
        self.data_hash = data_hash
        self.validators_hash = validators_hash
        self.next_validators_hash = next_validators_hash
        self.consensus_hash = consensus_hash
        self.app_hash = app_hash
        self.last_results_hash = last_results_hash
        self.evidence_hash = evidence_hash
        self.proposer_address = proposer_address


@dataclass
class PubKey:
    """Represents a public key used for validating a transaction.

    Attributes:
        type (str): The type of public key.
        value (Base64): The base64 encoded public key.
    """

    type: str
    value: Base64


@dataclass
class Validator:
    """Represents a validator in the consensus system.

    Attributes:
        address (str): The address of the validator.
        pub_key (PubKey): The public key of the validator.
        voting_power (str): The voting power of the validator.
        proposer_priority (str): The proposer priority of the validator.
    """

    address: str
    pub_key: PubKey
    voting_power: str
    proposer_priority: str

    def __init__(self, address, pub_key, voting_power, proposer_priority):
        self.address = address
        self.pub_key = PubKey(**pub_key)
        self.voting_power = voting_power
        self.proposer_priority = proposer_priority


@dataclass
class ValidatorSet:
    """Represents a set of validators and the proposer.

    Attributes:
        validators (tuple[Validator, ...]): The list of validators.
        proposer (Validator): The proposer of the block.
    """

    validators: tuple[Validator, ...]
    proposer: Validator

    def __init__(self, validators, proposer):
        self.validators = tuple(Validator(**validator) for validator in validators)
        self.proposer = Validator(**proposer)


@dataclass
class Signature:
    """Represents a signature for a commit block.

    Attributes:
        block_id_flag (int): The block ID flag.
        validator_address (str): The address of the validator signing the block.
        timestamp (str): The timestamp of the signature.
        signature (Base64): The base64 encoded signature.
    """

    block_id_flag: int
    validator_address: str
    timestamp: str
    signature: Base64

    def __init__(self, block_id_flag, validator_address, timestamp, signature):
        self.block_id_flag = block_id_flag
        self.validator_address = validator_address
        self.timestamp = timestamp
        self.signature = signature


@dataclass
class Commit:
    """Represents a commit for a block, including signatures.

    Attributes:
        height (int): The block height.
        round (int): The block round.
        block_id (BlockId): The ID of the block.
        signatures (tuple[Signature, ...]): The signatures of the validators.
    """

    height: int
    round: int
    block_id: BlockId
    signatures: tuple[Signature, ...]

    def __init__(self, height, round, block_id, signatures):
        self.height = height
        self.round = round
        self.block_id = BlockId(**block_id)
        self.signatures = tuple(Signature(**signature) for signature in signatures)


@dataclass
class Dah:
    """Represents the data availability header.

    Attributes:
        row_roots (tuple[Base64, ...]): The row roots.
        column_roots (tuple[Base64, ...]): The column roots.
    """

    row_roots: tuple[Base64, ...]
    column_roots: tuple[Base64, ...]

    def __init__(self, row_roots, column_roots):
        self.row_roots = tuple(row_root for row_root in row_roots)
        self.column_roots = tuple(column_root for column_root in column_roots)


@dataclass
class ExtendedHeader:
    """Represents an extended header containing header, validator set, commit, and DAH.

    Attributes:
        header (Header): The block header.
        validator_set (ValidatorSet): The validator set.
        commit (Commit): The commit information.
        dah (Dah): The data availability header.
    """

    header: Header
    validator_set: ValidatorSet
    commit: Commit
    dah: Dah

    def __init__(self, header, validator_set, dah, commit):
        self.header = Header(**header)
        self.validator_set = ValidatorSet(**validator_set)
        self.commit = Commit(**commit)
        self.dah = Dah(**dah)

    @staticmethod
    def deserializer(result: dict) -> "ExtendedHeader":
        """Deserializes the provided result into a `ExtendedHeader` object.

        Args:
            result (dict): The dictionary representation of a ExtendedHeader.

        Returns:
            ExtendedHeader: A deserialized ExtendedHeader object.
        """
        if result is not None:
            return ExtendedHeader(**result)


@dataclass
class State:
    """Represents a state for the block range.

    Attributes:
        id (int): The ID of the state.
        height (int): The height of the block.
        from_height (int): The starting height for the range.
        to_height (int): The ending height for the range.
        from_hash (str): The hash at the start of the range.
        to_hash (str): The hash at the end of the range.
        start (str): The start time of the state.
        end (str): The end time of the state.
    """

    id: int
    height: int
    from_height: int
    to_height: int
    from_hash: str
    to_hash: str
    start: str
    end: str

    def __init__(self, id, height, from_height, to_height, from_hash, to_hash, start, end):
        self.id = id
        self.height = height
        self.from_height = from_height
        self.to_height = to_height
        self.from_hash = from_hash
        self.to_hash = to_hash
        self.start = start
        self.end = end

    @staticmethod
    def deserializer(result: dict) -> "State":
        """Deserializes the provided result into a `State` object.

        Args:
            result (dict): The dictionary representation of a State.

        Returns:
            State: A deserialized State object.
        """
        if result is not None:
            return State(**result)
