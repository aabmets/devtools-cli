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
import orjson
from rich import print
from pathlib import Path
from typing import Any, Callable
from pydantic import ValidationError
from orjson import JSONDecodeError, JSONEncodeError
from .models import *

GLOBAL_DATA_DIR = ".devtools-cli"
LOCAL_CONFIG_FILE = ".devtools"

__all__ = [
	"io_error_pretty_printer",
	"get_data_storage_path",
	"find_local_config_file",
	"read_local_config_file",
	"write_local_config_file",
	"read_file_into_model",
	"write_model_into_file"
]


def io_error_pretty_printer(func: Callable) -> Callable:
	def closure(*args, **kwargs) -> Any:
		try:
			return func(*args, **kwargs)
		except (OSError, JSONDecodeError, JSONEncodeError, ValidationError) as ex:
			print(ex)
			raise SystemExit()
	return closure


def check_model_type(arg: Any, expect: str) -> None:
	match expect:
		case 'class':
			if not issubclass(arg, FilterModel):
				raise TypeError(
					f"Expected a subclass of FilterModel, "
					f"but received a '{arg.__name__}' instead."
				)
		case 'object':
			if not isinstance(arg, FilterModel):
				raise TypeError(
					f"Expected an instance of FilterModel, "
					f"but received a '{type(arg)}' instead."
				)
		case _:
			raise ValueError(
				f"Expected a string literal 'class' or 'object' for the "
				f"'expect' parameter, but received '{expect}' instead."
			)


def get_data_storage_path(subdir='', filename='', create=False) -> Path:
	"""
	Gets the path for a data storage location.

	This function constructs a path to a data storage location
	in the user's home directory. Options to create the directory
	and/or file if they don't exist are provided.

	Args:
		subdir: Subdirectory under the global data directory.
		filename: Name of the file under the subdir or global data directory.
		create: If True, creates the directory and/or file if they don't exist.
			Defaults to False.

	Returns:
		A pathlib.Path object for the data storage location.
	"""
	data_path = Path.home() / GLOBAL_DATA_DIR
	if subdir:
		data_path = data_path / subdir
		if create:
			data_path.mkdir(parents=True, exist_ok=True)
	if filename:
		data_path = data_path / filename
		if create:
			data_path.touch(exist_ok=True)
	return data_path


def find_local_config_file() -> Path:
	"""
	Find the local configuration file.

	This function searches for a local configuration file starting
	from the current directory and going up to the root directory.
	If the file is not found, it creates one in the current directory.

	Returns:
		A pathlib.Path object representing the path to the local configuration file.
	"""
	current_path = Path.cwd()
	root = Path(current_path.parts[0])
	while current_path != root:
		config_path = current_path / LOCAL_CONFIG_FILE
		if config_path.exists():
			return config_path
		current_path = current_path.parent
	config_path = Path.cwd() / LOCAL_CONFIG_FILE
	config_path.touch(exist_ok=True)
	return config_path


@io_error_pretty_printer
def read_local_config_file(model_cls: type[FilterModelTypeHint], section: str = None) -> FilterModelTypeHint:
	"""
	Reads and parses a local config file (expected to be JSON), filters it by
	a given section (optional), and models the data using a provided class.
	If the file doesn't exist, it is created in the current working directory.

	Args:
		model_cls: A subclass of `FilterModel` used to model the parsed data.
		section: Section of the file to parse. If None, the entire file is used.

	Returns:
		FilterModel: Instance of `model_cls` initialized with the parsed data.

	Raises:
		TypeError: If the `model_cls` arg is not a subclass of `FilterModel`.
		JSONDecodeError: If the file contents cannot be parsed into an object.
		ValidationError: If the loaded data fails Pydantic model validation.
		IOError: If there's a problem reading from the local config file.
	"""
	check_model_type(model_cls, expect="class")
	path = find_local_config_file()

	with open(path, 'rb') as file:
		data = file.read() or b'{}'
		data = orjson.loads(data)

		if section and isinstance(section, str):
			data = data.get(section, {})

		return model_cls(**data)


@io_error_pretty_printer
def write_local_config_file(model_obj: FilterModelTypeHint, section: str = None) -> None:
	"""
	Serializes and writes a given configuration to a local file.

	Updates the specified section if provided, otherwise overwrites the whole file.
	If the file doesn't exist, it is created in the current working directory.

	Args:
		model_obj: A FilterModel instance.
		section: Optional section to update, overwrites file by default.

	Raises:
		TypeError: If `model_obj` isn't an instance of FilterModel.
		IOError: If there's a problem writing to the local config file.
		JSONEncodeError: If config can't be serialized.
	"""
	check_model_type(model_obj, expect="object")
	to_dict, path = model_obj.to_dict, find_local_config_file()

	if section and isinstance(section, str):
		data = read_local_config_file(FilterModel)
		setattr(data, section, model_obj)
		to_dict = data.model_dump

	with open(path, 'wb') as file:
		dump = orjson.dumps(to_dict(), option=orjson.OPT_INDENT_2)
		file.write(dump)


@io_error_pretty_printer
def read_file_into_model(path: Path, model_cls: type[FilterModelTypeHint]) -> FilterModelTypeHint:
	"""
	Loads JSON data from a file into an instance of a FilterModel subclass.

	Args:
		path: An instance of pathlib.Path.
		model_cls: A subclass of the FilterModel.

	Returns:
		Instance of `model_cls` populated with data.

	Raises:
		ValidationError. If the loaded data fails Pydantic model validation.
		FileNotFoundError: If the path doesn't exist or isn't a file.
		TypeError: If the `path` arg is not an instance of pathlib.Path
			or the `model_cls` arg is not a subclass of `FilterModel`.
		IOError: If there's a problem reading from the data file.
	"""
	check_model_type(model_cls, expect="class")

	if not path or not isinstance(path, Path):
		raise TypeError("The `path` arg must be an instance of pathlib.Path.")
	if not path.exists() or not path.is_file():
		raise FileNotFoundError("Path doesn't exist or isn't a file.")

	with open(path, 'rb') as file:
		data = orjson.loads(file.read())
		return model_cls(**data)


@io_error_pretty_printer
def write_model_into_file(path: Path, model_obj: FilterModelTypeHint) -> None:
	"""
	Dumps the data of a FilterModel instance into a JSON file.

	Args:
		path: An instance of pathlib.Path.
		model_obj: An instance of a subclass of FilterModel.

	Raises:
		FileNotFoundError: If the path exists and isn't a file.
		TypeError: If the `path` arg is not an instance of pathlib.Path
			or the `model_obj` arg is not an instance of `FilterModel`.
		IOError: If there's a problem writing to the data file.
	"""
	check_model_type(model_obj, expect="object")

	if not path or not isinstance(path, Path):
		raise TypeError("The `path` arg must be an instance of pathlib.Path.")
	if path.exists() and not path.is_file():
		raise FileNotFoundError("Path exists, but isn't a file.")

	with open(path, 'wb') as file:
		data = orjson.dumps(
			model_obj.to_dict(),
			option=orjson.OPT_INDENT_2
		)
		file.write(data)
