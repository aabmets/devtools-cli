#
#  MIT License
#
#  Copyright (c) 2023 Mattias Aabmets
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
import tomllib
from typer import Typer
from pathlib import Path
from rich.console import Console

app = Typer()


@app.command(name="info", epilog="Example: devtools info")
def main() -> None:
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
    filepath = Path(__file__).parents[2] / "pyproject.toml"
    with open(filepath, 'rb') as file:
        package_data = tomllib.load(file)
        info_data = package_data['tool']['poetry']
        return PackageInfo(info_data)
