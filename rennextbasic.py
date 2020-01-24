#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# Do not change the previous lines. See PEP 8, PEP 263.
"""
Text NextBASIC Renumbering

    Copyright (c) 2020 @Kounch

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

try:
    from pathlib import Path
except (ImportError, AttributeError):
    from pathlib2 import Path

__MY_VERSION__ = '0.2'

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
    with open(arg_data['input'], 'r') as f:
        code = f.readlines()

    arr_lines = {}
    for line in code:
        test_line = line.strip()
        if test_line and test_line[
                0] != '#':  # Lines with only comments and directives aren't parsed

            # Split line number and content, then catalog
            det_comm = re.compile('(\\s*\\d+)\\s*(.*)')
            match_comm = det_comm.match(line)
            if match_comm:
                l_number = int(match_comm.group(1).strip())
                l_text = match_comm.group(2).strip()
                if l_number not in arr_lines:
                    arr_lines[l_number] = [0, l_text]
                else:
                    LOGGER.error(
                        'Duplicated line number: {0}'.format(l_number))
            else:
                LOGGER.warn('Line number not found: ´{0}'.format(line))

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
        LOGGER.warn('Too many lines ({0})!. Step changed to: ´{1}'.format(
            max_lines, n_step))
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
        new_lines = []
        for line in code:
            test_line = line.strip()
            if test_line:
                if test_line[
                        0] == '#':  # Lines with only comments and directives aren't parsed
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
                            l_text += '{0}\n'.format(match_comm.group(3))

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
                                LOGGER.error(
                                    'Line not found!: {0} in line {1}({2})'.
                                    format(old_number, l_number, new_number))

                    new_line += l_text + '\n'
                    new_lines.append(new_line)

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
        LOGGER.debug('Nothing to do')


# Functions
# ---------


def parse_args():
    """Command Line Parser"""

    parser = argparse.ArgumentParser(description='NextBASIC TXT Renumber')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s {}'.format(__MY_VERSION__))
    parser.add_argument('-i',
                        '--input',
                        action='store',
                        dest='input_path',
                        help='Input text file with BASIC code')
    parser.add_argument('-o',
                        '--output',
                        action='store',
                        dest='output_path',
                        help='Output file path')
    parser.add_argument('-s',
                        '--step',
                        action='store',
                        dest='step',
                        help='Line number step size')

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
        LOGGER.error('Path not found: %s', i_path)
        raise IOError('Input path does not exist!')

    values['input'] = i_path
    values['output'] = o_path
    values['step'] = step

    return values


if __name__ == '__main__':
    main()
