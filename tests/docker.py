import subprocess
from dataclasses import dataclass
from io import StringIO


@dataclass
class Container:
    id: str
    name: str
    image: str
    port: dict[str, int]

    def __init__(self, id: str, name: str, image: str, ports: str):
        self.id = id
        self.name = name
        self.image = image
        ports = [s.strip().split("->") for s in ports.split(",")]
        self.port = dict((p[1], int(p[0].split(":")[-1])) for p in ports if len(p) == 2)


class Containers(list[Container]):

    def __init__(self, prefix: str):
        result = list()
        self._prefix = prefix
        proc = subprocess.run(["docker", "ps"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        f = StringIO(proc.stdout.decode("utf8"))
        ready = f.readline()
        if ready:
            ready = ready.replace("CONTAINER ID", "CONTAINER_ID")
            b = [ready.index(word) for word in ready.split()] + [1024]
            while True:
                if line := f.readline():
                    line.split()
                    c = [line[b[N] : b[N + 1]].strip() for N in range(len(b) - 1)]
                    if c[6].startswith(self._prefix):
                        result.append(Container(c[0], c[6], c[1], c[5]))
                else:
                    break
        super().__init__(result)

    def get_by_id(self, id: str) -> Container | None:
        if result := [container for container in self if container.id == id]:
            return result[0]

    def get_by_name(self, name: str) -> tuple[Container, ...]:
        return tuple(
            sorted(
                [
                    container
                    for container in self
                    if container.name.startswith("-".join([self._prefix, name, ""]))
                ],
                key=lambda container: container.name,
            )
        )

    def get_by_name_first(self, name: str) -> Container | None:
        if result := self.get_by_name(name):
            return result[0]
