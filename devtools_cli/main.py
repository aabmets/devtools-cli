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
import inspect
import importlib
from typer import Typer
from pathlib import Path

app = Typer()

package_path = Path(__file__).parent
import_dir = package_path / "commands"

for filepath in import_dir.rglob("*.py"):
	relative_path = filepath.relative_to(package_path)
	module_path = '.'.join(relative_path.with_suffix('').parts)
	module = importlib.import_module(
		package=package_path.name,
		name=f'.{module_path}'
	)
	for _, obj in inspect.getmembers(module):
		if isinstance(obj, Typer):
			name = obj.info.name
			if isinstance(name, str) and len(name) > 0:
				app.add_typer(obj, name=name)
			else:
				app.registered_commands.extend([
					*obj.registered_commands
				])

	importlib.invalidate_caches()
