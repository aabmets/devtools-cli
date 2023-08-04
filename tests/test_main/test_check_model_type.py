import pytest
from devtools_cli.utils import check_model_type


class MyClass:
	pass


class MySubClass(MyClass):
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
