import re
import sys
import unicodedata
from dataclasses import dataclass
from collections import defaultdict

def line_pos(program: str, span: tuple[int, int]):
    line = program.count("\n", 0, span[0])
    pos = span[0] - program.rfind("\n", 0, span[0]) - 1
    return line + 1, pos, program.splitlines()[line]

def text_width(text: str):
    width = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ('F', 'W', 'A'):
            width += 2
        else:
            width += 1
    return width

def caret_tilda(text: str, from_: int, to: int):
    pos_from = text_width(text[:from_])
    pos_to = text_width(text[:to])
    return " " * pos_from + "^" + "~" * (pos_to - pos_from - 1)

@dataclass
class Token:
    token_type: str
    content: str
    span: tuple[int, int]

@dataclass
class Variable:
    name: str

@dataclass
class Program:
    program: str
    tokens: list[Token]

class Undefined:
    def __repr__(self):
        return "Undefined"

class InvalidTokenException(Exception):
    def __init__(self, program: str, token: Token):
        line, pos, line_content = line_pos(program, token.span)
        content = token.content
        message = (
            f"[解析時エラー]\n"
            f"無効なトークン「{content}」が見つかりました。\n"
            f"[発生箇所]\n"
            f"{line}行目\n{line_content}\n" +
            caret_tilda(line_content, pos, pos + len(content))
        )
        super().__init__(message)

class InvalidProgramException(Exception):
    def __init__(self, program: str, token: Token, exception: Exception):
        line, pos, line_content = line_pos(program, token.span)
        content = token.content
        message = (
            f"[解析時エラー]\n"
            f"{content}は無効なプログラムです。\n"
            f"[発生箇所]\n"
            f"{line}行目\n{line_content}\n" +
            caret_tilda(line_content, pos, pos + len(content))
        ) + "\n" + str(exception)
        super().__init__(message)

class InvalidNumberException(Exception):
    def __init__(self, program: str, value: str, token: Token):
        print(token)
        line, pos, line_content = line_pos(program, token.span)
        message = (
            f"[実行時エラー]\n"
            f"{value}は数値ではありません。\n"
            f"[発生箇所]\n"
            f"{line}行目\n{line_content}\n" +
            caret_tilda(line_content, pos, pos + len(token.content))
        )
        super().__init__(message)

class ErrorWhileRunningCodeException(Exception):
    def __init__(self, program: str, token: Token, exception: Exception):
        line, pos, line_content = line_pos(program, token.span)
        content = token.content
        message = (
            f"[実行時エラー]\n"
            f"{content}に渡されたプログラムを実行中にエラーが発生しました。\n"
            f"[発生箇所]\n"
            f"{line}行目\n{line_content}\n" +
            caret_tilda(line_content, pos, pos + len(content))
        ) + "\n" + str(exception)
        super().__init__(message)

class NoSuchCommandException(Exception):
    def __init__(self, program: str, token: Token):
        line, pos, line_content = line_pos(program, token.span)
        content = token.content
        message = (
            f"[解析時エラー]\n"
            f"コマンド「{content}」は存在しません。\n"
            f"[発生箇所]\n"
            f"{line}行目\n{line_content}\n" +
            caret_tilda(line_content, pos, pos + len(content))
        )
        super().__init__(message)

class StackTooShortException(Exception):
    def __init__(self, program: str, stack: list, required_amount: int, token: Token):
        line, pos, line_content = line_pos(program, token.span)
        content = token.content
        message = (
            f"[実行時エラー]\n"
            f"スタックの要素が足りません！\n"
            f"コマンド{content}は{required_amount}個の値を要求していますが、{len(stack)}個しかスタックにありません。\n"
            f"[発生箇所]\n"
            f"{line}行目\n{line_content}\n" +
            caret_tilda(line_content, pos, pos + len(content))
        )
        super().__init__(message)


class WrongTypeException(Exception):
    def __init__(self, program: str, stack: list, types: list[type], token: Token):
        line, pos, line_content = line_pos(program, token.span)
        content = token.content
        message = (
            f"[実行時エラー]\n"
            f"{content}は{[i.__name__ for i in types]}を要求しますが、{[type(i).__name__ for i in stack[:len(types)]]}が渡されました。\n"
            f"[発生箇所]\n"
            f"{line}行目\n{line_content}\n" +
            caret_tilda(line_content, pos, pos + len(content))
        )
        super().__init__(message)

class ZeroDivisionException(Exception):
    def __init__(self, program: str, token: Token):
        line, pos, line_content = line_pos(program, token.span)
        content = token.content
        message = (
            f"[実行時エラー]\n"
            f"0除算が発生しました。\n"
            f"[発生箇所]\n"
            f"{line}行目\n{line_content}\n" +
            caret_tilda(line_content, pos, pos + len(content))
        )
        super().__init__(message)

class BraceNotEnoughException(Exception):
    def __init__(self, program: str, span: tuple[int, int]):
        line, pos, line_content = line_pos(program, span)
        message = (
            f"[解析時エラー]\n"
            f"対応する括弧が見つかりません。\n"
            f"[発生箇所]\n"
            f"{line}行目\n{line_content}\n" +
            caret_tilda(line_content, span[0], span[1])
        )
        super().__init__(message)

class IndexNotPositiveIntegerException(Exception):
    def __init__(self, program: str, token: Token, index: float):
        line, pos, line_content = line_pos(program, token.span)
        content = token.content
        message = (
            f"[実行時エラー]\n"
            f"インデックスは正の整数である必要がありますが、{index}が渡されました。\n"
            f"[発生箇所]\n"
            f"{line}行目\n{line_content}\n" +
            caret_tilda(line_content, pos, pos + len(content))
        )
        super().__init__(message)

class IndexOutOfRangeException(Exception):
    def __init__(self, program: str, token: Token, list_length: int, index: float):
        line, pos, line_content = line_pos(program, token.span)
        content = token.content
        message = (
            f"[実行時エラー]\n"
            f"長さ{list_length}のリストに対して、インデックス{index}は範囲外です。\n"
            f"[発生箇所]\n"
            f"{line}行目\n{line_content}\n" +
            caret_tilda(line_content, pos, pos + len(content))
        )
        super().__init__(message)

class NoSuchKeyException(Exception):
    def __init__(self, program: str, token: Token, key: str):
        line, pos, line_content = line_pos(program, token.span)
        content = token.content
        message = (
            f"[実行時エラー]\n"
            f"渡された辞書に指定されたキー{key}は存在しません。\n"
            f"[発生箇所]\n"
            f"{line}行目\n{line_content}\n" +
            caret_tilda(line_content, pos, pos + len(content))
        )
        super().__init__(message)

UNDEFINED = Undefined()

TOKEN_DICT = {
    "NUMBER": r"\d+(\.\d*)?",
    "STRING": r"\".*?\"",
    "CODE": r"{.*?}",
    "BOOLEAN": r"True|False",
    "COMMAND": r"[a-z]+|[\+\-\*\/\%\#]|[><=!]=?",
    "VARIABLE": r"\$[A-Za-z][A-Za-z0-9_]*",
    "INVALID": r".*"
}

def tokenize(program: str):
    pos = 0
    is_brace_mode = False
    chars_in_brace = ""
    brace_start_pos = 0
    brace_count = 0
    tokens = []
    regex = "|".join([f"(?P<{key}>{val})" for key, val in TOKEN_DICT.items()])
    compiled = re.compile(regex)
    while pos < len(program):
        char = program[pos]
        if is_brace_mode:
            if char == "{":
                brace_count += 1
            if char == "}":
                brace_count -= 1
            pos += 1
            if brace_count == 0:
                is_brace_mode = False
                tokens.append(Token("CODE", "{" + chars_in_brace + "}", (brace_start_pos, pos)))
            chars_in_brace += char
            continue
        if char == "{":
            brace_count += 1
            brace_start_pos = pos
            pos += 1
            chars_in_brace = ""
            is_brace_mode = True
            continue
        if char.isspace():
            pos += 1
            continue
        
        match = compiled.match(program, pos)
        token_type = match.lastgroup
        value = match.group(token_type)
        span = match.span()
        token = Token(token_type, value, span)
        if token_type == "INVALID":
            raise InvalidTokenException(program, token)
        tokens.append(token)
        pos = match.span()[1]

    if brace_count > 0:
        raise BraceNotEnoughException(program, (brace_start_pos, pos))
    return tokens

def pop_values(program: str, stack: list, types: tuple[type], token: Token):
    values = []

    if len(stack) < len(types):
        raise StackTooShortException(program, stack, len(types), token)
    
    peeks = stack[-len(types):]
    for type_ in types[::-1]:
        peek = peeks.pop()
        if not issubclass(type(peek), type_):
            raise WrongTypeException(program, stack, types, token)

    for type_ in types[::-1]:
        value = stack.pop()
        values.append(value)
            
    return values[::-1]

def run_command_token(program: str, stack: list, variables: dict, token: Token):
    command = token.content
    match command:
        case "print":
            value, = pop_values(program, stack, (object,), token)
            print(value, end="")
        case "printsp":
            value, = pop_values(program, stack, (object,), token)
            print(value, end=" ")
        case "println":
            value, = pop_values(program, stack, (object,), token)
            print(value)
        case "printstack":
            print(stack)
        case "+":
            v1, v2 = pop_values(program, stack, (float, float), token)
            stack.append(v1 + v2)
        case "-":
            v1, v2 = pop_values(program, stack, (float, float), token)
            stack.append(v1 - v2)
        case "*":
            v1, v2 = pop_values(program, stack, (float, float), token)
            stack.append(v1 * v2)
        case "/":
            v1, v2 = pop_values(program, stack, (float, float), token)
            if v2 == 0:
                raise ZeroDivisionException(program, token)
            stack.append(v1 / v2)
        case "%":
            v1, v2 = pop_values(program, stack, (float, float), token)
            if v2 == 0:
                raise ZeroDivisionException(program, token)
            stack.append(v1 % v2)
        case ">":
            v1, v2 = pop_values(program, stack, (float, float), token)
            stack.append(v1 > v2)
        case "<":
            v1, v2 = pop_values(program, stack, (float, float), token)
            stack.append(v1 < v2)
        case ">=":
            v1, v2 = pop_values(program, stack, (float, float), token)
            stack.append(v1 >= v2)
        case "<=":
            v1, v2 = pop_values(program, stack, (float, float), token)
            stack.append(v1 <= v2)
        case "==":
            v1, v2 = pop_values(program, stack, (object, object), token)
            stack.append(v1 == v2)
        case "!=":
            v1, v2 = pop_values(program, stack, (object, object), token)
            stack.append(v1 != v2)
        case "#":
            value, = pop_values(program, stack, (object,), token)
        case "concat":
            v1, v2 = pop_values(program, stack, (str, str), token)
            stack.append(v1 + v2)
        case "tonum":
            value, = pop_values(program, stack, (str,), token)
            try:
                stack.append(float(value))
            except ValueError:
                raise InvalidNumberException(program, value, token)
        case "tostr":
            value, = pop_values(program, stack, (object,), token)
            stack.append(str(value))
        case "input":
            stack.append(input())
        case "set":
            var, value = pop_values(program, stack, (Variable, object), token)
            variables[var.name] = value
        case "rset":
            value, var = pop_values(program, stack, (object, Variable), token)
            variables[var.name] = value
        case "get":
            var, = pop_values(program, stack, (Variable,), token)
            stack.append(variables[var.name])
        case "dup":
            value, = pop_values(program, stack, (object,), token)
            stack.append(value)
            stack.append(value)
        case "if":
            cond, prog = pop_values(program, stack, (bool, Program), token)
            if cond:
                try:
                    run(prog.program, prog.tokens, stack, variables)
                except Exception as e:
                    raise ErrorWhileRunningCodeException(program, token, e)
        case "unless":
            cond, prog = pop_values(program, stack, (bool, Program), token)
            if not cond:
                try:
                    run(prog.program, prog.tokens, stack, variables)
                except Exception as e:
                    raise ErrorWhileRunningCodeException(program, token, e)
        case "isundefined":
            value, = pop_values(program, stack, (object, ), token)
            stack.append(value is UNDEFINED)
        case "for":
            var, from_, to, step, prog = pop_values(program, stack, (Variable, float, float, float, Program), token)
            value = from_
            while value <= to:
                variables[var.name] = value
                try:
                    run(prog.program, prog.tokens, stack, variables)
                except Exception as e:
                    raise ErrorWhileRunningCodeException(program, token, e)
                value += step
        case "exec":
            prog, = pop_values(program, stack, (Program, ), token)
            try:
                run(prog.program, prog.tokens, stack, variables)
            except Exception as e:
                raise ErrorWhileRunningCodeException(program, token, e)
        case "emplist":
            stack.append([])
        case "seq":
            from_, to, step = pop_values(program, stack, (float, float, float), token)
            list_ = []
            value = from_
            while value <= to:
                list_.append(value)
                value += step
            stack.append(list_)
        case "put":
            list_, value = pop_values(program, stack, (list, object), token)
            stack.append(list_ + [value])
        case "foreach":
            var, list_, prog = pop_values(program, stack, (Variable, list, Program), token)
            for value in list_:
                variables[var.name] = value
                try:
                    run(prog.program, prog.tokens, stack, variables)
                except Exception as e:
                    raise ErrorWhileRunningCodeException(program, token, e)
        case "len":
            list_, = pop_values(program, stack, (list, ), token)
            stack.append(float(len(list_)))
        case "getat":
            list_, index = pop_values(program, stack, (list, float), token)
            if index < 0 or index % 1 != 0:
                raise IndexNotPositiveIntegerException(program, token, index)
            if index >= len(list_):
                raise IndexOutOfRangeException(program, token, len(list_), index)
            stack.append(list_[int(index)])
        case "setat":
            list_, index, value = pop_values(program, stack, (list, float, object), token)
            if index < 0 or index % 1 != 0:
                raise IndexNotPositiveIntegerException(program, token)
            if index >= len(list_):
                raise IndexOutOfRangeException(program, token, len(list_), index)
            new_list = list_[:]
            new_list[int(index)] = value
            stack.append(new_list)
        case "map":
            list_, prog = pop_values(program, stack, (list, Program), token)
            new_list = []
            for value in list_:
                try:
                    stack.append(value)
                    run(prog.program, prog.tokens, stack, variables)
                    new_value = pop_values(program, stack, (object, ), token)[0]
                    new_list.append(new_value)
                except Exception as e:
                    raise ErrorWhileRunningCodeException(program, token, e)
            stack.append(new_list)
        case "filter":
            list_, prog = pop_values(program, stack, (list, Program), token)
            new_list = []
            for value in list_:
                try:
                    stack.append(value)
                    run(prog.program, prog.tokens, stack, variables)
                    cond = pop_values(program, stack, (bool, ), token)[0]
                    if cond:
                        new_list.append(value)
                except Exception as e:
                    raise ErrorWhileRunningCodeException(program, token, e)
            stack.append(new_list)
        case "empdict":
            stack.append({})
        case "dicset":
            dict_, key, value = pop_values(program, stack, (dict, str, object), token)
            stack.append(dict_ | {key: value})
        case "dicget":
            dict_, key = pop_values(program, stack, (dict, str), token)
            if key not in dict_.keys():
                raise NoSuchKeyException(program, token, key)
            stack.append(dict_[key])
        case "keys":
            dict_, = pop_values(program, stack, (dict, ), token)
            stack.append([*dict_.keys()])
        case "values":
            dict_, = pop_values(program, stack, (dict, ), token)
            stack.append([*dict_.values()])
        case _:
            raise NoSuchCommandException(program, token)


def run(program: str, tokens: list[Token], stack: list = [], variables = defaultdict(lambda: UNDEFINED)):
    for token in tokens:
        value = token.content
        match token.token_type:
            case "NUMBER":
                stack.append(float(value))
            case "STRING":
                stack.append(value[1:-1])
            case "CODE":
                try:
                    program_of_code = value[1:-1]
                    tokens = tokenize(program_of_code)
                    stack.append(Program(program_of_code, tokens))
                except Exception as e:
                    raise InvalidProgramException(program, token, e)
            case "BOOLEAN":
                stack.append(value == "True")
            case "VARIABLE":
                stack.append(Variable(value[1:]))
            case "COMMAND":
                run_command_token(program, stack, variables, token)


def main():
    argv = sys.argv
    argc = len(argv)
    if argc != 2:
        print(f"Usage: python {__file__} ProgramName")
        return
    file_name = sys.argv[1]
    with open(file_name, "r", encoding="UTF-8") as f:
        program = f.read()
    tokens = tokenize(program)
    run(program, tokens)

if __name__ == "__main__":
    #main()
    try:
        main()
    except Exception as e:
        print(e)