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
import orjson
from pathlib import Path
from typing import Literal

__all__ = [
    "rw_pyproject_toml_version",
    "rw_package_json_version",
    "SupportedDescriptors"
]

Operation = Literal['read', 'write']


def rw_pyproject_toml_version(op: Operation, filepath: Path, new_version: str = '0.0.0') -> str:
    with open(filepath, 'r') as f:
        lines = f.readlines()
    searching_for_version = False
    for index, line in enumerate(lines):
        line = line.strip()
        if line in ['[tool.poetry]', '[project]']:
            searching_for_version = True
            continue
        if searching_for_version and line.startswith('['):
            break
        if searching_for_version and line.startswith('version'):
            if op == 'read':
                keyval: list = line.split('=')
                if len(keyval) == 2:
                    return keyval[-1].strip().strip('"').strip("'")
                return new_version
            elif op == 'write':
                lines[index] = f'version = "{new_version}"\n'
                with open(filepath, 'w') as f:
                    f.writelines(lines)
                    break
    return new_version


def rw_package_json_version(op: Operation, filepath: Path, new_version: str = '0.0.0') -> str:
    with open(filepath, 'rb') as f:
        text = f.read() or b'{}'
    data = orjson.loads(text)
    if isinstance(data, dict):
        if op == 'read':
            return data.get('version', new_version)
        elif op == 'write':
            data['version'] = new_version
            with open(filepath, 'wb') as f:
                text = orjson.dumps(data, option=orjson.OPT_INDENT_2)
                f.write(text)
    return new_version


SupportedDescriptors = {
    'pyproject.toml': rw_pyproject_toml_version,
    'package.json': rw_package_json_version
}
