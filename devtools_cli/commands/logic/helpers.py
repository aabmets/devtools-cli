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
from typing import Literal
from devtools_cli.models import GitHubFile
from devtools_cli.utils import *

__all__ = ["select", "compare", "to_gh_file"]

Operator = Literal['eq', 'ne']


def select(operands: list[str]) -> tuple:
    for i, op in enumerate(operands):
        for j in range(i, len(operands)):
            yield op, operands[j]


def compare(operands: list[str], operator: Operator) -> str:
    result = None
    if operator == 'eq':
        result = True
        for a, b in select(operands):
            if a != b:
                result = False
    elif operator == 'ne':
        result = False
        for a, b in select(operands):
            if a != b:
                result = True

    return str(result).lower()


def to_gh_file(result: str, ghenv: str, ghout: str) -> None:
    for key, file in [(ghenv, GitHubFile.ENV), (ghout, GitHubFile.OUT)]:
        write_to_github_file(key, result, file) if key else None
