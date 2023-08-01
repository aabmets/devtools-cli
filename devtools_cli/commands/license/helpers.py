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
from typing import Callable, Iterator
from devtools_cli.utils import *
from .models import *

__all__ = [
	"github_repo_tree",
	"fetch_license_filenames",
	"fetch_one_license",
	"fetch_license_details",
	"write_licenses_to_storage",
	"read_license_metadata",
	"ident_to_license_filepath",
	"write_local_license_file",
	"apply_license"
]

GH_API_REPO_TREE_TOP = "https://api.github.com/repos/github/choosealicense.com/git/trees/gh-pages"
GH_RAW_PARTIAL_PATH = "https://raw.githubusercontent.com/github/choosealicense.com/gh-pages/_licenses/"
LIC_SITE_PARTIAL_PATH = "https://choosealicense.com/licenses/"

LICENSE_DATA_SUBDIR = "licenses"
METADATA_FILENAME = ".metadata"
LICENSE_FILENAME = "LICENSE"


def github_repo_tree(url: str) -> Iterator[GitHubRepoLeaf]:
	resp = httpx.get(url, timeout=3)
	resp = orjson.loads(resp.text)
	resp = GitHubResponse(**resp)
	for leaf in resp.tree:
		yield leaf


def fetch_license_filenames() -> list[str]:
	for leaf in github_repo_tree(GH_API_REPO_TREE_TOP):
		if leaf.type == 'tree' and leaf.path == '_licenses':
			return [x.path for x in github_repo_tree(leaf.url)]
	raise RuntimeError(
		"GitHub repo structure has changed, "
		"unable to find the '_licenses' folder."
	)


async def fetch_one_license(client: httpx.AsyncClient, index: int, filename: str) -> LicenseDetails:
	resp = await client.get(GH_RAW_PARTIAL_PATH + filename)
	resp = resp.text.split(sep="---")
	spdx = filename.removesuffix('.txt')
	data = yaml.safe_load(resp[1])

	return LicenseDetails(
		web_url=LIC_SITE_PARTIAL_PATH + spdx,
		file_name=spdx + '.json',
		index_id=str(index),
		full_text=resp[2],
		**data
	)


async def fetch_license_details(filenames: list[str], callback: Callable) -> list[LicenseDetails]:
	async with httpx.AsyncClient() as client:
		tasks = []
		for index, filename in enumerate(filenames, start=1):
			coro = fetch_one_license(client, index, filename)
			task = asyncio.create_task(coro)
			task.add_done_callback(callback)
			tasks.append(task)
		return await asyncio.gather(*tasks)


def write_licenses_to_storage(licenses: list[LicenseDetails]) -> None:
	data_path = get_data_storage_path(subdir=LICENSE_DATA_SUBDIR, create=True)
	ident_map, lic_list = dict(), list()

	for lic in licenses:
		file_path = data_path / lic.file_name
		write_model_into_file(file_path, lic)

		key = f"{lic.index_id}=={lic.spdx_id}"
		ident_map[key] = str(file_path)

		lic_list.append({
			"index_id": lic.index_id,
			"spdx_id": lic.spdx_id,
			"title": lic.title
		})

	meta_data = LicenseMetadata(
		ident_map=ident_map,
		lic_list=lic_list
	)
	write_model_into_file(
		path=(data_path / METADATA_FILENAME),
		model_obj=meta_data
	)


def read_license_metadata() -> LicenseMetadata:
	data_path = get_data_storage_path(subdir=LICENSE_DATA_SUBDIR)
	return read_file_into_model(
		path=(data_path / METADATA_FILENAME),
		model_cls=LicenseMetadata
	)


def ident_to_license_filepath(ident: str) -> Path | None:
	if meta_data := read_license_metadata():
		if ident.isdecimal():
			for k, v in meta_data.ident_map.items():
				if k.startswith(ident):
					return Path(v)
		else:
			for k, v in meta_data.ident_map.items():
				if k.lower().endswith(ident.lower()):
					return Path(v)


def write_local_license_file(config_path: Path, ident: str) -> None:
	if path := ident_to_license_filepath(ident):
		data = read_file_into_model(path, LicenseDetails)
		path = config_path.parent / LICENSE_FILENAME
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
