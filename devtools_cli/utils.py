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
import orjson
from pathlib import Path

GLOBAL_DATA_DIR = ".devtools-cli"
LOCAL_CONFIG_FILE = ".devtools"

__all__ = [
	"get_global_data_dir",
	"find_local_config_file",
	"read_local_config_file",
	"write_local_config_file"
]


def get_global_data_dir() -> Path:
	data_path = Path.home() / GLOBAL_DATA_DIR
	data_path.mkdir(parents=True, exist_ok=True)
	return data_path


def find_local_config_file() -> Path:
	current_path = Path.cwd()
	while current_path != current_path.root:
		config_path = current_path / LOCAL_CONFIG_FILE
		if config_path.exists():
			return config_path
		current_path = current_path.parent
	new_path = Path.cwd() / LOCAL_CONFIG_FILE
	new_path.touch(exist_ok=True)
	return new_path


def read_local_config_file() -> dict:
	path = find_local_config_file()
	with open(path, 'rb') as file:
		data = file.read() or '{}'
		return orjson.loads(data)


def write_local_config_file(config: dict) -> None:
	path = find_local_config_file()
	with open(path, 'wb') as file:
		pretty = orjson.OPT_INDENT_2
		dump = orjson.dumps(config, option=pretty)
		file.write(dump)
