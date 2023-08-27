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
from devtools_cli.models import DefaultModel, ConfigSection

__all__ = [
    "TrackedComponent",
    "VersionConfig"
]


class TrackedComponent(DefaultModel):
    name: str
    target: str
    ignore: list[str]
    hash: str

    @staticmethod
    def __defaults__() -> dict:
        return {
            "name": "",
            "target": "",
            "ignore": list(),
            "hash": ""
        }


class VersionConfig(ConfigSection):
    app_version: str
    components: list[TrackedComponent]

    @staticmethod
    def __defaults__() -> dict:
        return {
            "app_version": "0.0.0",
            "components": list()
        }

    @property
    def section(self) -> str:
        return 'version_cmd'
