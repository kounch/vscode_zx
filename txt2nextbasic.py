#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not change the previous lines. See PEP 8, PEP 263.
"""
Text to NextBASIC File Converter for ZX Spectrum Next (+3e/ESXDOS compatible)

    Copyright (c) 2020 @Kounch

    BASIC parser modified from original version in ZX Basic libraries
    https://zxbasic.readthedocs.io/en/latest/

    ZX Basic Copyleft (K) 2008, Jose Rodriguez-Rosa (a.k.a. Boriel)
    <http://www.boriel.com>

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
__MY_VERSION__ = '0.4'

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
            code += ['LOAD "{0}" CODE {1}'.format(arg_data['name'], s_addr)]
            code += ['30 RANDOMIZE USR {0}'.format(s_addr)]

        basic_data = Basic()
        for line in code:
            line = line.strip()
            arr_line = line.split()
            if line and line[
                    0] != '#':  #  Comments and directives aren't parsed
                arr_line = preproc(line)
                if arr_line:
                    n_line = None
                    # Detect line numbers
                    if arr_line[0].isdigit():
                        n_line = int(arr_line[0])
                        arr_line = arr_line[1:]
                    # Parse line
                    basic_data.add_line([arr_line], n_line)
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
        file_content = bytearray(basic_data.bytes)

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


def preproc(line):
    """Does some pre-processing on a BASIC line"""

    # Char conversion
    dict_char = {'£': '`', '©': '\x7f'}
    for s_char in dict_char:
        line = line.replace(s_char, dict_char[s_char])

    # Detect ; and REM comments
    comment = ''
    # Comments at start of line
    det_comm = re.compile('(\\s*\\d*\\s*(?:;|REM\\s?))(.*)')
    match_comm = det_comm.match(line)
    if match_comm:
        line = match_comm.group(1)
        comment = match_comm.group(2)
    else:
        # Comments after :
        det_comm = re.compile('(.*:\\s*(?:;|REM\\s?))(.*)')
        match_comm = det_comm.match(line)
        if match_comm:
            n_line = match_comm.group(1)
            if n_line.count('"') % 2 == 0:  # Not between quotes
                line = n_line
                comment = match_comm.group(2)

    # Detect if quoted
    b_quote = False

    new_line = ''
    for letter in line:
        if letter == '"':
            if b_quote:
                b_quote = False
            else:
                b_quote = True

            new_line += letter
            continue

        if b_quote:
            new_line += letter
            continue

        # Expand if it's a separator character and unquoted
        if letter in ";:,#+-*/=&|^><%!()'":
            new_line += ' {0} '.format(letter)
        else:
            new_line += letter

    # Convert to array of possible tokens
    try:
        lex = shlex.shlex(new_line, posix=False)
        lex.quotes = '"'
        lex.scapedquotes = '"'
        lex.whitespace_split = True
        lex.commenters = ''
        arr_line = list(lex)
    except:
        LOGGER.error(line)
        raise

    arr_result = []
    # Special cases: OPEN#, CLOSE#, >>, << ,<>, >=, <=, DEF FN, GO TO, GO SUB
    for word in arr_line:
        if word == '#' and len(arr_result) > 1:
            if arr_result[-1].upper() in ['OPEN', 'CLOSE']:
                arr_result[-1] = arr_result[-1] + word
                continue
        elif word in '><' and len(arr_result) > 1:
            if arr_result[-1] == word:
                arr_result[-1] = arr_result[-1] + word
                continue
            if word == '>' and arr_result[-1] == '<':
                arr_result[-1] = arr_result[-1] + word
                continue
        elif word == '=' and len(arr_result) > 1:
            if arr_result[-1] in '><':
                arr_result[-1] = arr_result[-1] + word
                continue
        elif word == 'FN' and len(arr_result) > 1:
            if arr_result[-1].upper() == 'DEF':
                arr_result[-1] = arr_result[-1] + ' {0}'.format(word)
                continue
        elif word in ['TO', 'SUB'] and len(arr_result) > 1:
            if arr_result[-1].upper() == 'GO':
                arr_result[-1] = arr_result[-1] + ' {0}'.format(word)
                continue

        arr_result.append(word)

    if comment:
        arr_result.append(comment)

    return arr_result


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
        # arr_bytes += (self.checksum).to_bytes(1, 'little')
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


class Basic(object):
    """ Class for a simple BASIC tokenizer

        Originally obtained from ZX Basic libraries
        https://zxbasic.readthedocs.io/en/latest/
    
        Copyleft (K) 2008, Jose Rodriguez-Rosa (a.k.a. Boriel)
        <http://www.boriel.com>
    """
    def __init__(self):
        self.bytes = [
        ]  # Array of bytes containing a ZX Spectrum BASIC program
        self.current_line = 0  # Current basic_line

    def line_number(self, number):
        """ Returns the bytes for a line number.
        This is BIG ENDIAN for the ZX Basic
        """
        numberH = (number & 0xFF00) >> 8
        numberL = number & 0xFF

        return [numberH, numberL]

    def numberLH(self, number):
        """ Returns the bytes for 16 bits number.
        This is LITTLE ENDIAN for the ZX Basic
        """
        numberH = (number & 0xFF00) >> 8
        numberL = number & 0xFF

        return [numberL, numberH]

    def convert(self, strnum):
        """ Detect if string it's a number and then the type (int or float),
        then try to convert using Sinclair BASIC 5-byte number format
        (http://fileformats.archiveteam.org/wiki/Sinclair_BASIC_tokenized_file#5-byte_numeric_format)
        """

        c = None

        det_int = re.compile('[+-]?[0-9]+$')
        match_int = det_int.match(strnum)
        if match_int:
            LOGGER.debug('int: {0}'.format(strnum))
            newint = int(strnum)
            c = self.convert_int(newint)

        det_float = re.compile('[+-]?([0-9]*)?[.][0-9]+$')
        match_float = det_float.match(strnum)
        if match_float:
            LOGGER.debug('float: {0}'.format(strnum))
            newfloat = float(strnum)
            c = self.convert_float(newfloat)

        if c:
            b = strnum.encode('utf-8')
            c = b''.join([b, b'\x0e', c])

        return c

    def convert_int(self, newint):
        """Convert int to bytes using 5-byte Sinclair format"""

        if newint < 65536 and newint > -65536:
            LOGGER.debug('int->{0}'.format(newint))
            if newint < 0:
                b = b'\x00\xff'
                newint += 65536
            else:
                b = b'\x00\x00'
            c = newint.to_bytes(2, byteorder='little', signed=False)
            b = b''.join([b, c, b'\x00'])
            return b
        else:
            return self.convert_float(float(newint))

    def convert_float(self, newfloat):
        """Convert float to bytes using 5-byte Sinclair format"""

        if newfloat != 0.0:
            LOGGER.debug('float->{0}'.format(newfloat))
            b_sign = '0'
            normalized = False
            if newfloat < 0.0:
                b_sign = '1'
                newfloat = abs(newfloat)

            intpart = int(newfloat)
            mantissa = '{0:b}'.format(intpart)
            if intpart == 0:
                mantissa = ''
            else:
                normalized = True
            newexp = len(mantissa)

            fractpart = newfloat - intpart
            i = 0
            fractbin = ''
            while i < 33:
                fractpart *= 2
                if int(fractpart) > 0:
                    if not normalized:
                        normalized = True
                        fractbin = fractbin[i:]
                        i = 0
                    fractpart -= int(fractpart)
                    fractbin += '1'
                else:
                    if not normalized:
                        newexp -= 1
                    fractbin += '0'
                i += 1

            fractint = int(fractbin, 2)
            if newexp < 0:
                fractint -= 1
            fractint = '{0:033b}'.format(fractint)

            mantissa += fractint
            mantissa = b_sign + mantissa[1:]

            b = '{0:08b}'.format(128 + newexp)
            b += mantissa
            if b[40] == '1':
                b = b[:39] + '1'
            b = int(b[:40], 2)
            b = b.to_bytes(5, byteorder='big', signed=False)

            return b
        else:
            return self.convert_int(0)

    def token(self, string):
        """ Return the token for the given word
        """
        string = string.upper()

        return [TOKENS[string]]

    def literal(self, string):
        """ Return the current string "as is"
        in bytes
        """
        return [ord(x) for x in string]

    def parse_sentence(self, string):
        """ Parses the given sentence. BASIC commands must be
        types UPPERCASE and as SEEN in ZX BASIC. e.g. GO SUB for gosub, etc...
        """

        result = []

        def shift(string_):
            """ Returns first word of a string, and remaining
            """
            string_ = string_.strip()  # Remove spaces and tabs

            if not string_:  # Avoid empty strings
                return '', ''

            i = string_.find(' ')
            if i == -1:
                command_ = string_
                string_ = ''
            else:
                command_ = string_[:i]
                string_ = string_[i:]

            return command_, string_

        command, string = shift(string)
        while command != '':
            result += self.token(command)

    def sentence_bytes(self, sentence):
        """ Return bytes of a sentence.
        This is a very simple parser. Sentence is a list of strings and numbers.
        1st element of sentence MUST match a token.
        """

        result = []
        for i in sentence:
            try:
                word = int(i)
            except:
                try:
                    word = float(i)
                except:
                    word = i

            if isinstance(word, str):
                if word.upper() in TOKENS:  # A token
                    result.extend([TOKENS[word.upper()]])
                elif word[0] == '.':  # Extended dot command
                    word = ' {0} '.format(word)
                    result.extend(self.literal(word))
                else:  # Plain text
                    result.extend(self.literal(word))
            elif isinstance(word, float) or isinstance(word, int):  # A number?
                result.extend(self.convert(i))
            else:
                result.extend(word)  # Another thing

        return result

    def line(self, sentences, line_number=None):
        """ Return the bytes for a basic line.
        If no line number is given, current one + 10 will be used
        Sentences if a list of sentences
        """
        if line_number is None:
            line_number = self.current_line + 10
        self.current_line = line_number

        sep = []
        result = []
        for sentence in sentences:
            result.extend(sep)
            result.extend(self.sentence_bytes(sentence))
            sep = [ord(':')]

        result.extend([ENTER])
        result = self.line_number(line_number) + self.numberLH(
            len(result)) + result

        return result

    def add_line(self, sentences, line_number=None):
        """ Add current line to the output.
        See self.line() for more info
        """
        self.bytes += self.line(sentences, line_number)


# Constants
# ---------

ENTER = 0x0D

TOKENS = {
    'PEEK$': 135,
    'REG': 136,
    'DPOKE': 137,
    'DPEEK': 138,
    'MOD': 139,
    '<<': 140,
    '>>': 141,
    'UNTIL': 142,
    'ERROR': 143,
    'ON': 144,
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
    'INKEY$': 166,
    'PI': 167,
    'FN': 168,
    'POINT': 169,
    'SCREEN$': 170,
    'ATTR': 171,
    'AT': 172,
    'TAB': 173,
    'VAL$': 174,
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
    'INT': 186,
    'SQR': 187,
    'SGN': 188,
    'ABS': 189,
    'PEEK': 190,
    'IN': 191,
    'USR': 192,
    'STR$': 193,
    'CHR$': 194,
    'NOT': 195,
    'BIN': 196,
    'OR': 197,
    'AND': 198,
    '<=': 199,
    '>=': 200,
    '<>': 201,
    'LINE': 202,
    'THEN': 203,
    'TO': 204,
    'STEP': 205,
    'DEF FN': 206,
    'CAT': 207,
    'FORMAT': 208,
    'MOVE': 209,
    'ERASE': 210,
    'OPEN#': 211,
    'CLOSE#': 212,
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
    'COPY': 255
}

if __name__ == '__main__':
    main()
