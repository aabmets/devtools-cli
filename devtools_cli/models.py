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
from pydantic import BaseModel, ValidationError
from abc import ABC, abstractmethod
from rich.pretty import pprint
from rich import print
from typing import TypeVar

__all__ = ["FilterModel", "FilterModelTypeHint", "ConfigModel", "ConfigModelTypeHint"]


class FilterModel(BaseModel, extra='allow'):
	"""
	FilterModel extends Pydantic's BaseModel with the `to_dict` method and the
	`extra='allow'` parameter allows fields that are not specified in the model definition.
	"""

	def __init__(self, **data):
		try:
			super().__init__(**data)
		except ValidationError:
			model = self.__class__.__name__
			print('-' * 60)
			print("[bold red]ERROR![/bold red] [red]A data object has failed Pydantic's model validation.")
			print(f"Data object being validated against the [deep_sky_blue1]'{model}'[/deep_sky_blue1] model:")
			pprint(data, expand_all=True)
			print()
			raise SystemExit()

	def to_dict(self) -> dict:
		"""
		Converts the model instance into a dictionary. Only fields specified
		in the model's annotations are included in the returned dictionary.
		"""
		fields = set(self.__annotations__.keys())
		return self.model_dump(include=fields, warnings=False)


FilterModelTypeHint = TypeVar('FilterModelTypeHint', bound=FilterModel)


class ConfigModel(ABC, FilterModel):
	"""
	An abstract base class representing a configuration model.

	This class serves as a template for creating specific configuration models,
	providing an interface for default value management and indicating if an object
	instance has been created with default values.

	Static methods:
		__defaults__: An abstract static method that must be implemented by all
		subclasses, which returns a dictionary of default values for all the
		annotated fields of the subclass.

	Properties:
		is_default: Returns True if an instance was created with default values.
	"""
	def __init__(self, **data):
		if not data:
			data = self.__defaults__()
			data["__is_default__"] = True
		super().__init__(**data)

	@property
	def is_default(self) -> bool:
		if hasattr(self, '__is_default__'):
			return True
		return False

	@staticmethod
	@abstractmethod
	def __defaults__() -> dict:
		pass


ConfigModelTypeHint = TypeVar('ConfigModelTypeHint', bound=ConfigModel)
