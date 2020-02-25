#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not change the previous lines. See PEP 8, PEP 263.
"""
Text to NextBASIC File Converter for ZX Spectrum Next (+3e/ESXDOS compatible)
    Copyright (c) 2020 @Kounch

    File Structure and Headers obtained from
    http://www.worldofspectrum.org/ZXSpectrum128+3Manual/chapter8pt27.html

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import os
import argparse
import logging
import shlex
import re
import gettext

try:
    from pathlib import Path
except (ImportError, AttributeError):
    from pathlib2 import Path

__MY_NAME__ = 'txt2nextbasic.py'
__MY_VERSION__ = '1.0'

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOG_FORMAT = logging.Formatter(
    '%(asctime)s [%(levelname)-5.5s] - %(name)s: %(message)s')
LOG_STREAM = logging.StreamHandler(sys.stdout)
LOG_STREAM.setFormatter(LOG_FORMAT)
LOGGER.addHandler(LOG_STREAM)

path_locale = os.path.dirname(__file__)
path_locale = os.path.join(path_locale, 'locale')
gettext.bindtextdomain(__MY_NAME__, localedir=path_locale)
gettext.textdomain(__MY_NAME__)
_ = gettext.gettext


def main():
    """Main Routine"""

    #Check Python version
    arr_v = sys.version_info
    if arr_v[0] < 3 or (arr_v[0] == 3 and arr_v[1] < 6):
        str_msg = _('You need version 3.6 or later of Python')
        LOGGER.error(str_msg)
        raise RuntimeError(str_msg)

    arg_data = parse_args()

    load_addr = 0x8000
    if arg_data['is_binary']:
        with open(arg_data['input'], 'rb') as f:
            file_content = f.read()
    else:
        if arg_data['input']:
            with open(arg_data['input'], 'r') as f:
                code = f.readlines()
        else:
            s_addr = arg_data['start_addr']
            code = ['#autostart']
            code += ['10 CLEAR {0}'.format(s_addr - 1)]
            code += ['20 LOAD "{0}" CODE {1}'.format(arg_data['name'], s_addr)]
            code += ['30 RANDOMIZE USR {0}'.format(s_addr)]

        basic_data = []
        for line in code:
            line = line.strip()
            arr_line = line.split(' ', -1)
            if line:
                # Comments and directives aren't parsed
                if line[0] != '#':
                    arr_line = proc_basic(line)
                    if arr_line:
                        basic_data.append(arr_line)  # Parse BASIC
                elif line.startswith('#program'):
                    if not arg_data['output']:
                        if len(arr_line) > 1:
                            arg_data['output'] = arg_data['input'].with_name(
                                arr_line[1] + '.bas')
                elif line.startswith('#autostart'):
                    if len(arr_line) > 1:
                        load_addr = int(arr_line[1])
                    else:
                        load_addr = 0
                else:
                    str_msg = _('Cannot parse line: {0}')
                    LOGGER.error(str_msg.format(line))
                    raise RuntimeError(str_msg.format(line))

        file_content = b''.join(basic_data)

    # Save bytes to file
    file_obj = Plus3DosFile(0, file_content, load_addr)
    with open(arg_data['output'], 'wb') as f:
        f.write(file_obj.make_bin())


# Functions
# ---------


def parse_args():
    """Command Line Parser"""

    parser = argparse.ArgumentParser(description='Text to NextBASIC Converter')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s {}'.format(__MY_VERSION__))
    parser.add_argument('-n',
                        '--name',
                        action='store',
                        dest='name',
                        help='Destination Binary File Name')
    parser.add_argument('-o',
                        '--output',
                        action='store',
                        dest='output_path',
                        help='Output path')
    parser.add_argument('-s',
                        '--start',
                        action='store',
                        dest='start_addr',
                        help='Machine Code Start Address')
    parser.add_argument('-i',
                        '--input',
                        required=False,
                        action='store',
                        dest='input_path',
                        help='Input text file with BASIC code')
    parser.add_argument('-b',
                        '--binary',
                        action='store_true',
                        dest='is_binary',
                        help='Input file is binary BASIC data')

    arguments = parser.parse_args()

    values = {}

    b_name = None
    if arguments.name:
        b_name = arguments.name

    i_path = None
    if arguments.input_path:
        i_path = Path(arguments.input_path)

    o_path = None
    if arguments.output_path:
        o_path = Path(arguments.output_path)

    s_addr = 32768
    if arguments.start_addr:
        s_addr = int(arguments.start_addr)

    is_binary = False
    if arguments.is_binary:
        is_binary = True

    if i_path:
        if not i_path.exists():
            str_msg = _('Path not found: {0}')
            LOGGER.error(str_msg.format(i_path))
            str_msg = _('Input path does not exist!')
            raise IOError(str_msg)
    else:
        if not b_name:
            str_msg = _('A binary name is required!')
            LOGGER.error(str_msg)
            str_msg = _('No name!')
            raise ValueError(str_msg)

    values['name'] = b_name
    values['input'] = i_path
    values['output'] = o_path
    values['start_addr'] = s_addr
    values['is_binary'] = is_binary

    return values


def proc_basic(line):
    """
       Does processing on a BASIC line, replacing text tokens, params, numbers,
       etc. with Sinclair ASCII characters. It also extracts line number apart.
       Data is returned as bytes.
    """

    line_number, line = extract_linenumber(line)  # Line number as int
    line = convert_char(line)  # Replace all known UTF-9 characters
    line, comment = extract_comment(line)  # REM comments won't be parsed
    arr_statements = extract_statements(line)  # Split quoted strings and ':'

    line_bin = ''
    for str_sttmnt in arr_statements:
        if str_sttmnt:
            if str_sttmnt[0] != '"' and str_sttmnt.strip()[0] != '.':
                str_sttmnt = process_tokens(str_sttmnt)
                str_sttmnt = process_params(str_sttmnt)
                str_sttmnt = process_numbers(str_sttmnt)
        line_bin += str_sttmnt
    line_bin += comment + '\x0d'
    line_bin = [ord(c) for c in line_bin]
    line_bin = bytes(line_bin)

    line_number = line_number.to_bytes(2, byteorder='big')
    line_len = len(line_bin)
    line_len = line_len.to_bytes(2, byteorder='little')
    line_bin = b''.join([line_number, line_len, line_bin])

    return line_bin


def extract_linenumber(line):
    """Splits line into line number and line"""

    det_line = re.compile('\\s*([0-9]+)\\s*(.*)')
    match_det = det_line.match(line)
    if match_det:
        line_number = match_det.group(1)
        line = match_det.group(2)

    return int(line_number), line


def convert_char(line):
    """Converts non-ASCII characters from UTF-8 to Sinclair ASCII"""

    # UTF Char conversion (Block Graphics, etc)
    for s_char in CHARS:
        line = line.replace(s_char, CHARS[s_char])

    # Escape characters conversion
    n_line = ''
    arr_line = line.split('`')  # Split using escape ` char
    if arr_line:
        n_line = arr_line[0]
        for p_line in arr_line[1:]:
            str_i = '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'  # Integer between 0 and 255
            str_x = '(x[0-9a-fA-F]{1,2})'  # Hex between 0 and FF
            det_esc = re.compile('({0}|{1})(.*)'.format(str_i, str_x))
            match_esc = det_esc.findall(p_line)
            if match_esc:
                match_esc = match_esc[0]
                n_char = match_esc[1]
                if match_esc[2]:
                    n_char = match_esc[2].replace(u'x', u'0x')
                n_line += chr(int(n_char, 0))
                n_line += match_esc[3]
            else:
                n_line += p_line
    line = n_line
    return line


def extract_comment(line):
    """Splits line into line and ;/REM comment strings"""

    # Detect ; and REM comments
    comment = ''
    det_comm = re.compile('(\\s*\\d*\\s*(?:;|REM\\s?))(.*)', re.MULTILINE
                          | re.DOTALL)  # Comments at start of line
    match_comm = det_comm.match(line)
    if match_comm:
        line = match_comm.group(1)
        comment = match_comm.group(2)
    else:
        det_comm = re.compile('(.*:\\s*(?:;|REM\\s?))(.*)',
                              re.MULTILINE | re.DOTALL)  # Comments after :
        match_comm = det_comm.match(line)
        if match_comm:
            n_line = match_comm.group(1)
            if n_line.count(u'"') % 2 == 0:  # Not between quotes
                line = n_line
                comment = match_comm.group(2)

    return line, comment


def extract_statements(line):
    """Converts line to array with quoted elements and statements as members"""

    arr_line = []
    # Split quoted elements
    b_quote = False
    elem_line = u''
    for letter in line:
        if letter == u'"':
            if b_quote:
                b_quote = False
                elem_line += letter
                arr_line.append(elem_line)  # End quote: Append to list
                elem_line = u''
                continue
            else:
                arr_line.append(elem_line)  # Start quote. Split and append
                elem_line = u''
                b_quote = True

        elem_line += letter
    if elem_line:
        arr_line.append(elem_line)  # Add ending string if not empty

    # Split statements using ':'
    arr_statements = []
    for elem_line in arr_line:
        if elem_line:
            if elem_line[0] == u'"':
                arr_statements.append(elem_line)  # Quoted strings kept as is
            else:
                i = prev_i = 0
                for str_char in elem_line:
                    if str_char == u':':
                        arr_statements.append(
                            elem_line[prev_i:i])  # Split on :
                        prev_i = i
                    i += 1
                if prev_i < i:
                    arr_statements.append(
                        elem_line[prev_i:i])  # Last statement

    return arr_statements


def process_tokens(str_statement):
    """ Converts token strings to Sinclair ASCII"""

    for token in TOKENS:
        chr_token = chr(TOKENS[token])  # Dictionaries are ordereded since 3.6
        det_t = re.compile('(\\s*{0}\\s*)'.format(token))
        find_t = det_t.findall(str_statement)
        if find_t:
            for str_token in find_t:
                str_statement = str_statement.replace(str_token, chr_token)

    return str_statement


def process_params(str_statement):
    """
        Parses statement and expands parameters to 5-byte format.
        Statement MUST have tokens converted to Sinclair ASCII
        (e.g. 0xCE instead of DEF FN)
    """

    # Detect DEF FN parameters
    det_params = re.compile('(.*\xCE[^\\(]*\\()([^\\)]*)(\\).*)')
    match_det = det_params.match(str_statement)
    if match_det:
        str_statement = match_det.group(1)
        str_params = match_det.group(2)
        if str_params:
            arr_params = str_params.split(',')
            arr_line = []
            for param in arr_params:
                param = param.strip()
                # Analyzing basic programs, looks like DEF FN parameters are
                # identified like numbers (using 0x0E as marker) and then
                # filled with arbitrary data on definition, and dynamically
                # replaced with other data on runtime, so we take an easy
                # approach, and use dashes to fill the space
                arr_line.append('{0}\x0e-----'.format(param))
            str_params = ','.join(arr_line)
        str_statement += str_params
        str_statement += match_det.group(3)

    return str_statement


def process_numbers(str_statement):
    """Parses statement and expands numbers to 5-byte format"""

    is_number = False
    is_intexpr = False  # Integer in int expression (NextBASIC)
    arr_numbers = []
    chr_prev = ''
    n_prev = 0
    i = 0
    # Compose a list of all possible numbers in statement, split accordingly
    for str_char in str_statement:
        if str_char in '0123456789.e+-' and not is_intexpr:
            if not is_number:
                if str_char != 'e':
                    is_number = True
                    n_pos = i
                    if i:
                        chr_prev = str_statement[i - 1]
            else:
                if str_char in '+-' and str_statement[i-1] not in 'e ':
                    is_number = False
    
        else:
            if str_char in '%@$\x8b':  # Int expression or MOD
                is_intexpr = True
            elif str_char in ',=' or ord(str_char) > 164:
                is_intexpr = False
            if is_number:
                is_number = False
                str_number = str_statement[n_pos:i]
                arr_numbers.append(
                    # Number as string, position, previous char and previous
                    # part of statement
                    [str_number, n_pos, chr_prev, str_statement[n_prev:n_pos]])
                n_prev = i
        i += 1

    if is_number:
        # We still have one remaining number to process
        str_number = str_statement[n_pos:i]
        arr_numbers.append(
            [str_number, n_pos, chr_prev, str_statement[n_prev:n_pos]])
        n_prev = i

    # Save remaining text of statement (without numbers inside)
    str_post = str_statement[n_prev:i]

    # Read list of numbers and compose the expanded statement
    str_result = ''
    for str_num, n_pos, chr_prev, str_prev in arr_numbers:
        bin_num = str_num  # By default, the number is not expanded
        str_result += str_prev  # Append text prepending number

        if chr_prev == '\xc4':  # BIN number
            LOGGER.debug('bin: {0}'.format(str_num))
            det_bin = re.compile('^[01]{8}$')
            match_det = det_bin.match(str_num)
            if match_det:
                int_num = int(str_num, base=2)  # Binary text to int
                bin_num = u'{0}\x0e'.format(
                    str_num)  # Sinclair BASIC number marker
                # Looks like BIN nubers are saved using one byte surrounded by 0s
                bin_num += u'\x00\x00{0}\x00\x00'.format(chr(int_num))
        else:  # Other kind of number
            LOGGER.debug('Number: {0}'.format(str_num))
            if str_num != '.':  # Only valid floats allowed
                bin_num = convert_number(str_num)  # Expand int or float
                bin_num = '{0}\x0e{1}'.format(str_num, bin_num)

        str_result += bin_num

    str_result += str_post  # Recover remaining text of statement

    return str_result


def convert_number(strnum):
    """ Detect if string it's a number and then the type (int, float),
    then try to convert using Sinclair BASIC 5-byte number format
    (http://fileformats.archiveteam.org/wiki/Sinclair_BASIC_tokenized_file#5-byte_numeric_format)
    """

    c = None
    # Integer
    det_int = re.compile('[+-]?[0-9]+$')
    match_int = det_int.match(strnum)
    if match_int:
        LOGGER.debug('int: {0}'.format(strnum))
        newint = int(strnum)
        c = convert_int(newint)

    # Float
    try:
        newfloat = float(strnum)
        LOGGER.debug('float: {0}'.format(strnum))
        c = convert_float(newfloat)
    except ValueError:
        pass

    # Convert binary to string
    s = ''
    if c:
        for b_char in c:
            s += chr(b_char)

    return s


def convert_int(newint):
    """Convert int to bytes using 5-byte Sinclair format"""

    if newint < 65536 and newint > -65536:
        LOGGER.debug('int->{0}'.format(newint))
        if newint < 0:  # Negative, so two's complement is needed
            b = b'\x00\xff'
            newint += 65536
        else:
            b = b'\x00\x00'

        c = newint.to_bytes(2, byteorder='little', signed=False)

        # To bytes
        b = b''.join([b, c, b'\x00'])

        return b
    else:
        # Out of range, must be treated as float
        return convert_float(float(newint))


def convert_float(newfloat):
    """Convert float to bytes using 5-byte Sinclair format"""

    if newfloat != 0.0:
        LOGGER.debug('float->{0}'.format(newfloat))

        # Extract sign and absolute value
        b_sign = '0'
        normalized = False
        if newfloat < 0.0:
            b_sign = '1'
            newfloat = abs(newfloat)

        # Process integer part
        intpart = int(newfloat)
        mantissa = '{0:b}'.format(intpart)
        if intpart == 0:
            mantissa = ''
        else:
            normalized = True

        # Base exponent, possibly not normalized yet
        newexp = len(mantissa)

        # Process fractional part
        fractpart = newfloat - intpart
        i = 0  # Bit counter
        fractbin = ''
        # Bit by bit, one extra bit for rounding reasons
        while i < 33:
            fractpart *= 2
            if int(fractpart) > 0:
                if not normalized:
                    normalized = True
                    fractbin = fractbin[i:]
                    i = 0  # Normalizing, so more bits are needed
                fractpart -= int(fractpart)
                fractbin += '1'
            else:
                if not normalized:
                    newexp -= 1  # Normalizing
                fractbin += '0'
            i += 1
        fractint = int(fractbin, 2)  # Convert binary string to int

        if newexp < 0:  # Negative exponent, adjust fractional part
            fractint -= 1

        fractint = '{0:033b}'.format(fractint)  # To string again

        # Compose mantisa
        mantissa += fractint
        mantissa = b_sign + mantissa[1:]

        # Format exponent
        b = '{0:08b}'.format(128 + newexp)  #To string

        b += mantissa  # Final bits

        # Rounding using bit #41
        if b[40] == '1':
            b = b[:39] + '1'
        b = int(b[:40], 2)

        # To bytes
        b = b.to_bytes(5, byteorder='big', signed=False)

        return b
    else:
        # 0 is always treated as int
        return convert_int(0)


#Classes
#-------
class Plus3DosFile(object):
    """+3DOS File Object"""
    def __init__(self, filetype=0, content=None, load_addr=0x8000):
        self.issue = 1
        self.version = 0
        self.filetype = filetype
        self.load_addr = load_addr
        self.set_content(content)

    def set_content(self, content=None):
        self.content = content
        content_length = 0
        if content:
            content_length = len(content)

        self.header = Plus3DosFileHeader(self.filetype, content_length,
                                         self.load_addr)

        self.length = 128 + content_length

    def make_bin(self):
        arr_bytes = b'PLUS3DOS'  # +3DOS signature - 'PLUS3DOS'
        arr_bytes += b'\x1A'  # 1Ah (26) Soft-EOF (end of file)
        arr_bytes += (self.issue).to_bytes(1, 'little')
        arr_bytes += (self.version).to_bytes(1, 'little')
        arr_bytes += (self.length).to_bytes(4, 'little')
        arr_bytes += self.header.make_bin()
        arr_bytes += b'\0' * 104  # Reserved (set to 0)
        checksum = 0
        for i in range(0, 126):
            checksum += arr_bytes[i]
        checksum %= 256
        arr_bytes += (checksum).to_bytes(1, 'little')
        arr_bytes += self.content

        return arr_bytes


class Plus3DosFileHeader(object):
    """+3DOS File Header Object
    
      504C5553 33444F53  Bytes 0...7  - +3DOS signature - 'PLUS3DOS'
      1A                 Byte 8       - 1Ah (26) Soft-EOF (end of file)
      01                 Byte 9       - Issue number
      00                 Byte 10      - Version number
      C7000000           Bytes 11...14    - Length of the file in bytes, 32 bit number,
                                            least significant byte in lowest address
      0047000A 00470000  Bytes 15...22    - +3 BASIC header data
      Program  -  0  - file length - 8000h or LINE    offset to prog -  (not used)
                 00    4700          0A00             4700              00
      000000 (...) 0000  Bytes 23...126   - Reserved (set to 0)
      D7                 Byte 127 - Checksum (sum of bytes 0...126 modulo 256)
      (BASIC Program)
        Notes for a file named: "nnnnnnnnn.bin":
        504C5553 33444F53 1A0100           -> Bytes 0...10
        187 + n bytes (file)               -> Bytes 11...14 least significant byte in lowest address
        00                                 -> Byte  15
        59  + n bytes (prog)               -> Bytes 16,17 least significant byte in lowest address
        0A00                               -> Bytes 18,19
        59  + n bytes (prog)               -> Bytes 20,21
        00..00                             -> Bytes 22..126
        Checksum  179 + (3 x n) % mod(256) -> Byte  127
        000A0D00 FD333237 36370E00         -> Bytes 128..139
        00FF7F00 0D001415 00EF22           -> Bytes 140..150
        "Filename.bin"                     -> Bytes 151..(151+n+3)
        22AF3332 3736380E 00000080         -> Bytes (151+n+4)..EOF
        000D001E 0E00F9C0 33323736
        380E0000 0080000D
    """
    def __init__(self, filetype=0, length=0, load_addr=0x8000):
        self.filetype = filetype
        self.load_addr = load_addr
        self.set_length(length)

    def set_length(self, length=0):
        self.length = length
        self.offset = length

    def make_bin(self):
        arr_bytes = (self.filetype).to_bytes(1, 'little')
        arr_bytes += (self.length).to_bytes(2, 'little')
        arr_bytes += (self.load_addr).to_bytes(2, 'little')
        arr_bytes += (self.offset).to_bytes(2, 'little')
        arr_bytes += b'\x00'
        return arr_bytes


# Constants
# ---------

TOKENS = {
    'PEEK\\$': 135,
    'REG': 136,
    'DPOKE': 137,
    'DPEEK': 138,
    'MOD': 139,
    '<<': 140,
    '>>': 141,
    'UNTIL': 142,
    'ERROR': 143,
    'DEFPROC': 145,
    'ENDPROC': 146,
    'PROC': 147,
    'LOCAL': 148,
    'DRIVER': 149,
    'WHILE': 150,
    'REPEAT': 151,
    'ELSE': 152,
    'REMOUNT': 153,
    'BANK': 154,
    'TILE': 155,
    'LAYER': 156,
    'PALETTE': 157,
    'SPRITE': 158,
    'PWD': 159,
    'CD': 160,
    'MKDIR': 161,
    'RMDIR': 162,
    'SPECTRUM': 163,
    'PLAY': 164,
    'RND': 165,
    'INKEY\\$': 166,
    'PI': 167,
    'POINT': 169,
    'SCREEN\\$': 170,
    'ATTR': 171,
    'TAB': 173,
    'VAL\\$': 174,
    'CODE': 175,
    'VAL': 176,
    'LEN': 177,
    'SIN': 178,
    'COS': 179,
    'TAN': 180,
    'ASN': 181,
    'ACS': 182,
    'ATN': 183,
    'LN': 184,
    'EXP': 185,
    'SQR': 187,
    'SGN': 188,
    'ABS': 189,
    'PEEK': 190,
    'USR': 192,
    'STR\\$': 193,
    'CHR\\$': 194,
    'NOT': 195,
    'BIN': 196,
    '<=': 199,
    '>=': 200,
    '<>': 201,
    'LINE': 202,
    'THEN': 203,
    'STEP': 205,
    'DEF FN': 206,
    'CAT': 207,
    'FORMAT': 208,
    'MOVE': 209,
    'ERASE': 210,
    'OPEN #': 211,
    'CLOSE #': 212,
    'MERGE': 213,
    'VERIFY': 214,
    'BEEP': 215,
    'CIRCLE': 216,
    'INK': 217,
    'PAPER': 218,
    'FLASH': 219,
    'BRIGHT': 220,
    'INVERSE': 221,
    'OVER': 222,
    'OUT': 223,
    'LPRINT': 224,
    'LLIST': 225,
    'STOP': 226,
    'READ': 227,
    'DATA': 228,
    'RESTORE': 229,
    'NEW': 230,
    'BORDER': 231,
    'CONTINUE': 232,
    'DIM': 233,
    'REM': 234,
    'FOR': 235,
    'GO TO': 236,
    'GO SUB': 237,
    'INPUT': 238,
    'LOAD': 239,
    'LIST': 240,
    'LET': 241,
    'PAUSE': 242,
    'NEXT': 243,
    'POKE': 244,
    'PRINT': 245,
    'PLOT': 246,
    'RUN': 247,
    'SAVE': 248,
    'RANDOMIZE': 249,
    'IF': 250,
    'CLS': 251,
    'DRAW': 252,
    'CLEAR': 253,
    'RETURN': 254,
    'COPY': 255,
    'ON': 144,
    'FN': 168,
    'AT': 172,
    'INT': 186,
    'IN': 191,
    'OR': 197,
    'AND': 198,
    'TO': 204
}

CHARS = {
    '£': '`',
    '©': '\x7f',
    '\u259D': '\x81',  # Quadrant upper right
    '\u2598': '\x82',  # Quadrant upper left
    '\u2580': '\x83',  # Upper half block
    '\u2597': '\x84',  # Quadrant lower right
    '\u2590': '\x85',  # Right half block
    '\u259A': '\x86',  # Quadrant upper left and lower right
    '\u259C': '\x87',  # Quadrant upper left and upper right and lower right
    '\u2596': '\x88',  # Quadrant lower left
    '\u259E': '\x89',  # Quadrant upper right and lower left
    '\u258C': '\x8a',  # Left half block
    '\u259B': '\x8b',  # Quadrant upper left and upper right and lower left
    '\u2584': '\x8c',  # Lower half block
    '\u259F': '\x8d',  # Quadrant upper right and lower left and lower right
    '\u2599': '\x8e',  # Quadrant upper left and lower left and lower right
    '\u2588': '\x8f'  # Full block
}

if __name__ == '__main__':
    main()
