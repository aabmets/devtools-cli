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
from pathlib import Path
from devtools_cli.utils import get_data_storage_path

GLOBAL_DATA_DIR = ".devtools-cli"


def test_get_data_storage_path_directory(monkeypatch, tmp_path):
	monkeypatch.setattr(Path, 'home', lambda: tmp_path)

	subdir = 'subdir'
	path = get_data_storage_path(subdir)
	assert path == tmp_path / GLOBAL_DATA_DIR / subdir
	assert path.is_dir()


def test_get_data_storage_path_file(monkeypatch, tmp_path):
	monkeypatch.setattr(Path, 'home', lambda: tmp_path)

	filename = 'file.txt'
	path = get_data_storage_path(filename=filename)
	assert path == tmp_path / GLOBAL_DATA_DIR / filename
	assert path.is_file()


def test_get_data_storage_path_subdir_file(monkeypatch, tmp_path):
	monkeypatch.setattr(Path, 'home', lambda: tmp_path)

	subdir = 'subdir'
	filename = 'file.txt'
	path = get_data_storage_path(subdir, filename)
	assert path == tmp_path / GLOBAL_DATA_DIR / subdir / filename
	assert path.is_file()


def test_get_data_storage_path_no_create(monkeypatch, tmp_path):
	monkeypatch.setattr(Path, 'home', lambda: tmp_path)

	subdir = 'subdir'
	filename = 'file.txt'
	path = get_data_storage_path(subdir, filename, create=False)
	assert path == tmp_path / GLOBAL_DATA_DIR / subdir / filename
	assert not path.exists()
