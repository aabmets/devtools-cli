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
import os
import orjson
from pathlib import Path
from functools import wraps
from typing import Any, Callable, Literal
from pydantic import BaseModel, ValidationError
from rich.prompt import Confirm
from rich.pretty import pprint
from rich import print
from .models import *

GLOBAL_DATA_DIR = ".devtools-cli"
LOCAL_CONFIG_FILE = ".devtools"

__all__ = [
	"error_printer",
	"check_model_type",
	"get_data_storage_path",
	"find_local_config_file",
	"read_local_config_file",
	"write_local_config_file",
	"read_file_into_model",
	"write_model_into_file",
	"read_from_github_file",
	"write_to_github_file"
]


def error_printer(func: Callable) -> Callable:
	@wraps(func)
	def closure(*args, **kwargs) -> Any:
		try:
			return func(*args, **kwargs)
		except ValidationError as ex:
			obj = orjson.loads(ex.json())
			part1, part2 = "ERROR! A data object has failed ", " model validation."
			print('-' * len(part1 + f"'{ex.title}'" + part2))
			print(f"[bold red]{part1}[deep_sky_blue1]'{ex.title}'[bold red]{part2}")
			if os.environ.get("PYTEST") is None:  # pragma: no cover
				choice = Confirm.ask("Do you want to read the ValidationError details?")
				if choice is True:
					if isinstance(obj, list):
						[pprint(x) for x in obj]
					else:
						pprint(obj)
					raise
				return ''
			print()
			raise

	return closure


def check_model_type(obj: Any, cmp: Any, expect: Literal['class', 'object']) -> None:
	match expect:
		case 'class':
			if not isinstance(obj, type):
				raise TypeError(
					f"Expected a subclass of '{cmp.__name__}', but received "
					f"an instance of '{obj.__class__.__name__}' instead."
				)
			elif not issubclass(obj, cmp):
				raise TypeError(
					f"Expected a subclass of '{cmp.__name__}', but "
					f"received class '{obj.__name__}' instead."
				)
		case 'object':
			if isinstance(obj, type):
				raise TypeError(
					f"Expected an instance of '{cmp.__name__}' subclass, "
					f"but received class '{obj.__name__}' instead."
				)
			if not isinstance(obj, cmp):
				raise TypeError(
					f"Expected an instance of {cmp.__name__} subclass, "
					f"but received '{obj.__class__.__name__}' instead."
				)
		case _:  # pragma: no cover
			raise ValueError(
				f"Expected a string literal 'class' or 'object' for the "
				f"'expect' parameter, but received '{expect}' instead."
			)


def get_data_storage_path(subdir='', filename='', create=True) -> Path:
	"""
	Gets the path for a data storage location.

	This function constructs a path to a data storage location
	in the user's home directory. Options to create the directory
	and/or file if they don't exist are provided.

	Args:
		subdir: Subdirectory under the global data directory.
		filename: Name of the file under the `subdir` or the global data directory.
		create: If True, creates the directory and/or the file if they don't exist.
			Defaults to False.

	Returns:
		A `pathlib.Path` object for the data storage location.
	"""
	data_path = Path.home() / GLOBAL_DATA_DIR
	if create:
		data_path.mkdir(parents=True, exist_ok=True)
	if subdir:
		data_path = data_path / subdir
		if create:
			data_path.mkdir(parents=True, exist_ok=True)
	if filename:
		data_path = data_path / filename
		if create:
			data_path.touch(exist_ok=True)
	return data_path


def find_local_config_file(*, init_cwd: bool) -> Path | None:
	"""
	Find the local configuration file.

	This function searches for a local configuration file starting from the current working
	directory and going up to the root directory. If the file is not found and the `init_cwd`
	keyword argument is True, a new config file is created in the current working directory.

	Returns:
		Either None, if the file is not found and `init_cwd` is False, or an instance
		of `pathlib.Path` representing the path to the local configuration file.
	"""
	current_path = Path.cwd()
	root = Path(current_path.parts[0])

	while current_path != root:
		config_path = current_path / LOCAL_CONFIG_FILE
		if config_path.exists():
			return config_path
		current_path = current_path.parent

	if init_cwd:
		config_path = Path.cwd() / LOCAL_CONFIG_FILE
		config_path.touch(exist_ok=True)
		return config_path


@error_printer
def read_local_config_file(model_cls: type[ConfigSection]) -> ConfigSection:
	"""
	Reads and parses a local config file into an instance of `ConfigSection`.

	Args:
		model_cls: A subclass of `ConfigSection` used to model the parsed data.

	Returns:
		ConfigSection: Instance of `model_cls` initialized with the parsed data.

	Raises:
		TypeError: If the `model_cls` arg is not a subclass of `ConfigSection`.
		JSONDecodeError: If the file contents cannot be parsed into an object.
		ValidationError: If the loaded data fails Pydantic model validation.
		IOError: If there's a problem reading from the local config file.
	"""
	check_model_type(model_cls, DefaultModel, expect="class")

	if path := find_local_config_file(init_cwd=False):
		with open(path, 'rb') as file:
			data = file.read() or b'{}'
		data = orjson.loads(data)
		if not isinstance(data, dict):
			data = dict()
		return model_cls(**data)
	return model_cls()


@error_printer
def write_local_config_file(model_obj: ConfigSection) -> None:
	"""
	Serializes and writes a given configuration to a local file.
	If the file doesn't exist, it is created in the current working directory.

	Args:
		model_obj: An instance of `ConfigSection` subclass.

	Raises:
		TypeError: If `model_obj` isn't an instance of `ConfigModel`.
		IOError: If there's a problem writing to the local config file.
		JSONEncodeError: If the model object can't be serialized.
	"""
	check_model_type(model_obj, ConfigSection, expect="object")
	path = find_local_config_file(init_cwd=True)

	with open(path, 'rb') as file:
		data = file.read() or b'{}'

	data = orjson.loads(data)
	dump = model_obj.model_dump(warnings=False)
	data[model_obj.section] = dump
	dump = orjson.dumps(data, option=orjson.OPT_INDENT_2)

	with open(path, 'wb') as file:
		file.write(dump)


@error_printer
def read_file_into_model(path: Path, model_cls: type[BaseModel]) -> BaseModel:
	"""
	Loads JSON data from a file into a Pydantic model.

	Args:
		path: An instance of `pathlib.Path`.
		model_cls: A subclass of Pydantic's `BaseModel`.

	Returns:
		An instance of `model_cls` populated with data.

	Raises:
		ValidationError. If the loaded data fails Pydantic model validation.
		FileNotFoundError: If the path doesn't exist or isn't a file.
		JSONDecodeError: If the file contents cannot be parsed into an object.
		TypeError: If the `path` arg is not an instance of `pathlib.Path`
			or the `model_cls` arg is not a subclass of `BaseModel`.
		IOError: If there's a problem reading from the data file.
	"""
	check_model_type(model_cls, BaseModel, expect="class")

	if not path.exists() or not path.is_file():
		raise FileNotFoundError(f"Path doesn't exist or isn't a file: {path}")

	with open(path, 'rb') as file:
		data = file.read() or b'{}'

	data = orjson.loads(data)
	return model_cls(**data)


@error_printer
def write_model_into_file(path: Path, model_obj: BaseModel) -> None:
	"""
	Dumps an instance of a Pydantic's model into a JSON file.

	Args:
		path: An instance of `pathlib.Path`.
		model_obj: An instance of a Pydantic's model.

	Raises:
		FileNotFoundError: If the path exists and isn't a file.
		JSONEncodeError: If the model object can't be serialized.
		TypeError: If the `path` arg is not an instance of `pathlib.Path`
			or the `model_obj` arg is not an instance of `BaseModel`.
		IOError: If there's a problem writing to the data file.
	"""
	check_model_type(model_obj, BaseModel, expect="object")

	if path.exists() and not path.is_file():
		raise FileNotFoundError(f"Path exists, but isn't a file: {path}")

	dump = model_obj.model_dump(warnings=False)
	data = orjson.dumps(dump, option=orjson.OPT_INDENT_2)

	with open(path, 'wb') as file:
		file.write(data)


def read_from_github_file(key: str, gh_file: GitHubFile) -> str:
	"""
	Reads key-value pairs from GitHub Action files.

	Args:
		key: Name of the variable to read.
		gh_file: A value of the enum GitHubFile.

	Raises:
		RuntimeError: If not running inside a GitHub Actions runner.
	"""
	if gh_file in os.environ:
		with open(os.environ[gh_file], 'r') as file:
			lines = file.readlines()

		lines = [line.split('=') for line in lines]
		gh_vars = {line[0]: line[1] for line in lines if len(line) == 2}
		return gh_vars.get(key, '')

	raise RuntimeError(
		"Cannot read variables from GitHub Action files "
		"when not running inside a GitHub Actions runner."
	)


def write_to_github_file(key: str, value: str, gh_file: GitHubFile) -> None:
	"""
	Appends key-value pairs to GitHub Action files.

	Args:
		key: Name of the variable key.
		value: The value of the variable.
		gh_file: A value of the enum GitHubFile.

	Raises:
		RuntimeError: If not running inside a GitHub Actions runner.
	"""
	if gh_file in os.environ:
		with open(os.environ[gh_file], 'r') as file:
			lines = file.readlines()

		lines = [line.split('=') for line in lines]
		gh_vars = {line[0]: line[1] for line in lines if len(line) == 2}

		gh_vars[key] = value
		lines = [f"{k}={v}\n" for k, v in gh_vars.items()]

		with open(os.environ[gh_file], 'w') as file:
			file.writelines(lines)
			return

	raise RuntimeError(
		"Cannot write variables into GitHub Action files "
		"when not running inside a GitHub Actions runner."
	)
