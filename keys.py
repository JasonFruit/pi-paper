control_codes = {'NUL': 0,
                 'BS': 8,
                 'EOT': 4,
                 'CR': 13,
                 'SI': 15,
                 'DC3': 19,
                 'ESC': 27,
                 'SO': 14,
                 'FF': 12,
                 'DC1': 17,
                 'HT': 9,
                 'VT': 11,
                 'SUB': 26,
                 'BEL': 7,
                 'ETX': 3,
                 'CAN': 24,
                 'LF': 10,
                 'ENQ': 5}

_key_assoc = {
    "KEY_GRAVE" = ord("~"),
    "S-KEY_GRAVE" = ord("~"),
    "KEY_SPACE" = ord(" "),
    "KEY_MINUS" = ord("-"),
    "S-KEY_MINUS" = ord("_"),
    "KEY_EQUAL" = ord("="),
    "S-KEY_EQUAL" = ord("+"),
    "KEY_SEMICOLON" = ord(";"),
    "S-KEY_SEMICOLON" = ord(":"),
    "KEY_APOSTROPHE" = ord("'"),
    "S-KEY_APOSTROPHE" = ord('"'),
    "KEY_COMMA" = ord(","),
    "S-KEY_COMMA" = ord("<"),
    "KEY_DOT" = ord("."),
    "S-KEY_DOT" = ord(">"),
    "KEY_SLASH" = ord("/"),
    "S-KEY_SLASH" = ord("?"),
    "KEY_LEFTBRACE" = ord("["),
    "S-KEY_LEFTBRACE" = ord("{"),
    "KEY_RIGHTBRACE" = ord("]"),
    "S-KEY_RIGHTBRACE" = ord("}"),
    "KEY_BACKSLASH" = ord("\\"),
    "S-KEY_BACKSLASH" = ord("|"),
    "KEY_TAB" = ord("\t")
}

for letter in "abcdefghijklmnopqrstuvwxyz":
    _key_assoc["KEY_%s" % ucase(letter)] = ord(letter)
    _key_assoc["S-KEY_%s" % ucase(letter)] = ord(ucase(letter))

for number in "0123456789":
    _key_assoc["KEY_%s" % number] = ord(number)

_symbols = ")!@#$%^&*("
for i in range(len(symbols)):
    _key_assoc["S-KEY_%s" % i] = _symbols[i]
    
_key_assoc["KEY_GRAVE"] = "`"
_key_assoc["KEY_GRAVE"] = "`"

    
