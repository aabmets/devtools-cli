import os
import pytest
from pydantic import BaseModel, ValidationError
from devtools_cli.utils import error_printer


class Model(BaseModel):
    name: str


@pytest.fixture(autouse=True)
def set_env_vars():
    os.environ['PYTEST'] = "true"


@error_printer
def func_raise_validation_error():
    Model(name=123)  # This will raise ValidationError


def test_error_printer_validation_error(capsys):
    with pytest.raises(ValidationError):
        func_raise_validation_error()
    captured = capsys.readouterr()
    assert "A data object has failed" in captured.out
