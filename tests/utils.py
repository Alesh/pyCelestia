import logging
import os.path
import subprocess
from time import sleep

from tests.docker import Container

TESTNET_PATH = os.path.dirname(os.path.abspath(__file__))


def start_testnet() -> bool:
    args = ["docker", "compose", "-f", f"{TESTNET_PATH}/testnet/docker-compose.yml", "up", "-d"]
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode == 0:
        return True
    logging.error(proc.stderr.decode("utf8"))
    return False


def stop_testnet() -> bool:
    args = ["docker", "compose", "-f", f"{TESTNET_PATH}/testnet/docker-compose.yml", "down"]
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode == 0:
        return True
    logging.error(proc.stderr.decode("utf8"))
    return False


def get_auth_token(container: Container) -> str | None:
    args = [
        "docker",
        "exec",
        "-i",
        container.id,
        "celestia",
        container.image,
        "auth",
        "admin",
        "--p2p.network",
        "private",
    ]
    cnt = 10
    while cnt:
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode == 0:
            token = proc.stdout.decode("utf8").strip()
            return token
        sleep(1)
        cnt -= 1
        if not cnt:
            logging.error(proc.stderr.decode("utf8"))
