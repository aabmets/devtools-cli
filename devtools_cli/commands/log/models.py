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
from devtools_cli.models import ConfigSection

__all__ = [
    "GITHUB_URL",
    "CHANGELOG_FILENAME",
    "SECTION_LEVEL",
    "Header",
    "LogConfig"
]

GITHUB_URL = "https://github.com"
CHANGELOG_FILENAME = "CHANGELOG.md"
SECTION_LEVEL = '###'


class Header(str):
    __template__ = [
        "# Changelog",
        "",
        "All notable changes to this project will be documented in this file.  ",
        "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), "  # <--- Line continuation!
        "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).  ",
        "_NOTE: This changelog is generated and managed by [devtools-cli]"  # <--- Line continuation!
        "(https://pypi.org/project/devtools-cli/), **do not edit manually**._",
        ""
    ]
    line_count = len(__template__)

    def __new__(cls) -> str:
        header = '\n'.join(cls.__template__)
        return super().__new__(cls, header)


class LogConfig(ConfigSection):
    gh_user: str
    gh_repo: str

    @staticmethod
    def __defaults__() -> dict:
        return {
            "gh_user": "",
            "gh_repo": ""
        }

    @property
    def section(self) -> str:
        return 'log_cmd'
