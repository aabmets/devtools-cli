import pytest
from pydantic import BaseModel
from devtools_cli.utils import read_file_into_model


class BaseModelSubclass(BaseModel):
	field: str


def test_read_file_into_model_correctly_deserializes(tmp_path):
	model_path = tmp_path / 'test.json'
	model_path.write_text('{"field": "test_value"}')

	result = read_file_into_model(model_path, BaseModelSubclass)
	assert result.field == 'test_value'


def test_read_file_into_model_raises_file_not_found_error(tmp_path):
	model_path = tmp_path / 'non_existent_file.json'

	with pytest.raises(FileNotFoundError):
		read_file_into_model(model_path, BaseModelSubclass)


def test_read_file_into_model_raises_type_error(tmp_path):
	model_path = tmp_path / 'test.json'
	model_path.write_text('{"field": "test_value"}')

	with pytest.raises(TypeError):
		read_file_into_model(model_path, 'Not a BaseModel subclass')
