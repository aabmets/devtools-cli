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
from typing import Callable
from devtools_cli.models import DefaultModel, ConfigSection

__all__ = [
    "ProgLang",
    "ProjectTracker",
    "VersionConfig"
]


class ProgLang(DefaultModel):
    name: str
    metafile: str
    read: Callable
    write: Callable

    @staticmethod
    def __defaults__() -> dict:
        return {
            "name": '',
            "metafile": '',
            "read": lambda _: "0.0.0",
            "write": lambda _, __: None
        }


class ProjectTracker(DefaultModel):
    alias: str
    dir_path: str
    language: str
    metafile: str
    version: str
    virtual: dict[str, str]

    @staticmethod
    def __defaults__() -> dict:
        return {
            "alias": "",
            "dir_path": "",
            "language": "",
            "metafile": "",
            "version": "",
            "virtual": dict()
        }


class VersionConfig(ConfigSection):
    projects: list[ProjectTracker]

    @staticmethod
    def __defaults__() -> dict:
        return {
            "projects": []
        }

    @property
    def section(self) -> str:
        return 'version'
