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
from typer import Typer, Option
from rich.console import Console
from typing_extensions import Annotated
from .helpers import *


app = Typer(name="logic", help="Simplifies logic operations in linux terminals.")
console = Console(soft_wrap=True)


VarsOpt = Annotated[list[str], Option(
    '--var', '-v', show_default=False, help=''
    'A value to evaluate by the command. Can be used multiple times.'
)]
GitHubEnvOpt = Annotated[str, Option(
    '--ghenv', '-e', show_default=False, help=''
    'The name of the environment variable that the evaluated result is assigned to.'
)]
GitHubOutOpt = Annotated[str, Option(
    '--ghout', '-o', show_default=False, help=''
    'The name of the output variable that the evaluated result is assigned to.'
)]


@app.command(name="eq", epilog="Example: devtools logic eq --var abc --var cde")
def cmd_equal(_vars: VarsOpt, ghenv: GitHubEnvOpt = '', ghout: GitHubOutOpt = '') -> None:
    result = compare(_vars, 'eq')
    to_gh_file(result, ghenv, ghout)
    console.print(result)


@app.command(name="ne", epilog="Example: devtools logic ne --var abc --var cde")
def cmd_not_equal(_vars: VarsOpt, ghenv: GitHubEnvOpt = '', ghout: GitHubOutOpt = '') -> None:
    result = compare(_vars, 'ne')
    to_gh_file(result, ghenv, ghout)
    console.print(result)
