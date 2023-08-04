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
import pytest
from devtools_cli.models import *


class DefaultModelSubclass(DefaultModel):
	name: str

	@staticmethod
	def __defaults__():
		return {'name': 'DefaultName'}


def test_init_with_defaults():
	model = DefaultModelSubclass()

	assert model.is_default
	assert model.name == 'DefaultName'


def test_init_with_values():
	model = DefaultModelSubclass(name='CustomName')

	assert not model.is_default
	assert model.name == 'CustomName'


class ConfigSectionSubclass(ConfigSection):
	foo: str

	@property
	def section(self) -> str:
		return "test"

	@staticmethod
	def __defaults__() -> dict:
		return {"foo": "bar"}


def test_config_section_is_default():
	c = ConfigSectionSubclass()
	assert c.is_default is True
	assert c.foo == "bar"

	c = ConfigSectionSubclass(foo="baz")
	assert c.is_default is False
	assert c.foo == "baz"


def test_config_section_defaults():
	c = ConfigSectionSubclass()
	assert c.__defaults__() == {"foo": "bar"}


def test_config_section_with_data():
	c = ConfigSectionSubclass(**{"test": {"foo": "baz"}})
	assert c.is_default is False
	assert c.foo == "baz"


def test_config_section_with_invalid_data():
	with pytest.raises(ValueError):
		ConfigSectionSubclass(**{"invalid_section": {"foo": "baz"}})


def test_config_section_property():
	c = ConfigSectionSubclass()
	assert c.section == "test"
