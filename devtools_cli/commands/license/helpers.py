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
	"write_local_license_file"
]

GH_API_REPO_TREE_TOP = "https://api.github.com/repos/github/choosealicense.com/git/trees/gh-pages"
GH_RAW_PARTIAL_PATH = "https://raw.githubusercontent.com/github/choosealicense.com/gh-pages/_licenses/"
LIC_SITE_PARTIAL_PATH = "https://choosealicense.com/licenses/"

LICENSE_DATA_SUBDIR = "licenses"
METADATA_FILENAME = ".metadata"
LICENSE_FILENAME = "LICENSE"


def github_repo_tree(url: str) -> Iterator[GitHubRepoLeaf]:
	"""
	This function sends a GET request to a given GitHub repository URL, parses the JSON response into a
	GitHubResponse object, then iterates through the tree structure of the repository, yielding each leaf,
	thereby fetching the tree structure of a GitHub repository and presenting individual leaves.

	Args:
		url (str): The API URL of the GitHub repository.

	Returns:
		An iterator yielding the leaves (i.e., files and directories)
		in the tree structure of the GitHub repository.

	Raises:
		HTTPError: If the GET request fails.
		JSONDecodeError: If the response cannot be decoded into JSON.
	"""
	resp = httpx.get(url, timeout=3)
	resp = orjson.loads(resp.text)
	resp = GitHubResponse(**resp)
	for leaf in resp.tree:
		yield leaf


def fetch_license_filenames() -> list[str]:
	"""
	This function iterates over the tree structure of a GitHub repository, searches
	for a subtree with the path '_licenses', and if this subtree is found, returns a
	list of all filenames within it, thereby fetching the filenames of all licenses
	in the specified GitHub repository.

	Returns:
		A list of filenames found in the '_licenses' subtree.
		Each filename is represented as a string.

	Raises:
		RuntimeError: If the '_licenses' subtree cannot be found in the
			repository, indicating a change in the repository's structure.
	"""
	for leaf in github_repo_tree(GH_API_REPO_TREE_TOP):
		if leaf.type == 'tree' and leaf.path == '_licenses':
			return [x.path for x in github_repo_tree(leaf.url)]
	raise RuntimeError(
		"GitHub repo structure has changed, "
		"unable to find the '_licenses' folder."
	)


async def fetch_one_license(client: httpx.AsyncClient, index: int, filename: str) -> LicenseDetails:
	"""
	This coroutine sends a GET request to fetch the content of a license file from the GitHub
	repository and then parses and loads the retrieved content into a LicenseDetails object,
	thereby asynchronously fetching the details of a specified license.

	Args:
		client (httpx.AsyncClient): The HTTP client to be used for the GET request.
		index (int): The index number for this license in a sequence of licenses.
		filename (str): The filename of the license in the GitHub repository.

	Returns:
		An object containing details about the license.
	"""
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
	"""
	This coroutine creates an HTTP client, schedules a coroutine for each provided filename
	to fetch the corresponding license's details from a GitHub repository, attaches a callback
	to each task to be invoked upon task completion, and then concurrently runs all scheduled tasks
	and waits for them to finish, thereby asynchronously fetching the details of multiple licenses.

	Args:
		filenames: A list of license filenames to fetch details from.
		callback: A callback function to be invoked when a license fetch task is completed.

	Returns:
		A list of LicenseDetails objects, each containing the details of a license.
	"""
	async with httpx.AsyncClient() as client:
		tasks = []
		for index, filename in enumerate(filenames, start=1):
			coro = fetch_one_license(client, index, filename)
			task = asyncio.create_task(coro)
			task.add_done_callback(callback)
			tasks.append(task)
		return await asyncio.gather(*tasks)


def write_licenses_to_storage(licenses: list[LicenseDetails]) -> None:
	"""
	This function iterates through a list of LicenseDetails objects, each containing details
	of a license, writes each license's details into a file in a specified storage directory,
	and also creates a metadata object that includes an identity map and a list of licenses,
	which it then writes into a metadata file in the same directory.

	Args:
		licenses: A list of LicenseDetails objects, each containing the details of a license.

	Raises:
		IOError: If there's a problem writing to the files.
	"""
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
	"""
	This function retrieves the path to the storage directory where the license
	metadata is stored and reads this metadata from a file into a LicenseMetadata
	object, effectively reading the license metadata from storage.

	Returns:
		An object containing the license metadata read from the file.

	Raises:
		IOError: If there's a problem reading from the file.
	"""
	data_path = get_data_storage_path(subdir=LICENSE_DATA_SUBDIR)
	return read_file_into_model(
		path=(data_path / METADATA_FILENAME),
		model_cls=LicenseMetadata
	)


def ident_to_license_filepath(ident: str) -> Path | None:
	"""
	This function retrieves the file path of a license by reading the license metadata
	and searching for a license with a given identity, which can be either an index ID
	or an SPDX ID, and if a matching license is found, the function returns its file path.

	Args:
		ident: The identity of the license. Can be either an index ID or an SPDX ID.

	Returns:
		The file path of the license if found, otherwise None.

	Raises:
		IOError: If there's a problem reading the license metadata from the file.
	"""
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
	"""
	This function writes the full text of a specified license to a local file by retrieving
	the file path of the license based on a provided identity, reading the LicenseDetails
	object from that path, and then writing the full text of the license to a file located
	in the same directory as the provided configuration file.

	Args:
		config_path: The path to a configuration file.
			The license file will be written to a file in the same directory.
		ident: The identity of the license, either an index ID or an SPDX ID.

	Raises:
		IOError: If there's a problem reading from the license file or writing to the local file.
	"""
	if path := ident_to_license_filepath(ident):
		data = read_file_into_model(path, LicenseDetails)
		path = config_path.parent / LICENSE_FILENAME
		with open(path, 'w') as file:
			file.write(data.full_text)
