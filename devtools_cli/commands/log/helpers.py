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
from devtools_cli.utils import *
from .errors import *


__all__ = [
    "CHANGELOG_FILENAME",
    "SECTION_LEVEL",
    "HEADER",
    "get_section_label",
    "extract_version_from_label",
    "conform_changes",
    "get_logfile_path",
    "read_existing_content",
    "write_new_section",
    "update_latest_section",
    "validate_unique_version"
]

CHANGELOG_FILENAME = "CHANGELOG.md"
SECTION_LEVEL = '###'
HEADER = [
    "# Changelog",
    "",
    "All notable changes to this project will be documented in this file.  ",
    "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), "
    "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).  "
]


def get_section_label(version: str, partial=False) -> str:
    label = f"{SECTION_LEVEL} [{version}]"
    if not partial:
        label += f" - {date.today().isoformat()}  "
    return label


def extract_version_from_label(line: str) -> str:
    return line.split('[')[-1].split(']')[0]


def conform_changes(changes: str | list) -> list[str]:
    def conformed(c: str):
        return c.startswith("- ") or c.startswith("  ")

    if isinstance(changes, str):
        changes = changes.splitlines()

    return [c if conformed(c) else f"- {c}" for c in changes]


def get_logfile_path(*, init_cwd: bool) -> Path:
    config_file: Path = find_local_config_file(init_cwd=init_cwd)
    if config_file is None and not init_cwd:
        raise ConfigFileNotFound()
    logfile = config_file.parent / CHANGELOG_FILENAME
    if not logfile.exists():
        if not init_cwd:
            raise ChangelogFileNotFound()
        else:
            logfile.touch(exist_ok=True)
            with logfile.open('w') as file:
                file.write('\n'.join(HEADER))
    return logfile


def read_existing_content(*, init_cwd: bool) -> list[str]:
    logfile = get_logfile_path(init_cwd=init_cwd)
    with logfile.open('r') as file:
        lines = file.read().splitlines()
    existing = []
    for i, line in enumerate(lines):
        if line.startswith(SECTION_LEVEL):
            existing = lines[i:]
            break
    return existing


def write_new_section(version: str, changes: list[str], existing: list[str]) -> None:
    logfile = get_logfile_path(init_cwd=False)
    with logfile.open('w') as file:
        title = get_section_label(version)
        file.write('\n'.join([
            *HEADER,
            '',
            title,
            '',
            *changes,
            '',
            *existing
        ]))


def update_latest_section(changes: list[str], existing: list[str]) -> None:
    latest, remainder = [], []
    for i in range(1, len(existing)):
        if existing[i].startswith(SECTION_LEVEL):
            latest = existing[:i]
            remainder = existing[i:]

    if latest and latest[-1] == '':
        latest.pop(-1)
    latest.extend(changes)

    logfile = get_logfile_path(init_cwd=False)
    with logfile.open('w') as file:
        file.write('\n'.join([
            *HEADER,
            '',
            *latest,
            '',
            *remainder
        ]))


def validate_unique_version(version: str, existing: list) -> bool:
    for line in existing:
        if line.startswith(SECTION_LEVEL):
            ex_ver = extract_version_from_label(line)
            if version == ex_ver:
                return False
    return True
