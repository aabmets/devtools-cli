#
#   MIT License
#
#   Copyright (c) 2023, Mattias Aabmets
#
#   This file is subject to the terms and conditions defined in
#   the License. You may not use, modify, or distribute this file
#   except in compliance with the License.
#
#   SPDX-License-Identifier: MIT
#
import asyncio
import webbrowser
from typing import List
from typer import Typer, Option
from typing_extensions import Annotated
from rich.console import Console
from rich.table import Table
from .helpers import *

app = Typer(name="license")


InclPathsOpt = Annotated[List[str], Option(
	"--include", "-i", show_default=False, help=
	"A subdirectory path in the project directory, which will be "
	"processed by this script. If provided, only the included "
	"paths are processed. Option can be used multiple times."
)]
ExclPathsOpt = Annotated[List[str], Option(
	"--exclude", "-e", show_default=False, help=
	"A subdirectory path in the project directory, which "
	"will be excluded from being processed by this script. "
	"Option can be used multiple times."
)]
FormatVarsOpt = Annotated[List[str], Option(
	"--format", "-f", show_default=False, help=
	"Formats a placeholder in the license header text with the assigned value. "
	"Values must be in the format of \"placeholder=value\". "
	"Option can be used multiple times."
)]
SpacesOpt = Annotated[int, Option(
	"--spaces", "-S", show_default=False, help=
	"How many spaces the license header contents will "
	"indented with from the comment symbol. Default: 3"
)]
DryRunOpt = Annotated[bool, Option(
	"--dry-run", "-d", show_default=False, help=
	"If provided, does not alter files and prints out "
	"a list of directories to be processed instead."
)]
SpdxIdOpt = Annotated[str, Option(
	"--spdx", "-s", show_default=False, help=
	"The SPDX identifier of the license. Case-insensitive."
)]


@app.command(name="apply", epilog="Example: devtools license apply --spdx EUPL-1.2")
def cmd_apply():
	pass  # TODO


@app.command(name="update", epilog="Example: devtools license update")
def cmd_update() -> None:
	"""
	Updates available licenses from the https://choosealicense.com website.
	"""
	filenames = fetch_license_filenames()
	coro = fetch_license_details(filenames)
	licenses = asyncio.run(coro)
	write_licenses_to_file(licenses)


@app.command(name="list", epilog="Example: devtools license list")
def cmd_list() -> None:
	"""
	Prints out the list of available licenses to the console.
	"""
	meta_data = read_licenses_metadata()

	table = Table(title="Available Licenses")
	table.add_column("Index", style="sandy_brown", no_wrap=True)
	table.add_column("SPDX-Identifier", style="cyan", no_wrap=True)
	table.add_column("License Name", style="orchid", no_wrap=True)
	table.add_column("License Website", no_wrap=True)

	counter = 1
	for data in meta_data.values():
		table.add_row(
			str(counter),
			data["spdx_id"],
			data["title"],
			data["web_url"]
		)
		counter += 1

	console = Console(soft_wrap=True)
	console.print('')
	console.print(table)


@app.command(name="read", epilog="Example: devtools license read --spdx eupl-1.2")
def cmd_read(spdx_id: SpdxIdOpt = None) -> None:
	"""
	Opens the default web browser to a license on the https://choosealicense.com website.
	If the --spdx option is not provided, the script tries to open the current projects
	license. An exception is raised, if devtools haven't set a license for the project.
	"""
	if not spdx_id:
		pass  # TODO: try to open project license

	meta_data = read_licenses_metadata()
	lc_spdx_id = spdx_id.lower()
	opened = False

	for filename, data in meta_data.items():
		if filename.startswith(lc_spdx_id):
			opened = webbrowser.open(data["web_url"])

	if spdx_id and not opened:
		raise Exception()  # TODO


@app.command(name="compare", epilog="Example: devtools license compare")
def cmd_compare() -> None:
	"""
	Opens the default web browser to https://choosealicense.com/appendix/.
	"""
	webbrowser.open("https://choosealicense.com/appendix/")
