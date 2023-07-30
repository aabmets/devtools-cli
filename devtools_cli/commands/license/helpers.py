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
import yaml
import httpx
import orjson
import asyncio
from pathlib import Path

GH_API_REPO_TREE_TOP = "https://api.github.com/repos/github/choosealicense.com/git/trees/gh-pages"
GH_RAW_PARTIAL_PATH = "https://raw.githubusercontent.com/github/choosealicense.com/gh-pages/_licenses/"
LIC_SITE_PARTIAL_PATH = "https://choosealicense.com/licenses/"
METADATA_FILENAME = ".metadata.json"

LicenseData = tuple[str, dict]
Licenses = list[LicenseData]


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


async def fetch_one_license(client: httpx.AsyncClient, filename: str) -> LicenseData:
	resp = await client.get(GH_RAW_PARTIAL_PATH + filename)
	resp = resp.text.split(sep="---")
	meta = yaml.safe_load(resp[1])
	spdx_id = meta.get("spdx-id", '')
	web_url = LIC_SITE_PARTIAL_PATH + spdx_id.lower()
	return filename.replace(".txt", ".json"), {
		"title": meta.get("title", ''),
		"spdx_id": spdx_id,
		"web_url": web_url,
		"full_text": resp[2]
	}


async def fetch_license_details(filenames: list[str]) -> Licenses:
	async with httpx.AsyncClient() as client:
		return await asyncio.gather(*[
			fetch_one_license(client, filename)
			for filename in filenames
		])


def get_lic_file_path(spdx_id: str) -> Path:
	data_path = Path(__file__).parent / "data"
	if not data_path.exists():
		data_path.mkdir(exist_ok=True)
	return data_path / spdx_id.lower()


def write_licenses_to_file(licenses: Licenses) -> None:
	pretty = orjson.OPT_INDENT_2
	meta_data = {}

	for filename, data in licenses:
		file_path = get_lic_file_path(filename)

		with open(file_path, 'wb') as file:
			bts = orjson.dumps(data, option=pretty)
			file.write(bts)

		del data["full_text"]
		meta_data[filename] = data

	file_path = get_lic_file_path(METADATA_FILENAME)

	with open(file_path, 'wb') as file:
		bts = orjson.dumps(meta_data, option=pretty)
		file.write(bts)


def read_licenses_metadata() -> dict:
	meta_path = get_lic_file_path(METADATA_FILENAME)
	with open(meta_path, 'rb') as file:
		return orjson.loads(file.read())


def find_license_file():
	current_path = Path.cwd()

	while current_path != current_path.root:
		license_file = current_path / 'LICENSE'
		if license_file.exists():
			return license_file
		current_path = current_path.parent

	raise FileNotFoundError(
		"\n\nERROR! License file not found. "
		"Run the script with the --help option for info."
	)


def read_license(license_file: Path, spaces: int):
	license_lines = license_file.read_text().splitlines()
	indent = '#' + (spaces * ' ')

	for i, line in enumerate(license_lines):
		license_lines[i] = f"{indent}{line}"

	return ['#'] + license_lines + ['#']


def apply_licenses(folder_path, license_lines):
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


__all__ = [
	"fetch_json",
	"fetch_license_filenames",
	"fetch_one_license",
	"fetch_license_details",
	"write_licenses_to_file",
	"read_licenses_metadata",
	"find_license_file",
	"read_license",
	"apply_licenses"
]
