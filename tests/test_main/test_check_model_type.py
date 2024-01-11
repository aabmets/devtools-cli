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
import pytest
from devtools_cli.utils import check_model_type


class MyClass:
	pass


class MySubClass(MyClass):
	pass


class NotSubClass:
	pass


def test_check_model_type_class():
	obj = MyClass
	cmp = MyClass
	check_model_type(obj, cmp, 'class')  # must not raise

	obj = MySubClass
	cmp = MySubClass
	check_model_type(obj, cmp, 'class')  # must not raise

	obj = MySubClass
	cmp = MyClass
	check_model_type(obj, cmp, 'class')  # must not raise

	obj = MyClass()
	with pytest.raises(TypeError):
		check_model_type(obj, cmp, 'class')  # must raise

	obj = MySubClass
	cmp = NotSubClass
	with pytest.raises(TypeError):
		check_model_type(obj, cmp, 'class')  # must raise


def test_check_model_type_object():
	obj = MyClass()
	cmp = MyClass
	check_model_type(obj, cmp, 'object')  # must not raise

	obj = MySubClass()
	cmp = MyClass
	check_model_type(obj, cmp, 'object')  # must not raise

	obj = MyClass
	with pytest.raises(TypeError):
		check_model_type(obj, cmp, 'object')  # must raise

	obj = MyClass()
	cmp = MySubClass
	with pytest.raises(TypeError):
		check_model_type(obj, cmp, 'object')  # must raise
