"""Mask Lean literal text/comments while retaining active interpolation code.

This is a lexical source view, not an elaborator or a kernel census. Offsets and
newlines are preserved; quoted identifiers remain available to declaration scans.
"""
import re

CHAR = re.compile(r"'(?:[^'\\\n]|\\(?:u\{[0-9a-fA-F]+\}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.))'")
RAW = re.compile(r'r(#+)?"')

INTERPOLATED = re.compile(r"[^\W\d][\w']*!\"")

def neutralize_lean_source(text: str) -> str:
    out = list(text)
    size = len(text)

    def mask(start, end):
        for k in range(start, end):
            if text[k] != '\n':
                out[k] = ' '

    def string(start, quote, interpolate=False):
        mask(start, quote + 1)
        i = quote + 1
        while i < size:
            if text[i] == '\\':
                mask(i, min(size, i + 2)); i += 2
            elif text[i] == '"':
                mask(i, i + 1)
                return i + 1
            elif interpolate and text.startswith('{{', i):
                mask(i, i + 2); i += 2
            elif interpolate and text.startswith('}}', i):
                mask(i, i + 2); i += 2
            elif interpolate and text[i] == '{':
                i = code(i + 1, True)
            else:
                mask(i, i + 1); i += 1
        raise ValueError('Unterminated Lean string; source coverage unavailable')

    def code(start, brace=False):
        i = start
        while i < size:
            if text.startswith('--', i):
                end = text.find('\n', i)
                end = size if end < 0 else end
                mask(i, end); i = end
            elif text.startswith('/-', i):
                begin = i; depth = 1; i += 2
                while i < size and depth:
                    if text.startswith('/-', i): depth += 1; i += 2
                    elif text.startswith('-/', i): depth -= 1; i += 2
                    else: i += 1
                if depth: raise ValueError('Unterminated Lean comment; source coverage unavailable')
                mask(begin, i)
            elif text[i] == '«':
                end = text.find('»', i + 1)
                if end < 0: raise ValueError('Unterminated Lean quoted identifier')
                i = end + 1
            elif text[i] == "'" and (i == 0 or not (text[i-1].isalnum() or text[i-1] in "_'»")):
                match = CHAR.match(text, i)
                if match: mask(i, match.end()); i = match.end()
                else: i += 1
            elif match := INTERPOLATED.match(text, i):
                i = string(i, match.end() - 1, True)
            elif text[i] == 'r' and (i == 0 or not (text[i-1].isalnum() or text[i-1] in "_'»")) and (match := RAW.match(text, i)):
                delimiter = '"' + (match.group(1) or '')
                end = text.find(delimiter, match.end())
                if end < 0: raise ValueError('Unterminated Lean raw string')
                end += len(delimiter); mask(i, end); i = end
            elif text[i] == '"':
                i = string(i, i)
            elif brace and text[i] == '{':
                i = code(i + 1, True)
            elif brace and text[i] == '}':
                return i + 1
            else:
                i += 1
        if brace: raise ValueError('Unterminated Lean interpolation')
        return i

    code(0)
    return ''.join(out)
