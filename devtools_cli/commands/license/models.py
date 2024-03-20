#
#   MIT License
#   
#   Copyright (c) 2024, Mattias Aabmets
#   
#   The contents of this file are subject to the terms and conditions defined in the License.
#   You may not use, modify, or distribute this file except in compliance with the License.
#   
#   SPDX-License-Identifier: MIT
#
from typing import List, Dict
from pydantic import BaseModel, Field, AliasChoices
from devtools_cli.models import DefaultModel, ConfigSection

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
	tree: List[GitHubRepoLeaf]


class LicenseListEntry(DefaultModel):
	index_id: str
	spdx_id: str = Field(validation_alias=AliasChoices("spdx-id", "spdx_id"))
	title: str

	@staticmethod
	def __defaults__() -> dict:
		return {
			"index_id": "[index_id]",
			"spdx_id": "[spdx_id]",
			"title": "[title]"
		}


class LicenseMetadata(DefaultModel):
	ident_map: Dict[str, str]
	lic_list: List[LicenseListEntry]

	@staticmethod
	def __defaults__() -> dict:
		return {
			"ident_map": dict(),
			"lic_list": list()
		}


class LicenseDetails(DefaultModel):
	title: str
	spdx_id: str = Field(validation_alias=AliasChoices("spdx-id", "spdx_id"))
	index_id: str
	permissions: List[str]
	conditions: List[str]
	limitations: List[str]
	file_name: str
	web_url: str
	full_text: str

	@staticmethod
	def __defaults__() -> dict:
		return {
			"title": "[title]",
			"spdx_id": "[spdx_id]",
			"index_id": "[index_id]",
			"permissions": list(),
			"conditions": list(),
			"limitations": list(),
			"file_name": "DEFAULT",
			"web_url": "DEFAULT",
			"full_text": "DEFAULT"
		}


class LicenseConfigHeader(DefaultModel):
	title: str
	year: str
	holder: str
	spdx_id: str
	spaces: int
	oss: bool

	@staticmethod
	def __defaults__() -> dict:
		return {
			"title": "[title]",
			"year": "[year]",
			"holder": "[holder]",
			"spdx_id": "[spdx_id]",
			"spaces": 3,
			"oss": True
		}


class LicenseConfig(ConfigSection):
	header: LicenseConfigHeader
	paths: List[str]
	file_name: str

	@staticmethod
	def __defaults__() -> dict:
		return {
			"header": LicenseConfigHeader(),
			"paths": list(),
			"file_name": "DEFAULT"
		}

	@property
	def section(self) -> str:
		return 'license_cmd'
