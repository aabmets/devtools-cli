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
from rich.prompt import Prompt
from rich.console import Console
from typer import Typer, Option
from typing_extensions import Annotated
from devtools_cli.commands.version.models import VersionConfig
from devtools_cli.utils import *
from .helpers import *
from .errors import *


app = Typer(name="log", help="Manages project changelog file.")
console = Console(soft_wrap=True)


NewSectionOpt = Annotated[bool, Option(
    '--new', '-n', show_default=False, help=''
    'If the changes should be added to a new version section.'
)]


@app.command(name="add", epilog="Example: devtools log add --new")
def cmd_add(new_section: NewSectionOpt = False):
    """
    Interactively add changes into the changelog file.
    """
    config: VersionConfig = read_local_config_file(VersionConfig)
    version = config.app_version

    existing = read_existing_content(init_cwd=True)
    if not existing and not new_section:
        new_section = True
    elif new_section and not validate_unique_version(version, existing):
        console.print("ERROR! Cannot insert a duplicate version section into the changelog file.\n")
        raise SystemExit()

    console.print("Please provide the changelog contents: (Press Enter on empty prompt to apply.)")

    changes = []
    while True:
        change = Prompt.ask("Entry")
        if change == '':
            break
        changes.append(change)
    conformed = conform_changes(changes)

    if not changes:
        console.print("Did not alter the changelog file.\n")
    else:
        console.print("Added the provided changes into the changelog file.\n")

    if new_section:
        write_new_section(version, conformed, existing)
    else:
        update_latest_section(conformed, existing)


ChangesOpt = Annotated[str, Option(
    '--changes', '-c', show_default=False, help=''
    'Changes to be added into the next version section of the changelog file.'
)]


@app.command(name="insert", epilog="Example: devtools log insert --changes \"changes\"")
def cmd_insert(changes: ChangesOpt = ''):
    """
    This command is intended to be used in a bash script to insert
    variable contents into a new version section of a changelog file.
    """
    config: VersionConfig = read_local_config_file(VersionConfig)
    version = config.app_version

    existing = read_existing_content(init_cwd=True)
    if not validate_unique_version(version, existing):
        console.print("ERROR! Cannot insert a duplicate version section into the changelog file.\n")
        raise SystemExit()

    conformed = conform_changes(changes)
    write_new_section(version, conformed, existing)

    verb = "updated" if existing else "created"
    console.print(f"Successfully {verb} the changelog file.")


VersionOpt = Annotated[str, Option(
    '--version', '-v', show_default=False, help=''
    'A semantic version identifier of a section in the changelog file.'
)]


@app.command(name="view", epilog="Example: devtools log view --version 1.2.3")
def cmd_view(version: VersionOpt = None):
    try:
        existing = read_existing_content(init_cwd=False)
        if not existing:
            console.print("ERROR! The changelog does not contain any entries.\n")
            raise SystemExit()
    except ConfigFileNotFound:
        console.print("ERROR! Project is not initialized with a devtools config file.\n")
        raise SystemExit()
    except ChangelogFileNotFound:
        console.print("ERROR! Cannot view sections of a non-existent CHANGELOG.md file.\n")
        raise SystemExit()

    label = SECTION_LEVEL
    if version:
        label += f" [{version}]"

    line: str
    for i, line in enumerate(existing):
        if line.startswith(label):
            end = len(existing)
            for j in range(i + 1, end):
                if existing[j].startswith(f"{SECTION_LEVEL}"):
                    end = j
                    break

            ver_type = 'Version' if version else "Latest version"
            ver_ident = extract_version_from_label(line)
            print(f"{ver_type} {ver_ident} changelog:")

            contents = existing[i + 2:end]
            for c in contents:
                print(c)
            if contents[-1] != '':
                print('')
            return

    console.print(f"The changelog does not contain any sections for version {version}.")
