#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not change the previous lines. See PEP 8, PEP 263.
"""
Text to ZX Basic File Converter for ZX Spectrum Next (+3e/ESXDOS compatible)

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

try:
    from pathlib import Path
    Path().expanduser()
except (ImportError, AttributeError):
    from pathlib2 import Path

__MY_VERSION__ = '0.1'

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOG_FORMAT = logging.Formatter(
    '%(asctime)s [%(levelname)-5.5s] - %(name)s: %(message)s')
LOG_STREAM = logging.StreamHandler(sys.stdout)
LOG_STREAM.setFormatter(LOG_FORMAT)
LOGGER.addHandler(LOG_STREAM)


def main():
    """Main Routine"""

    arg_data = parse_args()

    load_addr = 0x8000
    if arg_data['is_binary']:
        with open(arg_data['input'], 'rb') as f:
            file_content = f.read()
    else:
        if arg_data['input_txt']:
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
            if line[0] != '#':  #  Comments and directives aren't parsed
                arr_line = preproc(line)
                if arr_line:
                    n_line = None
                    # Detect line numbers
                    if arr_line[0].isdigit():
                        n_line = int(arr_line[0])
                        arr_line = arr_line[1:]
                    # Parse line
                    basic_data.add_line([arr_line], n_line)
            elif '#program' in line:
                # Not implemented
                LOGGER.debug('Program Directive: {0}'.format(line))
            elif line == '#autostart':
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

    parser = argparse.ArgumentParser(description='ZX Binary Loader Maker')
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
            LOGGER.error('Path not found: %s', i_path)
            raise IOError('Input path does not exist!')
    else:
        if not b_name:
            LOGGER.error('A binary name is required!')
            raise ValueError('No name!')

    values['name'] = b_name
    values['input'] = i_path
    values['output'] = o_path
    values['start_addr'] = s_addr
    values['is_binary'] = is_binary

    return values


def preproc(line):
    """Does some pre-processing on a BASIC line"""

    new_line = ''

    # Detect if quoted
    b_quote = False
    for letter in line:
        if letter == '""':
            if b_quote:
                b_quote = False
            else:
                b_quote = True

            new_line += letter
            next

        if b_quote:
            new_line += letter
            next

        # Expand if a separator character and not quoted
        if letter in ';:,#':
            new_line += ' {0} '.format(letter)
        else:
            new_line += letter

    # Convert to array of possible tokens
    arr_line = shlex.split(new_line, posix=False)

    arr_result = []
    # Special cases: OPEN# and CLOSE#
    for word in arr_line:
        if word == '#' and len(arr_result) > 1:
            if arr_result[-1].upper() in ['OPEN', 'CLOSE']:
                arr_result[-1] = arr_result[-1] + word
            else:
                arr_result.append(word)
        else:
            arr_result.append(word)

    return arr_result


def fp(x):
    """ Returns a floating point number as EXP+128, Mantissa

        Obtained from ZX Basic libraries
        https://zxbasic.readthedocs.io/en/latest/
    
        Copyleft (K) 2008, Jose Rodriguez-Rosa (a.k.a. Boriel)
        <http://www.boriel.com>
    """
    def bin32(f):
        """ Returns ASCII representation for a 32 bit integer value
        """
        result = ''
        a = int(f) & 0xFFFFFFFF  # ensures int 32

        for _ in range(32):
            result = str(a % 2) + result
            a = a >> 1

        return result

    def bindec32(f):
        """ Returns binary representation of a mantissa x (x is float)
        """
        result = '0'
        a = f

        if f >= 1:
            result = bin32(f)

        result += '.'
        c = int(a)

        for _ in range(32):
            a -= c
            a *= 2
            c = int(a)
            result += str(c)

        return result

    e = 0  # exponent
    s = 1 if x < 0 else 0  # sign
    m = abs(x)  # mantissa

    while m >= 1:
        m /= 2.0
        e += 1

    while 0 < m < 0.5:
        m *= 2.0
        e -= 1

    M = bindec32(m)[3:]
    M = str(s) + M
    E = bin32(e + 128)[-8:] if x != 0 else bin32(0)[-8:]

    return M, E


def immediate_float(x):
    """
     Returns C DE HL as values for loading
    and immediate floating point.

    Obtained from ZX Basic libraries
    https://zxbasic.readthedocs.io/en/latest/

    Copyleft (K) 2008, Jose Rodriguez-Rosa (a.k.a. Boriel)
    <http://www.boriel.com>
    """
    def bin2hex(y):
        return "%02X" % int(y, 2)

    M, E = fp(x)

    C = '0' + bin2hex(E) + 'h'
    ED = '0' + bin2hex(M[8:16]) + bin2hex(M[:8]) + 'h'
    LH = '0' + bin2hex(M[24:]) + bin2hex(M[16:24]) + 'h'

    return C, ED, LH


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

    def number(self, number):
        """ Returns a floating point (or integer) number for a BASIC
        program. That is: It's ASCII representation followed by 5 bytes
        in floating point or integer format (if number in (-65535 + 65535)
        """
        s = [ord(x) for x in str(number)
             ] + [14]  # Bytes of string representation in bytes

        if number == int(number) and abs(number) < 65536:  # integer form?
            sign = 0xFF if number < 0 else 0
            b = [0, sign] + self.numberLH(number) + [0]
        else:  # Float form
            (C, ED, LH) = immediate_float(number)
            C = C[:2]  # Remove 'h'
            ED = ED[:4]  # Remove 'h'
            LH = LH[:4]  # Remove 'h'

            b = [int(C, 16)]  # Convert to BASE 10
            b += [int(ED[:2], 16), int(ED[2:], 16)]
            b += [int(LH[:2], 16), int(LH[2:], 16)]

        return s + b

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
        if sentence[0][0] == '.':
            # Extended dot command
            word = ' {0}'.format(' '.join(sentence))
            result.extend(self.literal(word))
        else:
            for i in sentence:
                LOGGER.debug('word: {0}'.format(i))
                try:
                    word = int(i)
                except:
                    try:
                        word = float(i)
                    except:
                        word = i

                if isinstance(word, str):
                    if word.upper() in TOKENS:
                        result.extend([TOKENS[word.upper()]])
                    else:
                        result.extend(self.literal(word))
                elif isinstance(word, float) or isinstance(word,
                                                           int):  # A number?
                    result.extend(self.number(word))
                else:
                    result.extend(word)  # Must be another thing

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
    'GOTO': 236,
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
