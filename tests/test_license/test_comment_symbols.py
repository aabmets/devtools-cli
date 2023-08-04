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
