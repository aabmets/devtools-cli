#
#   Apache License 2.0
#   
#   Copyright (c) 2024, Mattias Aabmets
#   
#   The contents of this file are subject to the terms and conditions defined in the License.
#   You may not use, modify, or distribute this file except in compliance with the License.
#   
#   SPDX-License-Identifier: Apache-2.0
#

import pytest
from devtools_cli.commands.license.header import *


def test_comment_symbols_initialization():
    cs = CommentSymbols(first='#', middle='*', last='$')
    assert cs.first == '#'
    assert cs.middle == '*'
    assert cs.last == '$'
    assert not cs.has_alias

    cs = CommentSymbols(first=('#', '//'), middle=('*', '/*'), last=('$', '**'))
    assert cs.first == '#'
    assert cs.middle == '*'
    assert cs.last == '$'
    assert cs.has_alias

    with pytest.raises(TypeError):
        CommentSymbols(first=('#', '//'), middle='*', last='$')


def test_comment_symbols_use_alias():
    cs = CommentSymbols(first=('#', '//'), middle=('*', '/*'), last=('$', '**'))
    cs.use_alias = True
    assert cs.first == '//'
    assert cs.middle == '/*'
    assert cs.last == '**'


def test_comment_symbols_identical():
    cs = CommentSymbols(first='#', middle='#', last='#')
    assert cs.identical

    cs = CommentSymbols(first=('#', '//'), middle=('#', '//'), last=('#', '//'))
    assert cs.identical

    cs = CommentSymbols(first=('#', '//'), middle=('*', '/*'), last=('$', '**'))
    assert not cs.identical
