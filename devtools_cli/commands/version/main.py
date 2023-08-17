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
import os
from pathlib import Path
from semver import Version
from rich.prompt import Confirm
from rich.console import Console
from typing_extensions import Annotated
from typer import Typer, Option
from .helpers import *
from .models import *
from devtools_cli.models import *
from devtools_cli.utils import *


app = Typer(name="version", help="Manages project version number and tracks filesystem changes.")
console = Console(soft_wrap=True)


NameOpt = Annotated[str, Option(
    '--name', '-n', show_default=False, help=''
    'A unique name identifier of the trackable component to reference it by.'
)]
TargetOpt = Annotated[str, Option(
    '--target', '-t', show_default=False, help=''
    'The path to target with tracking, relative to the path of the .devtools config file. '
    'If not provided, defaults to the location of the .devtools config file. If the config '
    'file does not exist, a new config file is created in the current working directory.'
)]
IgnoreOpt = Annotated[list[str], Option(
    '--ignore', '-i', show_default=False, help=''
    'A path to be ignored relative to the target path. Can be used multiple times.'
)]


@app.command(name="track", epilog="Example: devtools version track --name app")
def cmd_track(name: NameOpt, target: TargetOpt = '.', ignore: IgnoreOpt = None):
    """
    Tracks filesystem changes for a specified component in the project.
    This command associates a unique name with a target path (file or directory)
    and optionally sets paths to be ignored during tracking. If the specified name
    or path is already being tracked, it updates the existing tracking information.
    Errors will occur if the target path does not exist, if ignored paths are set
    when the target is a file, or if duplicate names or paths are assigned.
    """
    config_file: Path = find_local_config_file(init_cwd=True)
    config: VersionConfig = read_local_config_file(VersionConfig)
    track_path = config_file.parent / target

    if not track_path.exists():
        console.print(f"ERROR! Cannot track a target path which does not exist: '{track_path}'\n")
        raise SystemExit()
    elif track_path.is_file() and ignore:
        console.print(f"ERROR! Cannot set ignored paths when target is a file: '{track_path}'\n")
        raise SystemExit()

    index = None
    for i, entry in enumerate(config.components):
        if entry.name == name and entry.target != target:
            console.print(f"ERROR! Cannot assign the same name '{name}' to multiple targets!\n")
            raise SystemExit()
        elif entry.target == target and entry.name != name:
            console.print(f"ERROR! Cannot assign the same target '{target}' to multiple names!\n")
            raise SystemExit()
        elif entry.name == name and entry.target == target and entry.ignore == ignore:
            console.print(f"Nothing to update in the tracked component.\n")
            raise SystemExit()
        elif entry.name == name and entry.target == target:
            index = i

    if track_path.is_file():
        track_hash = hash_file(track_path)
    else:
        track_hash = hash_directory(track_path, ignore)

    comp = TrackedComponent(
        name=name,
        target=target,
        ignore=ignore,
        hash=track_hash
    )

    if index is None:
        config.components.append(comp)
        msg = f"Successfully tracked component: '{name}'.\n"
    else:
        config.components[index] = comp
        msg = f"Successfully updated the component '{name}'.\n"

    write_local_config_file(config)
    console.print(msg)


@app.command(name="untrack", epilog="Example: devtools version untrack --name app")
def cmd_untrack(name: NameOpt):
    """
    Un-tracks filesystem changes for a specified component in the project.
    If the specified name is not being tracked, an error will be raised.
    """
    config: VersionConfig = read_local_config_file(VersionConfig)

    index = None
    for i, entry in enumerate(config.components):
        if entry.name == name:
            index = i
            break

    if index is None:
        console.print("ERROR! Cannot untrack a non-existing component.\n")
        raise SystemExit()

    config.components.pop(index)
    write_local_config_file(config)
    console.print(f"Successfully untracked the component '{name}'.\n")


MajorBumpOpt = Annotated[bool, Option(
    '--major', '-M', show_default=False, help=""
    "Bump the major version number (the 'X' in 'X.Y.Z'). Y and Z are set to zero."
)]
MinorBumpOpt = Annotated[bool, Option(
    '--minor', '-m', show_default=False, help=""
    "Bump the minor version number (the 'Y' in 'X.Y.Z'). X is left untouched, Z is set to zero."
)]
PatchBumpOpt = Annotated[bool, Option(
    '--patch', '-p', show_default=False, help=""
    "Bump the patch version number (the 'Z' in 'X.Y.Z'). X and Y are left untouched."
)]
SuffixOpt = Annotated[str, Option(
    '--suffix', '-s', show_default=False, help=""
    "Append a suffix to the semver string. Example: '-s beta' produces 'X.Y.Z-beta'."
)]


@app.command(name="bump", epilog="Example: devtools version bump --minor")
def cmd_bump(
        major: MajorBumpOpt = False,
        minor: MinorBumpOpt = False,
        patch: PatchBumpOpt = False,
        suffix: SuffixOpt = ''
):
    """
    Bump the version number of the project.

    This command increments the major, minor, or patch version number of the project.
    By default, it bumps the patch version. You can optionally add a suffix to the version.
    If no components are being tracked, or if an attempt is made to bump multiple version
    numbers at the same time, an error will be raised.
    """
    if sum([major, minor, patch]) > 1:
        console.print("ERROR! Cannot bump multiple version numbers at the same time!\n")
        raise SystemExit()
    if not any([major, minor, patch]):
        patch = True

    if count_descriptors() > 1:
        console.print("ERROR! Cannot have multiple language descriptor files in the project directory!\n")
        raise SystemExit()

    config_file = find_local_config_file(init_cwd=True)
    config: VersionConfig = read_local_config_file(VersionConfig)
    descriptor_ver = read_descriptor_file_version()

    desc_ver = Version.parse(descriptor_ver)
    conf_ver = Version.parse(config.app_version)
    ver = desc_ver if desc_ver > conf_ver else conf_ver

    index = [major, minor, patch].index(True)
    func = [ver.bump_major, ver.bump_minor, ver.bump_patch][index]
    new_version = str(func()) + (f"-{suffix}" if suffix else '')

    bump = Confirm.ask(
        f"Bump the version of [light_goldenrod3]'{config_file.parent.name}'[/] from "
        f"[light_slate_blue]{config.app_version}[/] to [chartreuse3]{new_version}[/]?"
    )
    if not bump:
        console.print("[bold]Did not bump the project version.\n")
        raise SystemExit()

    write_descriptor_file_version(new_version)

    for comp in config.components:
        track_path = config_file.parent / comp.target
        if track_path.is_file():
            track_hash = hash_file(track_path)
        else:
            track_hash = hash_directory(track_path, comp.ignore)
        comp.hash = track_hash

    config.app_version = new_version
    write_local_config_file(config)
    console.print("[bold]Successfully bumped the project version.\n")


GitHubEnvOpt = Annotated[str, Option(
    '--ghenv', '-e', show_default=False, help=''
    'The name of the environment variable that the evaluated result is assigned to.'
)]
GitHubOutOpt = Annotated[str, Option(
    '--ghout', '-o', show_default=False, help=''
    'The name of the output variable that the evaluated result is assigned to.'
)]


@app.command(name="echo", epilog="Example: devtools version echo")
def cmd_echo(name: NameOpt = '', ghenv: GitHubEnvOpt = '', ghout: GitHubOutOpt = ''):
    """
    Echoes the project version to stdout if 'name' option is not provided, otherwise
    echoes the hash of the tracked component by name. If 'ghenv' option is provided,
    also inserts the value into the GitHub Actions environ file. If 'ghout' option
    is provided, also inserts the value into the GitHub Actions step output file.
    """
    config: VersionConfig = read_local_config_file(VersionConfig)
    var_map = [(ghenv, GitHubFile.ENV), (ghout, GitHubFile.OUT)]
    if not name:
        console.print(config.app_version)
        [
            write_to_github_file(key, config.app_version, file)
            for key, file in var_map if key
        ]
        return
    else:
        for entry in config.components:
            if entry.name == name:
                console.print(entry.hash)
                [
                    write_to_github_file(key, entry.hash, file)
                    for key, file in var_map if key
                ]
                return
        console.print("ERROR! Cannot access the hash of a non-existent component!\n")
        raise SystemExit()
