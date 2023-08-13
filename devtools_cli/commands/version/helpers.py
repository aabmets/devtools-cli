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
from .models import *

__all__ = [
    "find_tracked_project",
    "read_version_from_pyproject_toml",
    "write_version_to_pyproject_toml"
]


def find_tracked_project(arg: str, config: VersionConfig) -> tuple[int | None, ProjectTracker]:
    project = ProjectTracker()
    index = None

    for i, entry in enumerate(config.projects):
        if entry.dir_path == arg or entry.alias == arg:
            project = config.projects[i]
            index = i
            break

    return index, project


def read_version_from_pyproject_toml(filepath: Path) -> str:
    if not filepath or not filepath.exists() or not filepath.is_file() or filepath.name != 'pyproject.toml':
        raise RuntimeError(f"Filepath '{filepath} is not a valid pyproject.toml file!")

    with open(filepath, 'r') as file:
        lines = file.readlines()

    searching_for_version = False

    for line in lines:
        line = line.strip()

        if line in ['[tool.poetry]', '[project]']:
            searching_for_version = True
            continue

        if searching_for_version and line.startswith('['):
            break

        if searching_for_version and line.startswith('version'):
            return line.split('=')[-1].strip().strip('"').strip("'")

    return "0.0.0"


def write_version_to_pyproject_toml(filepath: Path, new_version: str = '0.0.0') -> None:
    if not filepath or not filepath.exists() or not filepath.is_file() or filepath.name != 'pyproject.toml':
        raise RuntimeError(f"Filepath '{filepath} is not a valid pyproject.toml file!")

    with open(filepath, 'r') as f:
        lines = f.readlines()

    searching_for_version = False

    for index, line in enumerate(lines):
        line = line.strip()

        if line in ['[tool.poetry]', '[project]']:
            searching_for_version = True
            continue

        if searching_for_version and line.startswith('['):
            break

        if searching_for_version and line.startswith('version'):
            lines[index] = f'version = "{new_version}"\n'

            with open(filepath, 'w') as f:
                f.writelines(lines)
                break
