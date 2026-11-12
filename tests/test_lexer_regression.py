import pytest

from sloperator.errors import LexicalError
from sloperator.lexer import tokenize


def test_escaped_closing_quote_at_eof_is_an_unterminated_string():
    with pytest.raises(LexicalError) as info:
        tokenize(r"“unfinished\”")

    assert info.value.line == 1
    assert info.value.message == "unterminated string"
    assert str(info.value) == "SlopLang lexical error at line 1: unterminated string"
