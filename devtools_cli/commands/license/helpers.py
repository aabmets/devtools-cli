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
import yaml
import httpx
import orjson
import asyncio
from pathlib import Path
from typing import Callable
from devtools_cli.utils import *
from .classes import *

__all__ = [
	"fetch_json",
	"fetch_license_filenames",
	"fetch_one_license",  # async
	"fetch_license_details",  # async
	"get_license_storage_path",
	"write_licenses_to_storage",
	"read_licenses_metadata",
	"ident_to_license_filepath",
	"filename_to_license_filepath",
	"read_license_details",
	"read_local_license_config",
	"write_local_license_config",
	"write_local_license_file",
	"apply_license"
]

GH_API_REPO_TREE_TOP = "https://api.github.com/repos/github/choosealicense.com/git/trees/gh-pages"
GH_RAW_PARTIAL_PATH = "https://raw.githubusercontent.com/github/choosealicense.com/gh-pages/_licenses/"
LIC_SITE_PARTIAL_PATH = "https://choosealicense.com/licenses/"
METADATA_FILENAME = ".metadata"
LICENSE_FILENAME = "LICENSE"


def fetch_json(url: str) -> dict:
	resp = httpx.get(url, timeout=3)
	return orjson.loads(resp.text)


def fetch_license_filenames() -> list[str]:
	resp = fetch_json(GH_API_REPO_TREE_TOP)
	for leaf in resp.get('tree'):
		if leaf.get('type') == 'tree' and leaf.get('path') == '_licenses':
			resp = fetch_json(leaf.get('url'))
			return [x.get('path') for x in resp.get('tree')]
	return []


async def fetch_one_license(client: httpx.AsyncClient, index: int, filename: str) -> dict:
	resp = await client.get(GH_RAW_PARTIAL_PATH + filename)
	resp = resp.text.split(sep="---")
	meta = yaml.safe_load(resp[1])
	spdx_id = meta.get("spdx-id", '')
	web_url = LIC_SITE_PARTIAL_PATH + spdx_id.lower()
	return {
		"title": meta.get("title", ''),
		"spdx_id": spdx_id,
		"index_id": str(index),
		"permissions": meta.get("permissions", []),
		"conditions": meta.get("conditions", []),
		"limitations": meta.get("limitations", []),
		"filename": filename.replace(".txt", ".json"),
		"web_url": web_url,
		"full_text": resp[2]
	}


async def fetch_license_details(filenames: list[str], callback: Callable) -> list[dict]:
	async with httpx.AsyncClient() as client:
		tasks = []
		for index, filename in enumerate(filenames, start=1):
			coro = fetch_one_license(client, index, filename)
			task = asyncio.create_task(coro)
			task.add_done_callback(callback)
			tasks.append(task)
		return await asyncio.gather(*tasks)


def get_license_storage_path(filename: str) -> Path:
	data_path = get_global_data_dir() / "licenses"
	data_path.mkdir(parents=True, exist_ok=True)
	return data_path / filename


def write_licenses_to_storage(licenses: list[dict]) -> None:
	pretty = orjson.OPT_INDENT_2
	ident_map, lic_list = {}, []

	for lic in licenses:
		filename = lic.pop("filename")
		file_path = get_license_storage_path(filename)

		with open(file_path, 'wb') as file:
			data = orjson.dumps(lic, option=pretty)
			file.write(data)

		key = f"{lic['index_id']}=={lic['spdx_id']}"
		ident_map[key] = str(file_path)
		lic_list.append({
			"index_id": lic["index_id"],
			"spdx_id": lic["spdx_id"],
			"title": lic["title"]
		})

	file_path = get_license_storage_path(METADATA_FILENAME)
	metadata = {
		"ident_map": ident_map,
		"lic_list": lic_list
	}
	with open(file_path, 'wb') as file:
		data = orjson.dumps(metadata, option=pretty)
		file.write(data)


def read_licenses_metadata() -> dict:
	meta_path = get_license_storage_path(METADATA_FILENAME)
	if meta_path.exists():
		with open(meta_path, 'rb') as file:
			data = orjson.loads(file.read())
			return data
	return {}


def ident_to_license_filepath(ident: str) -> Path | None:
	metadata = read_licenses_metadata()
	is_decimal = ident.isdecimal()
	for k, v in metadata["ident_map"].items():
		func = k.startswith if is_decimal else k.endswith
		if func(ident) is True:
			return Path(v)


def filename_to_license_filepath(filename: str) -> Path | None:
	data_dir = get_global_data_dir()
	file_path = data_dir / "licenses" / filename
	return file_path if file_path.exists() else None


def read_license_details(path: Path) -> LicenseData:
	with open(path, 'rb') as file:
		data = orjson.loads(file.read())
		return LicenseData(**data)


def read_local_license_config() -> LicenseConfig:
	config = read_local_config_file()
	lic = config.get("license", {})
	hdr = lic.get("header", {})
	lic["header"] = HeaderConfig(**hdr)
	return LicenseConfig(**lic)


def write_local_license_config(data: LicenseConfig) -> None:
	config = read_local_config_file()
	config["license"] = data.to_dict()
	write_local_config_file(config)


def write_local_license_file(ident: str) -> None:
	if path := ident_to_license_filepath(ident):
		data = read_license_details(path)
		path = find_local_config_file()
		path = path.parent / LICENSE_FILENAME
		with open(path, 'w') as file:
			file.write(data.full_text)


def apply_license(folder_path, license_lines):
	license_text = "\n".join(license_lines)
	for py_file in folder_path.rglob('*.py'):
		content = py_file.read_text().splitlines()
		current_header = content[:len(license_lines)]
		if current_header == license_lines:
			print("skipping")
			continue
		if content and content[0].startswith('#'):
			for i, line in enumerate(content):
				if not line.startswith('#'):
					break
			else:
				i = len(content)
			content = content[i:]
		content = license_text + "\n" + "\n".join(content)
		py_file.write_text(content)
