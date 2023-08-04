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
import tomllib
from typer import Typer
from pathlib import Path
from rich.console import Console

app = Typer()


@app.command(epilog="Example: devtools info")
def info() -> None:
    """
    Prints information about the devtools package to the console.
    """
    title_color = "[{}]".format("#ff5fff")
    key_color = "[{}]".format("#87d7d7")
    value_color = "[{}]".format("#ffd787")
    i1, i2 = 2 * ' ', 5 * ' '

    pkg = get_package_info()
    console = Console(soft_wrap=True)
    console.print(f"\n{i1}{title_color}Package Info:")

    for k, v in vars(pkg).items():
        k = f"{key_color}{k}"
        v = f"{value_color}{v}"
        console.print(f"{i2}{k}: {v}")

    console.print('')


class PackageInfo:
    name: str
    version: str
    description: str
    license: str
    authors: list[str]
    repository: str

    def __init__(self, data: dict):
        for k, v in data.items():
            if k in self.__annotations__:
                setattr(self, k, v)


def get_package_info() -> PackageInfo:
    current_path = Path(__file__).parent
    while current_path != current_path.root:
        toml_file = current_path / "pyproject.toml"
        if toml_file.exists():
            with open(toml_file, 'rb') as file:
                toml_data = tomllib.load(file)
                section = toml_data['tool']['poetry']
                return PackageInfo(section)
        current_path = current_path.parent
