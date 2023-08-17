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
from enum import Enum
from pydantic import BaseModel
from abc import ABC, abstractmethod

__all__ = ["GitHubFile", "DefaultModel", "ConfigSection"]


class GitHubFile(str, Enum):
	ENV = 'GITHUB_ENV'
	OUT = 'GITHUB_OUTPUT'


class DefaultModel(ABC, BaseModel):
	"""
	An abstract base class representing a default data model.
	This class serves as a template for creating specific data models, providing
	an interface for default value management and indicating if an object instance
	has been created with default values.

	Static methods:
		__defaults__: An abstract static method that must be implemented by all
		subclasses, which returns a dictionary of default values for all the
		annotated fields of the subclass.

	Properties:
		is_default: Returns True if an instance was created with default values.
	"""
	__is_default__: bool

	def __init__(self, **data):
		is_default = False
		if not data:
			data = self.__defaults__()
			is_default = True
		super().__init__(**data)
		self.__is_default__ = is_default

	@staticmethod
	@abstractmethod
	def __defaults__() -> dict:
		pass

	@property
	def is_default(self) -> bool:
		return self.__is_default__


class ConfigSection(DefaultModel):
	"""
	This abstract base class represents individual configuration sections.

	Each subclass must implement the 'section' property to specify the section name.
	"""
	def __init__(self, **data):
		if data and self.section in data:
			data = data[self.section]
		else:
			data = dict()
		super().__init__(**data)

	@property
	@abstractmethod
	def section(self) -> str:
		"""
		The name of the section key in the top level of the config JSON file.
		"""
		pass
