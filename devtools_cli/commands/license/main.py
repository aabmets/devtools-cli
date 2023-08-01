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
import time
import asyncio
import webbrowser
from typing import List, Any
from typer import Typer, Option
from typing_extensions import Annotated
from rich.progress import Progress
from rich.console import Console
from rich.table import Table
from .helpers import *
from .models import *
from devtools_cli.utils import *

app = Typer(name="license")
console = Console(soft_wrap=True)


YearOpt = Annotated[List[str], Option(
	"--year", "-Y", show_default=False, help=''
	"The year of the copyright claim."
)]
HolderOpt = Annotated[str, Option(
	'--holder', '-H', show_default=False, help=''
	"The name of the copyright holder."
)]
IdentOpt = Annotated[str, Option(
	"--id", "-I", show_default=False, help=''
	"Either the numerical index or The SPDX identifier of the "
	"license from the available licenses list. Case-insensitive. "
	"Execute \"devtools license --help\" for more info."
)]
SpacesOpt = Annotated[int, Option(
	"--spaces", "-S", show_default=False, help=''
	"How many spaces the license header contents will be"
	"indented with from the comment symbol. Default: 3"
)]
InclPathsOpt = Annotated[List[str], Option(
	"--include", "-i", show_default=False, help=''
	"A subdirectory path in the project directory, which will be "
	"processed by this script. If provided, only the included "
	"paths are processed. Option can be used multiple times."
)]
ExclPathsOpt = Annotated[List[str], Option(
	"--exclude", "-e", show_default=False, help=''
	"A subdirectory path in the project directory, which "
	"will be excluded from being processed by this script. "
	"Option can be used multiple times."
)]


@app.command(name="apply", epilog="Example: devtools license apply --spdx EUPL-1.2")
def cmd_apply(
		year: YearOpt = None,
		holder: HolderOpt = None,
		incl: InclPathsOpt = None,
		excl: ExclPathsOpt = None,
		ident: IdentOpt = None,
		spaces: SpacesOpt = 3,
):
	pass  # TODO


@app.command(name="update", epilog="Example: devtools license update")
def cmd_update() -> None:
	"""
	Updates the available licenses from the https://choosealicense.com website.
	"""
	def callback(_: Any = None):
		progress.update(task, advance=1)
		time.sleep(0.01)

	columns = Progress.get_default_columns()[:-1]

	with Progress(*columns, refresh_per_second=100) as progress:
		label = "[deep_sky_blue3]Downloading:"
		task = progress.add_task(label, start=False)

		filenames = fetch_license_filenames()
		progress.tasks[0].total = len(filenames)
		progress.start_task(task)

		coro = fetch_license_details(filenames, callback)
		licenses = asyncio.run(coro)

	console.print("Writing licenses to storage... ", style="grey78", end='')
	write_licenses_to_storage(licenses)

	time.sleep(0.5)
	console.print(f"Done! Updated {len(filenames)} licenses.\n", style="grey78")


@app.command(name="list", epilog="Example: devtools license list")
def cmd_list() -> None:
	"""
	Prints out the list of available licenses to the console.
	"""
	read_local_config_file(LicenseConfig, 'license')
	metadata = read_license_metadata()

	table = Table(title="Available Licenses")
	table.add_column("Index", justify="center", style="sandy_brown", no_wrap=True)
	table.add_column("SPDX-Identifier", style="cyan", no_wrap=True)
	table.add_column("License Name", style="orchid", no_wrap=True)

	for lic in metadata.lic_list:
		table.add_row(
			lic.index_id,
			lic.spdx_id,
			lic.title
		)

	console.print('')
	console.print(table)


@app.command(name="read", epilog="Example: devtools license read --id eupl-1.2")
def cmd_read(ident: IdentOpt = None) -> None:
	"""
	Opens the default web browser to a license on the https://choosealicense.com website.
	If the --id option is not provided, it tries to ascertain the license from the projects
	devtools config file. Else, it tries to open the browser to a valid matching identifier.
	"""
	if not ident:
		config = read_local_config_file(LicenseConfig, 'license')
		filepath = get_data_storage_path("licenses") / config.filename
		if not filepath:
			return  # TODO: complain about missing config file
	else:
		filepath = ident_to_license_filepath(ident)
		if not filepath:
			return  # TODO: complain about bad identifier

	details = read_file_into_model(filepath, LicenseDetails)
	webbrowser.open(details.web_url)


@app.command(name="compare", epilog="Example: devtools license compare")
def cmd_compare() -> None:
	"""
	Opens the default web browser to https://choosealicense.com/appendix/.
	"""
	webbrowser.open("https://choosealicense.com/appendix/")
