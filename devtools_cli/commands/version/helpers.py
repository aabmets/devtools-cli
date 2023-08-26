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
import hashlib
from pathlib import Path
from devtools_cli.utils import *
from .descriptors import *

__all__ = [
    "validate_version",
    "validate_digest",
    "is_in_ignored_path",
    "digest_file",
    "digest_directory",
    "count_descriptors",
    "read_descriptor_file_version",
    "write_descriptor_file_version"
]

DIGEST_LENGTH = 32


def validate_version(value: str) -> None:
    parts = value.split('.')
    for part in parts:
        if not part.isdecimal():
            raise ValueError(f"Invalid devtools SemVer identifier: {value}")


def validate_digest(value: str) -> None:
    if len(value) != DIGEST_LENGTH or any([True for c in value if not c.isalnum()]):
        raise ValueError(f"Invalid devtools version hash digest: {value}")


def is_in_ignored_path(filepath: Path, target: Path, ignored_paths: set) -> bool:
    rel_path = filepath.relative_to(target)
    for part in rel_path.parts:
        if part.startswith('.') or part.startswith('_'):
            return True
    for ignored_path in ignored_paths:
        if filepath.resolve().is_relative_to(ignored_path.resolve()):
            return True
    return False


def digest_file(filepath: Path) -> str:
    blake_hash = hashlib.blake2b()
    with filepath.open('rb') as f:
        for byte_block in iter(lambda: f.read(4096), b''):
            blake_hash.update(byte_block)
    return blake_hash.hexdigest()[:DIGEST_LENGTH]


def digest_directory(target: Path, ignore_paths: list) -> str:
    blake_hash = hashlib.blake2b()
    ignores = {
        (target / path).resolve()
        for path in ignore_paths
    }
    for filepath in target.rglob('*'):
        if is_in_ignored_path(filepath, target, ignores):
            continue
        elif filepath.is_file():
            file_hash = digest_file(filepath)
            blake_hash.update(file_hash.encode('utf-8'))

    return blake_hash.hexdigest()[:DIGEST_LENGTH]


def count_descriptors() -> int:
    config_file = find_local_config_file(init_cwd=True)
    return sum([
        1 for file in config_file.parent.glob('*.*')
        if file.name in SupportedDescriptors
    ])


def read_descriptor_file_version() -> str:
    config_file = find_local_config_file(init_cwd=True)
    for file, func in SupportedDescriptors.items():
        path = config_file.parent / file
        if path.exists() and path.is_file():
            return func('read', path)
    return '0.0.0'


def write_descriptor_file_version(new_version: str) -> None:
    config_file = find_local_config_file(init_cwd=True)
    for file, func in SupportedDescriptors.items():
        path = config_file.parent / file
        if path.exists() and path.is_file():
            func('write', path, new_version)
