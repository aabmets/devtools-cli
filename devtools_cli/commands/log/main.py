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
from semver import Version
from rich.prompt import Prompt
from rich.console import Console
from typer import Typer, Option
from typing_extensions import Annotated
from devtools_cli.commands.version.models import VersionConfig
from devtools_cli.utils import *
from .helpers import *
from .models import *
from .errors import *


app = Typer(name="log", help="Manages project changelog file.")
console = Console(soft_wrap=True)


UserOpt = Annotated[str, Option(
    '--user', '-u', show_default=False, help=''
    'The GitHub username of the current project.'
)]
RepoOpt = Annotated[str, Option(
    '--repo', '-r', show_default=False, help=''
    'The GitHub repository of the current project.'
)]


@app.command(name="init", epilog="Example: devtools log init --user \"user\" --repo \"repo\"")
def cmd_init(user: UserOpt, repo: RepoOpt):
    """
    Stores the provided GitHub project attributes into the devtools
    config file and (re-)initializes the CHANGELOG.md file with a header.
    """
    log_conf: LogConfig = read_local_config_file(LogConfig)
    log_conf.gh_user = user
    log_conf.gh_repo = repo
    write_local_config_file(log_conf)

    logfile = get_logfile_path(init_cwd=True)
    with logfile.open('w') as file:
        file.write(Header())

    console.print("Successfully initialized the log configuration.\n")


@app.command(name="add", epilog="Example: devtools log add")
def cmd_add():
    """
    Interactively add changes into the changelog file.
    If the version in the .devtools file is larger than the
    latest entry in the changelog file, then a new section
    is created into the changelog file for the new version.
    """
    log_conf: LogConfig = read_local_config_file(LogConfig)
    if log_conf.is_default:
        console.print("ERROR! Cannot add changes to the changelog without first initializing the log config.\n")
        raise SystemExit()

    ver_conf: VersionConfig = read_local_config_file(VersionConfig)
    existing = read_existing_content(init_cwd=True)
    new_section = True

    if len(existing) >= 1:
        prev_ver_str = extract_version_from_label(existing[0])
        curr_ver = Version.parse(ver_conf.app_version)
        prev_ver = Version.parse(prev_ver_str)

        if curr_ver == prev_ver:
            new_section = False

    console.print("Please provide the changelog contents: (Press Enter on empty prompt to apply.)")

    changes = []
    while True:
        change = Prompt.ask("Entry")
        if change == '':
            break
        changes.append(change)

    if not changes:
        msg = "Did not alter the changelog file.\n"
    elif new_section:
        write_new_section(ver_conf.app_version, changes, existing)
        msg = "Added the changes into a new section of the changelog file.\n"
    else:
        update_latest_section(changes, existing)
        msg = "Added the changes into the latest section of the changelog file.\n"
    console.print(msg)


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
    log_conf: LogConfig = read_local_config_file(LogConfig)
    if log_conf.is_default:
        console.print("ERROR! Cannot add changes to the changelog without first initializing the log config.\n")
        raise SystemExit()

    ver_conf: VersionConfig = read_local_config_file(VersionConfig)
    existing = read_existing_content(init_cwd=True)
    version = ver_conf.app_version

    if not validate_unique_version(version, existing):
        console.print("ERROR! Cannot insert a duplicate version section into the changelog file.\n")
        raise SystemExit()

    write_new_section(version, changes, existing)

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
                end_1 = existing[j].startswith(f"{SECTION_LEVEL}")
                end_2 = is_line_link_ref(existing[j])
                if end_1 or end_2:
                    end = j
                    break

            ver_type = 'Version' if version else "Latest version"
            ver_ident = extract_version_from_label(line)
            print(f"{ver_type} {ver_ident} changelog:")

            for c in existing[i + 2:end]:
                print(c)
            return

    console.print(f"The changelog does not contain any sections for version {version}.")
