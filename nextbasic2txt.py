#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not change the previous lines. See PEP 8, PEP 263.
"""
    NextBASIC to Text File Converter for ZX Spectrum Next
    Copyright (c) 2020-2022 @Kounch

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
import gettext

if sys.version_info > (3, 5):
    from pathlib import Path
else:
    from pathlib2 import Path

__MY_NAME__ = 'nextbasic2txt.py'
__MY_VERSION__ = '1.1.2'

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

    # Check Python version
    arr_v = sys.version_info
    if arr_v[0] < 3 or (arr_v[0] == 3 and arr_v[1] < 6):
        str_msg = _('You need version 3.6 or later of Python')
        LOGGER.error(str_msg)
        raise RuntimeError(str_msg)

    arg_data = parse_args()

    if arg_data['input']:
        with open(arg_data['input'], 'rb') as f:
            bindata = f.read()

    arr_str = []
    if arg_data['name']:
        arr_str.append('#program {0}\r\n'.format(arg_data['name']))

    arr_result = []
    if len(bindata) > 128 and bindata[:8] == b'PLUS3DOS' and bindata[
            15:16] == b'\x00':
        i_len = int.from_bytes(bindata[11:15], 'little')

        i_saddr = int.from_bytes(bindata[18:20], 'little')
        if i_saddr < 10000:
            s_addr = '#autostart'
            if i_saddr > 0:
                s_addr += ' {0}'.format(i_saddr)
            arr_str.append(s_addr + '\r\n')

        arr_bin = bindata[128:]  # Remove header
        arr_str += procbin(arr_bin, i_len)
    else:
        str_msg = _('Not a valid file')
        LOGGER.error(str_msg)
        raise RuntimeError(str_msg)

    if arr_str:
        with open(arg_data['output'], 'w') as f:
            f.writelines(arr_str)


# Functions
# ---------


def parse_args():
    """Command Line Parser"""

    parser = argparse.ArgumentParser(description='NextBASIC to Text Converter')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s {}'.format(__MY_VERSION__))
    parser.add_argument('-o',
                        '--output',
                        action='store',
                        dest='output_path',
                        help='Output path')
    parser.add_argument('-i',
                        '--input',
                        required=True,
                        action='store',
                        dest='input_path',
                        help='Input binary file with NextBASIC code')
    parser.add_argument('-n',
                        '--name',
                        required=False,
                        action='store',
                        dest='program_name',
                        help='Text for #program directive')

    arguments = parser.parse_args()

    values = {}

    i_path = None
    if arguments.input_path:
        i_path = Path(arguments.input_path)

    o_path = None
    if arguments.output_path:
        o_path = Path(arguments.output_path)
    values['output'] = o_path

    if i_path:
        if not i_path.exists():
            str_msg = _('Path not found: {0}')
            LOGGER.error(str_msg.format(i_path))
            str_msg = _('Input path does not exist!')
            raise IOError(str_msg)

    p_name = ''
    if arguments.program_name:
        p_name = Path(arguments.program_name)
    values['name'] = p_name

    values['input'] = i_path

    return values


def procbin(b_data, i_len):
    arr_str = []
    prev_line = -1
    while i_len > 4:
        line_number = int.from_bytes(b_data[:2], 'big')
        l_length = int.from_bytes(b_data[2:4], 'little')
        if line_number < prev_line or line_number > 9999:
            LOGGER.debug('End of program: Line {0}'.format(line_number))
            break
        prev_line = line_number

        b_data = b_data[4:]
        i_len = i_len - 4

        n_counter = 0
        tkn_expand = 1
        b_eol = False
        b_rem = False
        str_line = u''
        while l_length:
            b_char = b_data[:1]
            i_char = int.from_bytes(b_char, "big")
            s_char = chr(i_char)

            b_data = b_data[1:]
            l_length = l_length - 1
            i_len = i_len - 1

            # EOL char only valid at the real End Of Line
            if i_char == 0x0d and not l_length:
                b_eol = True
                break

            # Skip number 5-bytes data
            if i_char == 0x0e and not n_counter and not b_rem:
                n_counter = 6
            if n_counter:
                n_counter -= 1
                continue

            # Quoted data
            if s_char == '"':
                tkn_expand = 1 - tkn_expand

            # Comments
            if b_rem:
                tkn_expand = 0

            if tkn_expand:
                # Token expansion
                if i_char in TOKENS:
                    s_char = '{0} '.format(TOKENS[i_char])
            else:
                # Char conversion
                if s_char in CHARS:
                    s_char = '{0}'.format(CHARS[s_char])
                else:
                    # Escape non printable character
                    if i_char < 0x20 or i_char > 0x7e:
                        s_char = '`x{:02x}'.format(i_char)

            # Detect REM
            if i_char == 0x0EA:
                b_rem = True

            # Detect ; comments
            if s_char == ';' and tkn_expand:
                if not str_line.strip() or str_line.strip()[-1] == ':':
                    b_rem = True

            str_line += s_char

        str_line = str_line.strip()
        str_line += '\r\n'

        arr_str.append('{0:>4} {1}'.format(line_number, str_line))
        LOGGER.debug('{0}-> {1}'.format(line_number, str_line))

    return arr_str


# Constants
# ---------

CHARS = {
    '`': '£',
    127: '©',
    129: '\u259D',  # Quadrant upper right
    130: '\u2598',  # Quadrant upper left
    131: '\u2580',  # Upper half block
    132: '\u2597',  # Quadrant lower right
    133: '\u2590',  # Right half block
    134: '\u259A',  # Quadrant upper left and lower right
    135: '\u259C',  # Quadrant upper left and upper right and lower right
    136: '\u2596',  # Quadrant lower left
    137: '\u259E',  # Quadrant upper right and lower left
    138: '\u258C',  # Left half block
    139: '\u259B',  # Quadrant upper left and upper right and lower left
    140: '\u2584',  # Lower half block
    141: '\u259F',  # Quadrant upper right and lower left and lower right
    142: '\u2599',  # Quadrant upper left and lower left and lower right
    143: '\u2588'  # Full block
}

TOKENS = {
    135: 'PEEK$',
    136: 'REG',
    137: 'DPOKE',
    138: 'DPEEK',
    139: ' MOD',
    140: '<<',
    141: '>>',
    142: 'UNTIL',
    143: 'ERROR',
    144: ' ON',
    145: 'DEFPROC',
    146: 'ENDPROC',
    147: 'PROC',
    148: 'LOCAL',
    149: 'DRIVER',
    150: 'WHILE',
    151: 'REPEAT',
    152: 'ELSE',
    153: 'REMOUNT',
    154: 'BANK',
    155: 'TILE',
    156: 'LAYER',
    157: 'PALETTE',
    158: 'SPRITE',
    159: 'PWD',
    160: 'CD',
    161: 'MKDIR',
    162: 'RMDIR',
    163: 'SPECTRUM',
    164: 'PLAY',
    165: 'RND',
    166: 'INKEY$',
    167: 'PI',
    168: 'FN',
    169: 'POINT',
    170: 'SCREEN$',
    171: 'ATTR',
    172: 'AT',
    173: 'TAB',
    174: 'VAL$',
    175: 'CODE',
    176: 'VAL',
    177: 'LEN',
    178: 'SIN',
    179: 'COS',
    180: 'TAN',
    181: 'ASN',
    182: 'ACS',
    183: 'ATN',
    184: 'LN',
    185: 'EXP',
    186: 'INT',
    187: 'SQR',
    188: 'SGN',
    189: 'ABS',
    190: 'PEEK',
    191: ' IN',
    192: 'USR',
    193: 'STR$',
    194: 'CHR$',
    195: ' NOT',
    196: 'BIN',
    197: ' OR',
    198: ' AND',
    199: ' <=',
    200: ' >=',
    201: ' <>',
    202: 'LINE',
    203: ' THEN',
    204: ' TO',
    205: ' STEP',
    206: 'DEF FN',
    207: 'CAT',
    208: 'FORMAT',
    209: 'MOVE',
    210: 'ERASE',
    211: 'OPEN #',
    212: 'CLOSE #',
    213: 'MERGE',
    214: 'VERIFY',
    215: 'BEEP',
    216: 'CIRCLE',
    217: 'INK',
    218: 'PAPER',
    219: 'FLASH',
    220: 'BRIGHT',
    221: 'INVERSE',
    222: 'OVER',
    223: 'OUT',
    224: 'LPRINT',
    225: 'LLIST',
    226: 'STOP',
    227: 'READ',
    228: 'DATA',
    229: 'RESTORE',
    230: 'NEW',
    231: 'BORDER',
    232: 'CONTINUE',
    233: 'DIM',
    234: 'REM',
    235: 'FOR',
    236: 'GO TO',
    237: 'GO SUB',
    238: 'INPUT',
    239: 'LOAD',
    240: 'LIST',
    241: 'LET',
    242: 'PAUSE',
    243: 'NEXT',
    244: 'POKE',
    245: 'PRINT',
    246: 'PLOT',
    247: 'RUN',
    248: 'SAVE',
    249: 'RANDOMIZE',
    250: 'IF',
    251: 'CLS',
    252: 'DRAW',
    253: 'CLEAR',
    254: 'RETURN',
    255: 'COPY'
}

CHARS = {
    '`': '£',
    '\x7f': '©',
    '\x81': '\u259D',  # Quadrant upper right
    '\x81': '\u259D',  # Quadrant upper right
    '\x82': '\u2598',  # Quadrant upper left
    '\x83': '\u2580',  # Upper half block
    '\x84': '\u2597',  # Quadrant lower right
    '\x85': '\u2590',  # Right half block
    '\x86': '\u259A',  # Quadrant upper left and lower right
    '\x87': '\u259C',  # Quadrant upper left and upper right and lower right
    '\x88': '\u2596',  # Quadrant lower left
    '\x89': '\u259E',  # Quadrant upper right and lower left
    '\x8a': '\u258C',  # Left half block
    '\x8b': '\u259B',  # Quadrant upper left and upper right and lower left
    '\x8c': '\u2584',  # Lower half block
    '\x8d': '\u259F',  # Quadrant upper right and lower left and lower right
    '\x8e': '\u2599',  # Quadrant upper left and lower left and lower right
    '\x8f': '\u2588',  # Full block
}

if __name__ == '__main__':
    main()
