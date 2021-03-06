# This code is part of the checkmate project.
# Copyright (C) 2015-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os
import re
import sys
import argparse
import datetime

notice_head = """\
# This code is part of the checkmate project.
# Copyright (C) 2013 The checkmate project contributors
#
"""

short_free_software = """\
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

"""

long_free_software = """\
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-rm', '--remove', action='store_true')
    parser.add_argument('path', nargs=1)
    opts = parser.parse_args()
    for root, dirs, files in os.walk(opts.path[0]):
        for f in files:
            filepath = os.path.join(root, f)
            if opts.remove:
                if filepath.endswith('__init__.py'):
                    remove_header(filepath, notice_head + long_free_software) 
                elif filepath.endswith('.py'):
                    remove_header(filepath, notice_head + short_free_software)
            elif filepath.endswith('__init__.py'):
                with open(filepath, 'r') as f:
                    content = f.read()
                    content = update_header(content, notice_head +
                                long_free_software) 
            elif filepath.endswith('.py'):
                with open(filepath, 'r') as f:
                    content = f.read()
                    content = update_header(content, notice_head +
                                short_free_software)
                    write_content(filepath, content)

def update_header(content, header):
    """
    >>> import re
    >>> import datetime
    >>> import checkmate.tools.update_header
    >>> head = checkmate.tools.update_header.notice_head.replace(
    ...             '2013','2012')
    >>> print(head)
    # This code is part of the checkmate project.
    # Copyright (C) 2012 The checkmate project contributors
    #
    <BLANKLINE>
    >>> update = checkmate.tools.update_header.update_header(head, "")
    >>> print(update) #doctest: +ELLIPSIS
    # This code is part of the checkmate project.
    # Copyright (C) 2012-2...
    """
    d = datetime.date.today()
    d_year = str(d.year)
    if not content.startswith('#'):
        content = header.replace("2013", d_year) + content
    else:
        match = re.search(r".*Copyright\D+(\d[0-9-, ]+\d)\D", content)
        if match is not None:
            years = match.group(1).strip()
            if not d_year in years:
                if len(years) == 4:
                    new_years = years + '-' + d_year
                else:
                    new_years = years[:4] + '-' + d_year
                content = content.replace(years,new_years)
    return content

def remove_header(input_file, header):
    content = ''
    with open(input_file, 'r') as f:
        for line in f.readlines()[header.count('\n'):]:
            content += line
        write_content(input_file, content)
        f.close()

def write_content(input_file, content):
    with open(input_file, 'w') as new:
        new.write(content)
        new.close()

if __name__ == "__main__":
  main()
