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
import semver
from pathlib import Path
from typer import Typer, Argument, Option
from typing_extensions import Annotated
from rich.console import Console
from .helpers import *
from .models import *
from .langs import *
from devtools_cli.utils import *


app = Typer(name="version", help="Manages version numbers in project descriptor files.")
console = Console(soft_wrap=True)


PathArg = Annotated[str, Argument(
    show_default=False, help=""
    "A sub-path to a folder relative to the .devtools config file. If the .devtools config "
    "file cannot be found, it is created in the current working directory. If not provided, "
    "the command is applied to the directory of the .devtools config file."
)]
AliasOpt = Annotated[str, Option(
    '--alias', '-a', show_default=False, help=""
    "An alias for the path argument. Allows to reference the path by the alias. "
    "Mutually exclusive with '--virtual'."
)]
VirtualOpt = Annotated[str, Option(
    '--virtual', '-v', show_default=False, help=""
    "A sub-component inside the tracked project tracked by a virtual version. "
    "Mutually exclusive with '--alias'."
)]


@app.command(name="track", epilog="Example: devtools version track components/api --alias api")
def cmd_track(path: PathArg = '', alias: AliasOpt = '', virtual: VirtualOpt = ''):
    """
    Track a version number in a projects descriptor file.
    """
    if alias and virtual:
        console.print("Cannot use '--alias' and '--virtual' at the same time.")
        raise SystemExit()

    config_file: Path = find_local_config_file(init_cwd=True)
    config: VersionConfig = read_local_config_file(VersionConfig)
    track_dir = config_file.parent / path

    metafiles_count = count_lang_metafiles(track_dir)
    if metafiles_count == 0 and not virtual:
        console.print(f"The directory '{track_dir}' does not contain a supported project descriptor file.")
        raise SystemExit()
    elif metafiles_count > 1 and not virtual:
        console.print(f"The directory '{track_dir}' must not contain more than one project descriptor file.")
        raise SystemExit()

    rel_path = str(track_dir.relative_to(config_file.parent))
    index, project = find_tracked_project(rel_path or alias, config)

    if index is None and virtual:
        console.print("Cannot track a virtual component of an untracked project.")
        raise SystemExit()
    elif index is not None and virtual in project.virtual:
        console.print("Cannot track a virtual component that is already being tracked.")
        raise SystemExit()

    prog_lang = infer_project_lang(track_dir)
    new_proj = ProjectTracker(
        dir_path=rel_path,
        language=prog_lang.name,
        metafile=prog_lang.metafile,
        version=prog_lang.read(track_dir / prog_lang.metafile),
        virtual=dict() if index is None else project.virtual,
        alias=alias if alias else project.alias
    )

    for entry in config.projects:
        if entry.alias == new_proj.alias and entry.dir_path != new_proj.dir_path and not virtual:
            console.print(f"Cannot assign identical aliases to multiple sub-projects.")
            raise SystemExit()
        elif entry.dir_path == new_proj.dir_path and entry.alias == new_proj.alias and not virtual:
            console.print(f"Nothing to update for the project tracker.")
            raise SystemExit()

    if index is None:
        config.projects.append(new_proj)
        msg = f"Successfully tracked project in '{track_dir}'."
    else:
        config.projects[index] = new_proj
        msg = f"Successfully updated the tracker of '{track_dir}'."
    if virtual:
        config.projects[index].virtual[virtual] = "0.0.0"
        msg = f"Successfully tracked the virtual component '{virtual}' for project in '{track_dir}'."

    write_local_config_file(config)
    console.print(msg)


PathOrAliasArg = Annotated[str, Argument(
    show_default=False, help="Either a path to a project folder relative to the "
                             ".devtools config file or an alias of a tracked project."
)]


@app.command(name="untrack", epilog="Example: devtools version untrack api")
def cmd_assign(arg: PathOrAliasArg = '.', virtual: VirtualOpt = ''):
    """
    Untrack a projects descriptor file.
    """
    config: VersionConfig = read_local_config_file(VersionConfig)
    index, project = find_tracked_project(arg, config)

    if index is None or config.is_default:
        if not virtual:
            console.print("Cannot untrack an untracked project.")
        else:
            console.print("Cannot untrack a virtual component of an untracked project.")
        raise SystemExit()
    elif virtual and virtual not in project.virtual:
        console.print(f"Cannot untrack a virtual component which does not exist.")
        raise SystemExit()

    config_file: Path = find_local_config_file(init_cwd=False)
    track_dir = config_file.parent / project.dir_path

    if not virtual:
        config.projects.pop(index)
        msg = f"Successfully untracked project in '{track_dir}'."
    else:
        project.virtual.pop(virtual)
        msg = f"Successfully untracked virtual component '{virtual}' of project '{track_dir}'."

    write_local_config_file(config)
    console.print(msg)


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
    "Bump the patch version number (the 'Z' in 'X.Y.Z'). X and Y are left untouched. "
    "If no "
)]
SuffixOpt = Annotated[str, Option(
    '--suffix', '-s', show_default=False, help=""
    "Append a suffix to the semver string. Example: '-s beta' produces 'X.Y.Z-beta'."
)]


@app.command(name="bump")
def cmd_bump(
        arg: PathOrAliasArg = '.',
        major: MajorBumpOpt = False,
        minor: MinorBumpOpt = False,
        patch: PatchBumpOpt = False,
        suffix: SuffixOpt = '',
        virtual: VirtualOpt = ''
):
    if not any([major, minor, patch]):
        patch = True

    config: VersionConfig = read_local_config_file(VersionConfig)
    index, project = find_tracked_project(arg, config)

    if index is None or project.is_default:
        console.print("Cannot bump the version of an untracked project.")
        raise SystemExit()
    if virtual and virtual not in project.virtual:
        console.print("Cannot bump the version of a virtual component which does not exist.")
        raise SystemExit()
