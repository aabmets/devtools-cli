from pathlib import Path
from devtools_cli.utils import find_local_config_file

LOCAL_CONFIG_FILE = ".devtools"


def test_find_local_config_file_exists(monkeypatch, tmp_path):
	config_dir = tmp_path / "dir"
	config_dir.mkdir()
	config_file = config_dir / LOCAL_CONFIG_FILE
	config_file.touch()

	def mock_cwd():
		return config_dir

	monkeypatch.setattr(Path, "cwd", mock_cwd)

	path = find_local_config_file(init_cwd=False)
	assert path == config_file


def test_find_local_config_file_not_exists_but_init(monkeypatch, tmp_path):
	config_dir = tmp_path / "dir"
	config_dir.mkdir()

	def mock_cwd():
		return config_dir

	monkeypatch.setattr(Path, "cwd", mock_cwd)

	path = find_local_config_file(init_cwd=True)
	assert path == config_dir / LOCAL_CONFIG_FILE
	assert path.is_file()


def test_find_local_config_file_not_exists_no_init(monkeypatch, tmp_path):
	config_dir = tmp_path / "dir"
	config_dir.mkdir()

	def mock_cwd():
		return config_dir

	monkeypatch.setattr(Path, "cwd", mock_cwd)

	path = find_local_config_file(init_cwd=False)
	assert path is None


def test_find_local_config_file_in_parent_dir(monkeypatch, tmp_path):
	config_file = tmp_path / LOCAL_CONFIG_FILE
	config_file.touch()
	config_dir = tmp_path / "dir"
	config_dir.mkdir()

	def mock_cwd():
		return config_dir

	monkeypatch.setattr(Path, "cwd", mock_cwd)

	path = find_local_config_file(init_cwd=False)
	assert path == config_file
