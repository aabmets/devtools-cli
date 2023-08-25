#
#   MIT License
#
#   Copyright (c) 2023, Mattias Aabmets
#
#   The contents of this file are subject to the terms and conditions defined in the License.
#   You may not use, modify, or distribute this file except in compliance with the License.
#
#   SPDX-License-Identifier: MIT
#
from pathlib import Path
from datetime import date
from rich.console import Console
from typer import Typer, Option
from typing_extensions import Annotated
from devtools_cli.utils import *
from devtools_cli.commands.version.models import VersionConfig


app = Typer(name="log", help="Manages project changelog file.")
console = Console(soft_wrap=True)

CHANGELOG_FILENAME = "CHANGELOG.md"
SECTION_LEVEL = '###'
HEADER = [
    "# Changelog",
    "",
    "All notable changes to this project will be documented in this file.  ",
    "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), "
    "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).  "
]


ChangesOpt = Annotated[str, Option(
    '--changes', '-c', show_default=False, help=''
    'Changes to be added into the next version section of the changelog file.'
)]


@app.command(name="insert", epilog="Example: devtools log next --changes \"changes\"")
def cmd_next(changes: ChangesOpt = ''):
    config_file: Path = find_local_config_file(init_cwd=True)
    logfile = config_file.parent / CHANGELOG_FILENAME

    if not logfile.exists():
        logfile.touch(exist_ok=True)
        with logfile.open('w') as file:
            file.write('\n'.join(HEADER))

    with logfile.open('r') as file:
        lines = file.read().splitlines()

    existing = []
    for i, line in enumerate(lines):
        if line.startswith(SECTION_LEVEL):
            existing = lines[i:]
            break

    config: VersionConfig = read_local_config_file(VersionConfig)
    title = f"{SECTION_LEVEL} [{config.app_version}] - {date.today().isoformat()}  "
    changes = [c if c.startswith("- ") else f"- {c}" for c in changes.splitlines()]

    with logfile.open('w') as file:
        contents = [*HEADER, '', title, '', *changes, '', *existing]
        file.write('\n'.join(contents))

    verb = "updated" if existing else "created"
    console.print(f"Successfully {verb} the {CHANGELOG_FILENAME} file.")


VersionOpt = Annotated[str, Option(
    '--version', '-v', show_default=False, help=''
    'A semantic version identifier of a section in the changelog file.'
)]


@app.command(name="view", epilog="Example: devtools log view --version 1.2.3")
def cmd_view(version: VersionOpt = None):
    config_file = find_local_config_file(init_cwd=False)
    if config_file is None:
        console.print("ERROR! Project is not initialized with a devtools config file!")
        raise SystemExit()

    logfile = config_file.parent / CHANGELOG_FILENAME
    if not logfile.exists():
        console.print("ERROR! Cannot view sections of a non-existent CHANGELOG.md file!")
        raise SystemExit()

    with logfile.open('r') as file:
        lines = file.read().splitlines()

    line: str
    section = f"{SECTION_LEVEL} [{version}]" if version else f"{SECTION_LEVEL}"
    for i, line in enumerate(lines):
        if line.startswith(section):
            end = len(lines)
            for j in range(i + 1, end):
                if lines[j].startswith(f"{SECTION_LEVEL}"):
                    end = j
                    break

            ver_type = 'Version' if version else "Latest version"
            ver_ident = version or line.split('[')[-1].split(']')[0]
            print(f"{ver_type} {ver_ident} changelog:")

            contents = lines[i + 2:end]
            for c in contents:
                print(c)
            if contents[-1] != '':
                print('')
            return

    console.print(f"The changelog does not contain a section for version {version}.")
