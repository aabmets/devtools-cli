import os
import pytest
import orjson
from pathlib import Path
from devtools_cli.utils import write_local_config_file
from devtools_cli.models import ConfigSection

LOCAL_CONFIG_FILE = ".devtools"


@pytest.fixture(autouse=True)
def set_env_vars():
	os.environ['PYTEST'] = "true"


class ConfigSectionSubclass(ConfigSection):
	test_attr: str

	@property
	def section(self) -> str:
		return "section"

	@staticmethod
	def __defaults__() -> dict:
		return {"test_attr": "DEFAULT"}


def test_write_local_config_file_creates_file(tmp_path, monkeypatch):
	model_obj = ConfigSectionSubclass()
	monkeypatch.setattr(Path, 'cwd', lambda: tmp_path)

	write_local_config_file(model_obj)

	assert (tmp_path / LOCAL_CONFIG_FILE).exists()


def test_write_local_config_file_correctly_serializes(tmp_path, monkeypatch):
	model_obj = ConfigSectionSubclass()
	monkeypatch.setattr(Path, 'cwd', lambda: tmp_path)

	write_local_config_file(model_obj)

	with open(tmp_path / LOCAL_CONFIG_FILE, 'rb') as file:
		data = orjson.loads(file.read())
	assert data == {'section': {"test_attr": "DEFAULT"}}


def test_write_local_config_file_raises_type_error():
	model_obj = 'Not a ConfigSection instance'

	with pytest.raises(TypeError):
		write_local_config_file(model_obj)
