import pytest
from pathlib import Path
from devtools_cli.commands.license.header import *
from devtools_cli.commands.license.models import *

OSS_CONFIG = LicenseConfigHeader(
    title="MIT License",
    year="2023",
    holder="Mattias Aabmets",
    spdx_id="MIT",
    spaces=3,
    oss=True
)
PRPR_CONFIG = LicenseConfigHeader(
    title="Proprietary",
    year="2023",
    holder="Mattias Aabmets",
    spdx_id="-",
    spaces=3,
    oss=False
)
STARS = CommentSymbols(
    first=('/*', '//'),
    middle=(' *', '//'),
    last=(' */', '//')
)
HASHES = CommentSymbols(
    first='#',
    middle='#',
    last='#'
)
OSS_HEADER = LicenseHeader(OSS_CONFIG)
PRPR_HEADER = LicenseHeader(PRPR_CONFIG)


def get_end_index(text: list, cs: CommentSymbols) -> int:
    index = 0
    symbols = ('#!', cs.first, cs.middle, cs.last)
    for i, line in enumerate(text):
        if any([line.startswith(x) for x in symbols]):
            continue
        index = i
        break
    return index


def test_license_header_initialization():
    for obj in OSS_HEADER.__headers__:
        assert "SPDX-License" in obj.text.splitlines()[-2]
    for obj in PRPR_HEADER.__headers__:
        assert "All rights" in obj.text.splitlines()[-2]


def test_oss_license_header_apply_star_symbols(tmp_path):
    file_path = tmp_path / "test.js"
    file_path.write_text("CONTENTS")
    OSS_HEADER.apply(file_path)

    text = file_path.read_text().splitlines()
    assert text[0].startswith('/*')

    index = get_end_index(text, STARS)
    assert text[index] == "CONTENTS"

    STARS.use_alias = True
    file_path.write_text("// existing header\nCONTENTS")
    OSS_HEADER.apply(file_path)

    text = file_path.read_text().splitlines()
    assert text[0].startswith('/*')

    STARS.use_alias = False
    index = get_end_index(text, STARS)
    assert text[index] == "CONTENTS"


def test_prpr_license_header_apply_hash_symbols(tmp_path):
    file_path = tmp_path / "test.py"
    file_path.write_text("CONTENTS")
    PRPR_HEADER.apply(file_path)

    text = file_path.read_text().splitlines()
    assert text[0].startswith('#')

    index = get_end_index(text, HASHES)
    assert text[index] == "CONTENTS"

    file_path.write_text("#! usr/bin/python\nCONTENTS")
    PRPR_HEADER.apply(file_path)

    text = file_path.read_text().splitlines()
    assert text[0] == "#! usr/bin/python"
    index = get_end_index(text, HASHES)
    assert text[index] == "CONTENTS"


def test_oss_license_header_non_file_path():
    non_file_path = Path("non_existing_file.txt")

    with pytest.raises(FileNotFoundError):
        OSS_HEADER.apply(non_file_path)


def test_prpr_license_header_unsupported_file_type(tmp_path):
    test_file = tmp_path / "test.unsupported"
    test_file.write_text("This is a test file.")

    with pytest.raises(NotImplementedError):
        PRPR_HEADER.apply(test_file)