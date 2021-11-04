#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not change the previous lines. See PEP 8, PEP 263.
"""
Text NextBASIC Renumbering

    Copyright (c) 2020-2021 @Kounch

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
import re
import gettext

if sys.version_info > (3, 5):
    from pathlib import Path
else:
    from pathlib2 import Path

__MY_NAME__ = 'rennextbasic.py'
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

    arg_data = parse_args()

    new_lines = []
    if arg_data['decode']:
        # Binary decoding to ` codes
        LOGGER.debug("Decoding...")
        with open(arg_data['input'], 'rb') as f:
            code = f.read()
            code = code.split(b'\r')

        for line in code:
            n_line = ''
            for i_char in line:
                if i_char in CHARS:
                    n_line += CHARS[i_char]
                elif i_char < 32 or i_char > 127:
                    n_line += '`x{:02x}'.format(i_char)
                else:
                    n_line += chr(i_char)

            new_lines.append(n_line + '\r\n')
    else:
        LOGGER.debug("Renumbering...")
        with open(arg_data['input'], 'r') as f:
            code = f.readlines()

        arr_lines = {}
        for line in code:
            test_line = line.strip()
            if test_line and test_line[
                    0] != '#':  # Lines with just directives aren't parsed
                # Split line number and content, then catalog
                det_comm = re.compile('(\\s*\\d+)\\s*(.*)')
                match_comm = det_comm.match(line)
                if match_comm:
                    l_number = int(match_comm.group(1).strip())
                    l_text = match_comm.group(2).strip()
                    if l_number not in arr_lines:
                        arr_lines[l_number] = [0, l_text]
                    else:
                        str_msg = _('Duplicated line number: {0}')
                        LOGGER.error(str_msg.format(l_number))
                else:
                    str_msg = _('Line number not found: {0}')
                    LOGGER.warn(str_msg.format(line))

        max_lines = len(arr_lines.keys())
        if max_lines < 1000:
            n_step = 10
        elif max_lines < 2000:
            n_step = 5
        elif max_lines < 5000:
            n_step = 2
        else:
            n_step = 1

        if arg_data['step'] > n_step:
            str_msg = _('Too many lines ({0})!. Step changed to: {1}')
            LOGGER.warn(str_msg.format(max_lines, n_step))
        else:
            n_step = arg_data['step']

        must_change = False

        cur_line = n_step
        for item in arr_lines:
            arr_lines[item][0] = cur_line
            if item != cur_line:
                must_change = True
            cur_line += n_step

        if must_change:
            for line in code:
                test_line = line.strip()
                if test_line:
                    if test_line[
                            0] == '#':  # Lines with directives aren't parsed
                        l_text = line
                        if test_line.startswith('#autostart '):
                            # Split line number and content
                            det_comm = re.compile('(#autostart\\s+)(\\d+)(.*)')
                            match_comm = det_comm.match(line)
                            if match_comm:
                                old_number = int(match_comm.group(2))
                                new_number = arr_lines[old_number][0]
                                l_text = '{0}'.format(match_comm.group(1))
                                l_text += '{0}'.format(new_number)
                                l_text += '{0}\r\n'.format(match_comm.group(3))

                        new_lines.append(l_text)
                    else:
                        # Split line number and content
                        det_comm = re.compile('(\\s*\\d+)\\s*(.*)')
                        match_comm = det_comm.match(line)
                        if match_comm:
                            l_number = int(match_comm.group(1).strip())
                            l_text = match_comm.group(2)

                        new_number = arr_lines[l_number][0]
                        new_line = '{0:>4} '.format(new_number)

                        # Find GO TO, GO SUB, SAVE or RESTORE
                        arr_match = [
                            '(.*\\s*go\\s+to\\s+)(\\d+)(.*)',
                            '(.*\\s*go\\s+sub\\s+)(\\d+)(.*)',
                            '(.*save\\s*".*"\\s*line\\s*)',
                            '(.*\\s*restore\\s+)(\\d+)(.*)',
                        ]
                        for str_match in arr_match:
                            det_comm = re.compile(str_match, re.IGNORECASE)
                            match_comm = det_comm.match(l_text)
                            if match_comm:
                                old_number = int(match_comm.group(2))
                                if old_number in arr_lines:
                                    new_number = arr_lines[old_number][0]
                                    l_text = '{0}'.format(match_comm.group(1))
                                    l_text += '{0}{1}'.format(
                                        new_number, match_comm.group(3))
                                else:
                                    str_msg = _(
                                        'Line not found!: {0} in line {1}({2})'
                                    )
                                    LOGGER.error(
                                        str_msg.format(old_number, l_number,
                                                       new_number))

                        new_line += l_text + '\r\n'
                        new_lines.append(new_line)

    if new_lines:
        if arg_data['output']:
            output_file = arg_data['output']
        else:
            output_file = arg_data['input']
            os.rename(
                arg_data['input'],
                arg_data['input'].with_name(arg_data['input'].name + '.bak'))

        with open(output_file, 'w') as f:
            f.writelines(new_lines)

    else:
        str_msg = _('Nothing to do')
        LOGGER.debug(str_msg)


# Functions
# ---------


def parse_args():
    """Command Line Parser"""
    str_hlp_input = _('Input text file with BASIC code')
    str_hlp_output = _('Output file path')
    str_hlp_steps = _('Line number step size')

    parser = argparse.ArgumentParser(description='NextBASIC TXT Renumber')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s {}'.format(__MY_VERSION__))
    parser.add_argument('-i',
                        '--input',
                        required=True,
                        action='store',
                        dest='input_path',
                        help=str_hlp_input)
    parser.add_argument('-o',
                        '--output',
                        action='store',
                        dest='output_path',
                        help=str_hlp_output)
    parser.add_argument('-s',
                        '--step',
                        action='store',
                        dest='step',
                        help=str_hlp_steps)
    parser.add_argument('-d',
                        '--decode',
                        action='store_true',
                        dest='decode_binary',
                        help='Decode binary BASIC data to `x codes')

    arguments = parser.parse_args()

    values = {}

    i_path = None
    if arguments.input_path:
        i_path = Path(arguments.input_path)

    o_path = None
    if arguments.output_path:
        o_path = Path(arguments.output_path)

    step = 10
    if arguments.step:
        step = int(arguments.step)

    if not i_path.exists():
        str_msg = _('Path not found: {0}')
        LOGGER.error(str_msg.format(i_path))
        str_msg = _('Input path does not exist!')
        raise IOError(str_msg)

    b_decode = False
    if arguments.decode_binary:
        b_decode = True

    values['input'] = i_path
    values['output'] = o_path
    values['step'] = step
    values['decode'] = b_decode

    return values


CHARS = {
    0x60: '£',
    0x7f: '©',
    0x81: '\u259D',  # Quadrant upper right
    0x82: '\u2598',  # Quadrant upper left
    0x83: '\u2580',  # Upper half block
    0x84: '\u2597',  # Quadrant lower right
    0x85: '\u2590',  # Right half block
    0x86: '\u259A',  # Quadrant upper left and lower right
    0x87: '\u259C',  # Quadrant upper left and upper right and lower right
    0x88: '\u2596',  # Quadrant lower left
    0x89: '\u259E',  # Quadrant upper right and lower left
    0x8a: '\u258C',  # Left half block
    0x8b: '\u259B',  # Quadrant upper left and upper right and lower left
    0x8c: '\u2584',  # Lower half block
    0x8d: '\u259F',  # Quadrant upper right and lower left and lower right
    0x8e: '\u2599',  # Quadrant upper left and lower left and lower right
    0x8f: '\u2588'  # Full block
}

if __name__ == '__main__':
    main()
