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
from typing import TypeVar
from pydantic import BaseModel, ValidationError
from rich.pretty import pprint
from rich import print

__all__ = ["FilterModel", "FilterModelTypeHint"]


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
		return self.model_dump(include=fields)


FilterModelTypeHint = TypeVar('FilterModelTypeHint', bound=FilterModel)
