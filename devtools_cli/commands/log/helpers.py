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
import re
from pathlib import Path
from datetime import date
from devtools_cli.utils import *
from .models import *
from .errors import *


__all__ = [
    "get_section_label",
    "remove_latest_label",
    "extract_version_from_label",
    "conform_changes",
    "get_logfile_path",
    "read_existing_content",
    "write_new_section",
    "update_latest_section",
    "validate_unique_version",
    "add_release_link_ref",
    "is_line_link_ref"
]


def get_section_label(version: str) -> str:
    return " - ".join([
        f"{SECTION_LEVEL} [{version}]",
        date.today().isoformat(),
        "_latest_"
    ])


def remove_latest_label(arr: list[str]) -> None:
    if len(arr) >= 1:
        suffix = '- _latest_'
        line = arr[0].strip()
        if line.endswith(suffix):
            arr[0] = line.rstrip(suffix).strip()


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
    return logfile


def read_existing_content(*, init_cwd: bool) -> list[str]:
    logfile = get_logfile_path(init_cwd=init_cwd)
    with logfile.open('r') as file:
        lines = file.read().splitlines()
    skip = Header.line_count + 1
    return lines[skip:]


def write_new_section(version: str, changes: str | list[str], existing: list[str]) -> None:
    existing = add_release_link_ref(version, existing)
    conformed = conform_changes(changes)
    label = get_section_label(version)
    remove_latest_label(existing)

    logfile = get_logfile_path(init_cwd=False)
    with logfile.open('w') as file:
        file.write('\n'.join([
            Header(), '',
            label, '',
            *conformed, '',
            *existing
        ]))


def update_latest_section(changes: str | list[str], existing: list[str]) -> None:
    latest, remainder = [], []
    for i in range(1, len(existing)):
        if existing[i].startswith(SECTION_LEVEL) or is_line_link_ref(existing[i]):
            latest = existing[:i]
            remainder = existing[i:]
            break

    if not latest:
        latest = existing

    if latest and latest[-1] == '':
        latest.pop(-1)

    conformed = conform_changes(changes)
    latest.extend(conformed)

    logfile = get_logfile_path(init_cwd=False)
    with logfile.open('w') as file:
        file.write('\n'.join([
            Header(), '',
            *latest, '',
            *remainder
        ]))


def validate_unique_version(version: str, existing: list) -> bool:
    for line in existing:
        if line.startswith(SECTION_LEVEL):
            ex_ver = extract_version_from_label(line)
            if version == ex_ver:
                return False
    return True


def is_line_link_ref(line: str) -> bool:
    pattern = r"^\[(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)\]"
    return True if re.match(pattern, line) else False


def add_release_link_ref(curr_ver: str, changelist: list) -> list:
    prev_ver = curr_ver
    log = changelist
    refs = []

    for i, line in enumerate(changelist):
        if is_line_link_ref(line):
            log = changelist[:i]
            refs = changelist[i:]
            prev_ver = extract_version_from_label(line)
            break

    config: LogConfig = read_local_config_file(LogConfig)
    url = "{base}/{user}/{repo}/compare/{prev}...{curr}".format(
        base=GITHUB_URL,
        user=config.gh_user,
        repo=config.gh_repo,
        prev=prev_ver,
        curr=curr_ver
    )
    refs = [f"[{curr_ver}]: {url}", *refs]
    return log + refs
