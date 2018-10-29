from functools import total_ordering

from .run import run


@total_ordering
class Command:
    def __init__(self, name, cmd, type_obj):
        self.name = name
        self.cmd = cmd
        self.type_obj = type_obj

    def __str__(self):
        return f"{self.name} <- {self.type_obj._path}"

    @property
    def base_command_name(self):
        return self.name.split("--")[0]

    @property
    def phase(self):
        parts = self.name.split("--")
        phase = parts[1] if len(parts) > 1 else None
        return phase

    def run(self):
        if isinstance(self.cmd, str):
            run(self.cmd)
        elif isinstance(self.cmd, list):
            [run(x) for x in self.cmd]
        else:
            self.cmd()

    def __eq__(self, other):
        return (self.name, self.cmd, self.type_obj) == (
            other.name,
            other.cmd,
            other.type_obj,
        )

    def __lt__(self, other):
        if self.phase == other.phase:
            return self.name < other.name

        phase_order = {"pre": 0, None: 1, "post": 2}
        return phase_order[self.phase] < phase_order[other.phase]
