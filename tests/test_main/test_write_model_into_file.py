import pytest
from pydantic import BaseModel
from devtools_cli.utils import write_model_into_file, read_file_into_model


class BaseModelSubclass(BaseModel):
	field: str


def test_write_model_into_file_correctly_serializes(tmp_path):
	model_path = tmp_path / 'test.json'
	model_obj = BaseModelSubclass(field='test_value')

	write_model_into_file(model_path, model_obj)

	result = read_file_into_model(model_path, BaseModelSubclass)
	assert result.field == 'test_value'


def test_write_model_into_file_creates_file(tmp_path):
	model_path = tmp_path / 'test.json'
	model_obj = BaseModelSubclass(field='test_value')

	write_model_into_file(model_path, model_obj)

	assert model_path.exists()


def test_write_file_into_model_raises_file_not_found_error(tmp_path):
	model_path = tmp_path
	model_obj = BaseModelSubclass(field='test_value')

	with pytest.raises(FileNotFoundError):
		write_model_into_file(model_path, model_obj)
