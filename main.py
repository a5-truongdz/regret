"""
A simple interpreter for my language.
(On a single file)
"""

from enum import Enum, auto
from typing import *    # type: ignore

"""
Lexer.
"""

class Token(Enum):
    def __repr__(self) -> str:
        return f"Token.{self.name}"

    """
    Keywords.
    """
    FUNC     = auto()
    CALL     = auto()
    DEF      = auto()
    REF      = auto()
    PRINT    = auto()
    LPRINT   = auto()
    RETURN   = auto()
    IF       = auto()
    ELSE     = auto()
    MUT      = auto()
    BLANK    = auto()
    FOR      = auto()
    BREAK    = auto()
    CONTINUE = auto()
    COPY     = auto()
    ADD      = auto()
    SUB      = auto()
    MUL      = auto()
    DIV      = auto()
    MOD      = auto()

    """
    Types.
    """
    TYPE_INT   = auto()
    TYPE_STR   = auto()
    TYPE_BOOL  = auto()
    TYPE_FLOAT = auto()

    """
    Literals.
    """
    LITERAL_INT   = auto()
    LITERAL_STR   = auto()
    LITERAL_BOOL  = auto()
    LITERAL_FLOAT = auto()

    """
    Stuffs.
    """
    IDENTIFIER = auto()
    INDENT     = auto()
    DEDENT     = auto()
    EOF        = auto()
    REGISTER   = auto()
    NEWLINE    = auto()
    NULL       = auto()

    """
    Symbols.
    """
    COMMA      = auto()
    COLON      = auto()
    SEMICOLON  = auto()


"""
Keywords map.
"""
KEYWORDS: dict[str, Token] = {
    "func":     Token.FUNC,
    "call":     Token.CALL,
    "def":      Token.DEF,
    "ref":      Token.REF,
    "print":    Token.PRINT,
    "lprint":   Token.LPRINT,
    "return":   Token.RETURN,
    "if":       Token.IF,
    "else":     Token.ELSE,
    "mut":      Token.MUT,
    "blank":    Token.BLANK,
    "for":      Token.FOR,
    "break":    Token.BREAK,
    "continue": Token.CONTINUE,
    "copy":     Token.COPY,
    "add":      Token.ADD,
    "sub":      Token.SUB,
    "mul":      Token.MUL,
    "div":      Token.DIV,
    "mod":      Token.MOD,
}

"""
Types map.
"""
TYPES: dict[str, Token] = {
    "int":   Token.TYPE_INT,
    "str":   Token.TYPE_STR,
    "bool":  Token.TYPE_BOOL,
    "float": Token.TYPE_FLOAT
}

"""
Symbols map.
"""
SYMBOLS: dict[str, Token] = {
    ":":  Token.COLON,
    ";":  Token.SEMICOLON,
    ",":  Token.COMMA
}

"""
Booleans map.
"""
BOOLEANS: dict[str, Token] = {
    "true":  Token.LITERAL_BOOL,
    "false": Token.LITERAL_BOOL
}

class Lexer:
    class IndentError(Exception):
        def __init__(self, level: int) -> None:
            super().__init__(f"bad indent: {level}")

    class UnexpectedCharacter(Exception):
        def __init__(self, char: str, row: int) -> None:
            super().__init__(f"unexpected character {char!r} at line {row}")

    class UnterminatedString(Exception):
        def __init__(self, row: int) -> None:
            super().__init__(f"unterminated string literal at line {row}")

def lexer(src: str) -> list[Token | tuple[Token, str] | tuple[Token, bool] | tuple[Token, float] | tuple[Token, int]]:
    output: list[Token | tuple[Token, str] | tuple[Token, bool] | tuple[Token, float] | tuple[Token, int]] = []
    ptr: int = 0
    indent_stack: list[int] = [0]
    row: int = 1
    src_size: int = len(src)
    while ptr < src_size:
        char: str = src[ptr]
        if char.isalpha() or char == "_":
            start: int = ptr
            while ptr < src_size and (src[ptr].isalnum() or src[ptr] == "_"):
                ptr += 1
            word: str = src[start:ptr]
            if word in KEYWORDS:
                output.append(KEYWORDS[word])
            elif word in TYPES:
                output.append(TYPES[word])
            elif word in BOOLEANS:
                output.append((BOOLEANS[word], word == "true"))
            elif word == "null":
                output.append(Token.NULL)
            elif word.startswith("r"):
                try:
                    int(word[1:])
                    output.append((Token.REGISTER, word))
                except ValueError:
                    output.append((Token.IDENTIFIER, word))
            else:
                output.append((Token.IDENTIFIER, word))
            continue
        elif char in SYMBOLS:
            output.append(SYMBOLS[char])
        elif char == "\n":
            output.append(Token.NEWLINE)
            row += 1
            ptr += 1
            count: int = 0
            while ptr < src_size and src[ptr] == " ":
                count += 1
                ptr += 1
            prev: int = indent_stack[-1]
            if count > prev:
                indent_stack.append(count)
                output.append(Token.INDENT)
            elif count < prev:
                while indent_stack and indent_stack[-1] > count:
                    indent_stack.pop()
                    output.append(Token.DEDENT)
                if indent_stack[-1] != count:
                    raise Lexer.IndentError(count)
            continue
        elif char.isdecimal():
            start: int = ptr
            has_dot: bool = False
            while ptr < src_size and (src[ptr].isdecimal() or src[ptr] == "."):
                if src[ptr] == ".":
                    if has_dot:
                        break
                    has_dot = True
                ptr += 1
            num: str = src[start:ptr]
            if has_dot:
                output.append((Token.LITERAL_FLOAT, float(num)))
            else:
                output.append((Token.LITERAL_INT, int(num)))
            continue
        elif char == "\"" or char == "'":
            quote: str = char
            ptr += 1
            start: int = ptr
            while ptr < src_size and src[ptr] != quote:
                if src[ptr] == "\n":
                    raise Lexer.UnterminatedString(row)
                ptr += 1
            if ptr >= src_size:
                raise Lexer.UnterminatedString(row)
            string: str = src[start:ptr]
            ptr += 1
            output.append((Token.LITERAL_STR, string))
            continue
        elif char.isspace():
            pass
        else:
            raise Lexer.UnexpectedCharacter(char, row)
        ptr += 1
    while len(indent_stack) > 1:
        indent_stack.pop()
        output.append(Token.DEDENT)
    output.append(Token.EOF)
    return output

"""
AST nodes.
"""

class Literal:
    def __init__(self, value: int | bool | str | float | None) -> None:
        self.value: int | bool | str | float | None = value

    def __repr__(self) -> str:
        return f"Literal({self.value!r})"

class Identifier:
    def __init__(self, name: str) -> None:
        self.name: str = name

    def __repr__(self) -> str:
        return f"Identifier({self.name})"

class Register:
    def __init__(self, name: str) -> None:
        self.name: str = name
    
    def __repr__(self) -> str:
        return f"Register({self.name})"

class Def:
    def __init__(self, name: Identifier, type_: Token, value: Literal) -> None:
        self.name: Identifier = name
        self.type: Token = type_
        self.value: Literal = value

    def __repr__(self) -> str:
        return f"Def(name={self.name}, type={self.type}, value={self.value})"

class Ref:
    def __init__(self, variable: Identifier, register: Register) -> None:
        self.variable: Identifier = variable
        self.register: Register = register

    def __repr__(self) -> str:
        return f"Ref(variable={self.variable}, register={self.register})"
