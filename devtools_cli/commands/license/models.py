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
from pydantic import BaseModel, Field, AliasChoices
from devtools_cli.models import ConfigModel, ConfigSection

__all__ = [
	"GitHubRepoLeaf",
	"GitHubResponse",
	"LicenseListEntry",
	"LicenseMetadata",
	"LicenseDetails",
	"LicenseConfigHeader",
	"LicenseConfig"
]


class GitHubRepoLeaf(BaseModel):
	path: str = ''
	type: str = ''
	url: str = ''


class GitHubResponse(BaseModel):
	tree: list[GitHubRepoLeaf]


class LicenseListEntry(BaseModel):
	index_id: str
	spdx_id: str = Field(validation_alias=AliasChoices("spdx-id", "spdx_id"))
	title: str


class LicenseMetadata(BaseModel):
	ident_map: dict[str, str]
	lic_list: list[LicenseListEntry]


class LicenseDetails(BaseModel):
	title: str
	spdx_id: str = Field(validation_alias=AliasChoices("spdx-id", "spdx_id"))
	index_id: str
	permissions: list[str]
	conditions: list[str]
	limitations: list[str]
	file_name: str
	web_url: str
	full_text: str


class LicenseConfigHeader(ConfigModel):
	title: str
	year: str
	holder: str
	spdx_id: str
	spaces: int

	@staticmethod
	def __defaults__() -> dict:
		return {
			"title": "[title]",
			"year": "[year]",
			"holder": "[holder]",
			"spdx_id": "[spdx_id]",
			"spaces": 3
		}


class LicenseConfig(ConfigSection):
	header: LicenseConfigHeader
	include_paths: list[str]
	exclude_paths: list[str]
	filename: str

	@staticmethod
	def __defaults__() -> dict:
		return {
			"header": LicenseConfigHeader(),
			"include_paths": list(),
			"exclude_paths": list(),
			"filename": "DEFAULT"
		}

	@property
	def section(self) -> str:
		return 'license'
