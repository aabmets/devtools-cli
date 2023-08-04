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
import pytest
from pathlib import Path
from pydantic import ValidationError
from devtools_cli.models import ConfigSection
from devtools_cli.utils import read_local_config_file

LOCAL_CONFIG_FILE = ".devtools"


@pytest.fixture(autouse=True)
def set_env_vars():
	os.environ['PYTEST'] = "true"


class ConfigSectionSubclass(ConfigSection):
	test_attr: str

	@property
	def section(self) -> str:
		return "section"

	@staticmethod
	def __defaults__() -> dict:
		return {"test_attr": "DEFAULT"}


def test_read_local_config_file_no_file(monkeypatch, tmp_path):
	monkeypatch.setattr(Path, 'cwd', lambda: tmp_path)

	config = read_local_config_file(ConfigSectionSubclass)
	assert isinstance(config, ConfigSectionSubclass)


def test_read_local_config_file_with_empty_file(monkeypatch, tmp_path):
	monkeypatch.setattr(Path, 'cwd', lambda: tmp_path)
	(tmp_path / LOCAL_CONFIG_FILE).touch()

	config = read_local_config_file(ConfigSectionSubclass)
	assert isinstance(config, ConfigSectionSubclass)


def test_read_local_config_file_with_data(monkeypatch, tmp_path):
	monkeypatch.setattr(Path, 'cwd', lambda: tmp_path)

	with open(tmp_path / LOCAL_CONFIG_FILE, 'w') as f:
		f.write('{"test_attr": "value"}')

	config = read_local_config_file(ConfigSectionSubclass)
	assert isinstance(config, ConfigSectionSubclass)
	assert config.test_attr == "value"


def test_read_local_config_file_invalid_data(monkeypatch, tmp_path):
	monkeypatch.setattr(Path, 'cwd', lambda: tmp_path)

	with open(tmp_path / LOCAL_CONFIG_FILE, 'w') as f:
		f.write('{"key": "value"}')

	with pytest.raises(ValidationError):
		read_local_config_file(ConfigSectionSubclass)


def test_read_local_config_file_invalid_contents(monkeypatch, tmp_path):
	monkeypatch.setattr(Path, 'cwd', lambda: tmp_path)

	with open(tmp_path / LOCAL_CONFIG_FILE, 'w') as f:
		f.write('[{"key": "value"}]')

	config = read_local_config_file(ConfigSectionSubclass)
	assert config.is_default is True
