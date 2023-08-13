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
from pathlib import Path
from .models import *
from .helpers import *

__all__ = [
    "count_lang_metafiles",
    "infer_project_lang",
    "SupportedProgLangs"
]


def count_lang_metafiles(track_dir: Path) -> int:
    metafiles = [x.metafile for x in SupportedProgLangs]
    files_found = [1 for f in track_dir.glob('*.*') if f.name in metafiles]
    return len(files_found)


def infer_project_lang(track_dir: Path) -> ProgLang:
    for file in track_dir.glob('*.*'):
        for lang in SupportedProgLangs:
            if file.name == lang.metafile:
                return lang
    return ProgLang()


SupportedProgLangs = [
    ProgLang(
        name='python',
        metafile='pyproject.toml',
        read=read_version_from_pyproject_toml,
        write=write_version_to_pyproject_toml
    ),
    ProgLang(
        name='javascript',
        metafile='package.json',
        read=NotImplementedError,
        write=NotImplementedError
    )
]
