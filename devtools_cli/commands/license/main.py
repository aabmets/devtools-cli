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
from pathlib import Path
from typing import List, Any
from typer import Typer, Option
from typing_extensions import Annotated
from rich.progress import Progress
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .helpers import *
from .header import *
from .models import *
from devtools_cli.utils import *

app = Typer(name="license", help="Manages license headers in source code files.")
console = Console(soft_wrap=True)


YearOpt = Annotated[str, Option(
	"--year", "-y", show_default=False, help=''
	"The year of the copyright claim."
)]
HolderOpt = Annotated[str, Option(
	'--holder', '-h', show_default=False, help=''
	"The name of the copyright holder."
)]
IdentOpt = Annotated[str, Option(
	"--id", "-i", show_default=False, help=''
	"Either the numerical index or The SPDX identifier of the "
	"license from the available licenses list. Case-insensitive. "
	"Execute \"devtools license --help\" for more info."
)]
SpacesOpt = Annotated[int, Option(
	"--spaces", "-s", show_default=False, help=''
	"How many spaces the license header contents will be"
	"indented with from the comment symbol. Default: 3"
)]
PathsOpt = Annotated[List[str], Option(
	"--path", "-p", show_default=False, help=''
	"A subdirectory path in the project directory, which will be "
	"processed by this script. If provided, only the included "
	"paths are processed. Option can be used multiple times."
)]
VerboseOpt = Annotated[bool, Option(
	"--verbose", "-v", show_default=False, help=''
	"If the details of the operation should be printed to the console."
	"Default: False"
)]


@app.command(name="apply", epilog="Example: devtools license apply --spdx EUPL-1.2")
def cmd_apply(
		year: YearOpt = None,
		holder: HolderOpt = None,
		paths: PathsOpt = None,
		ident: IdentOpt = None,
		spaces: SpacesOpt = None,
		verbose: VerboseOpt = False,
):
	"""
	Applies a license header to any applicable files.
	"""
	config: LicenseConfig = read_local_config_file(LicenseConfig)
	data_path = get_data_storage_path("licenses", create=False) / config.file_name
	license_path = ident_to_license_filepath(ident or config.header.spdx_id)

	if not ident:
		if config.is_default:
			console.print("[bold red]No identifier and no local config, unable to continue.")
			raise SystemExit()
		elif config.header.spdx_id != 'none' and not data_path.exists():
			console.print("[bold red]Local config points to non-existent license data file.")
			raise SystemExit()
	elif config.is_default and (not year or not holder):
		console.print("[bold red]Missing local config requires year and holder arguments.")
		raise SystemExit()
	elif ident != '0' and (not license_path or not license_path.exists()):
		console.print("[bold red]Invalid identifier.")
		raise SystemExit()

	if year:
		config.header.year = year
	if holder:
		config.header.holder = holder
	if spaces:
		config.header.spaces = spaces

	conf_file: Path = find_local_config_file(init_cwd=True)
	conf_dir = conf_file.parent
	target_dirs = list()

	if not paths:
		for path in config.paths:
			target_dirs.append(conf_dir / path)
	if paths and '.' not in paths:
		config.paths = list()
		for path in paths:
			target_dirs.append(conf_dir / path)
			config.paths.append(path)
	if not target_dirs:
		config.paths = list()
		for path in conf_dir.iterdir():
			if path.is_dir() and not path.name.startswith('.'):
				target_dirs.append(path)

	if ident == '0':
		config.file_name = "none"
		config.header.spdx_id = 'none'
		config.header.title = 'Proprietary License'
		config.header.oss = False
	elif license_path and license_path.exists():
		details: LicenseDetails = read_file_into_model(license_path, LicenseDetails)
		config.file_name = details.file_name
		config.header.spdx_id = details.spdx_id
		config.header.title = details.title
		config.header.oss = True

	write_local_config_file(config)
	write_local_license_file(config)

	header = LicenseHeader(config.header)
	results = list()
	for target in target_dirs:
		for path in target.rglob('**/*.*'):
			if res := header.apply(path):
				results.append((path, res))
	if verbose:
		print_apply_results(results, config, conf_dir)


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
	time.sleep(0.1)


@app.command(name="list", epilog="Example: devtools license list")
def cmd_list() -> None:
	"""
	Prints out the list of available licenses to the console.
	"""
	meta_data = read_license_metadata()

	table = Table(title="Available Licenses")
	table.add_column("Index-ID", justify="left", style="sandy_brown", no_wrap=True)
	table.add_column("SPDX-Identifier", style="cyan", no_wrap=True)
	table.add_column("License Name", style="orchid", no_wrap=True)

	table.add_row('0', '---', 'Proprietary License')
	for lic in meta_data.lic_list:
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
	"""
	if not ident:
		config: LicenseConfig = read_local_config_file(LicenseConfig)
		if config.is_default:
			console.print("[bold red]No identifier and no local config, unable to continue.")
			raise SystemExit()
		filepath = get_data_storage_path("licenses") / config.file_name
		if not filepath.exists():
			console.print("[bold red]Local config points to non-existent license data file.")
			raise SystemExit()
	else:
		if ident == '0':
			text = '\n'.join(PrprTemplate.template)
			console.print(Panel.fit(text, border_style="deep_sky_blue1"))
			raise SystemExit()
		filepath = ident_to_license_filepath(ident)
		if not filepath:
			console.print("[bold red]Invalid identifier.")
			raise SystemExit()

	details = read_file_into_model(filepath, LicenseDetails)
	webbrowser.open(details.web_url)


@app.command(name="compare", epilog="Example: devtools license compare")
def cmd_compare() -> None:
	"""
	Opens the default web browser to https://choosealicense.com/appendix/.
	"""
	webbrowser.open("https://choosealicense.com/appendix/")
