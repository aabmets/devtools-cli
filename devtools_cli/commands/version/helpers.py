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
    "hash_file",
    "is_in_ignored_path",
    "hash_directory",
    "count_descriptors",
    "read_descriptor_file_version",
    "write_descriptor_file_version"
]


def hash_file(filepath: Path) -> str:
    blake_hash = hashlib.blake2b()
    with filepath.open('rb') as f:
        for byte_block in iter(lambda: f.read(4096), b''):
            blake_hash.update(byte_block)
    return blake_hash.hexdigest()[:32]


def is_in_ignored_path(filepath: Path, target: Path, ignored_paths: set) -> bool:
    rel_path = filepath.relative_to(target)
    for part in rel_path.parts:
        if part.startswith('.') or part.startswith('_'):
            return True
    for ignored_path in ignored_paths:
        if filepath.resolve().is_relative_to(ignored_path.resolve()):
            return True
    return False


def hash_directory(target: Path, ignore_paths: list) -> str:
    blake_hash = hashlib.blake2b()
    ignores = {
        (target / path).resolve()
        for path in ignore_paths
    }
    for filepath in target.rglob('*'):
        if is_in_ignored_path(filepath, target, ignores):
            continue
        elif filepath.is_file():
            file_hash = hash_file(filepath)
            blake_hash.update(file_hash.encode('utf-8'))

    return blake_hash.hexdigest()[:32]


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
