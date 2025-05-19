from dataclasses import dataclass


@dataclass
class Worker:
    job_type: str
    current: int
    from_: int
    to: int


@dataclass
class SamplingStats:
    head_of_sampled_chain: int
    head_of_catchup: int
    network_head_height: int
    concurrency: int
    catch_up_done: bool
    is_running: bool
    workers: tuple[Worker, ...] = None

    def __init__(
        self,
        head_of_sampled_chain,
        head_of_catchup,
        network_head_height,
        concurrency,
        catch_up_done,
        is_running,
        workers=None,
    ):
        self.head_of_sampled_chain = head_of_sampled_chain
        self.head_of_catchup = head_of_catchup
        self.network_head_height = network_head_height
        self.concurrency = concurrency
        self.catch_up_done = catch_up_done
        self.is_running = is_running
        self.workers = (
            tuple(Worker(**worker) for worker in workers) if workers is not None else None
        )

    @staticmethod
    def deserializer(result):
        if result is not None:
            return SamplingStats(**result)
