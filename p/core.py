import os

import click

from .types import known_types
from . import git


def discover_commands(in_path=".", ordered=True):
    commands = {}

    paths = os.listdir(in_path)

    # iterative the types in a specific order,
    # if duplicates, the first match is used for each command name
    for cmd_type in known_types:
        for p in paths:
            full_p = os.path.join(in_path, p)
            if cmd_type._recognizes_path(full_p):
                obj = cmd_type(full_p)

                for command in obj._available_commands():
                    if command.base_command_name not in commands:
                        commands[command.base_command_name] = {}

                    if command.name not in commands[command.base_command_name]:
                        commands[command.base_command_name][command.name] = command

    # recursively add any p- subdirectories
    subdirs = [x for x in paths if os.path.basename(x).startswith("p-")]
    for sub in subdirs:
        subdir_commands = discover_commands(os.path.join(in_path, sub), ordered=False)
        for sk, sv in subdir_commands.items():
            # update all our commands, but with the current having priority over the subdir
            commands[sk] = {**sv, **commands.get(sk, {})}

    if ordered:
        return {k: sorted(commands[k].values()) for k in sorted(commands.keys())}
    else:
        return commands


def do_command(command, commands):
    # commands = discover_commands()

    if command not in commands:
        click.secho("Not sure what to run", fg="red")
        return False

    if command == "setup" or command in git.GIT_COMMANDS:
        git.install_hooks(commands)

    for subcommand in commands[command]:
        click.secho(f"Running command: {subcommand}")
        subcommand.run()
