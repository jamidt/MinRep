#!/usr/bin/env python3
"""
Extract header dependencies for source file.

Copyright (C) 2017  Jan Schmidt

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse as ap
from pathlib import Path
import sys
import re


class MinRep(object):
    """
    Should write some documentation here...
    """
    def __init__(self, minrep_dir, minrep_include_dir):
        self.collected_include_files = []
        self.minrep_dir = minrep_dir
        self.minrep_include_dir = minrep_include_dir
        self.new_file = minrep_dir / Path(f).name
        self.include_pattern = re.compile('^\s*(#include\s*"|<)(.+)("|>)')
        if minrep_dir.is_dir():
            sys.exit("Dir {} already exists".format(minrep_dir))
        else:
            minrep_dir.mkdir()
            path_to_inc = minrep_dir / minrep_include_dir
            path_to_inc.mkdir()

    def parse_header(self, path_to_header):
        new_dest_file = self.minrep_dir / self.minrep_include_dir / path_to_header.name
        with open(str(path_to_header), "r") as header_file:
            dest_file = open(str(new_dest_file), "w")
            for line in header_file.readlines():
                include = self.include_pattern.search(line)
                if include:
                    header_source = path_to_header.parent / Path(include.group(2))
                    if header_source.is_file():
                        header_source = header_source.resolve()
                        new_header_source = \
                                self.minrep_dir / self.minrep_include_dir / header_source.name
                        dest_file.writelines('#include "{}"\n'.format(new_header_source.name))
                        if not header_source in self.collected_include_files:
                            self.parse_header(header_source)
                    else:
                        dest_file.writelines(line)
                else:
                    dest_file.writelines(line)

    def writeFile(self, src_file):
        with open(f, "r") as src_file:
            dest_file = open(str(self.new_file), "w")
            for line in src_file.readlines():
                include = self.include_pattern.search(line)
                if include:
                    header_source = Path(include.group(2))
                    if header_source.is_file():
                        self.collected_include_files.append(header_source.resolve())
                        new_dir = self.minrep_include_dir / header_source.name
                        to_file = '#include "{}"\n'.format(new_dir)
                        dest_file.writelines(to_file)
                    else:
                        dest_file.writelines(line)
                else:
                    dest_file.writelines(line)
        for header_file in self.collected_include_files:
            self.parse_header(header_file)

if __name__ == "__main__":
    parser = ap.ArgumentParser(description = "Provide a source file")
    parser.add_argument("-d", "--destination", default = "MinRep", help = "Provide destination directory")
# parser.add_argument("-f", "--force", action = "store_false", help = "Force overwrite destination directory")
    parser.add_argument("cpp_file", nargs = 1, help = "Only one file!")
    args = parser.parse_args()

    minrep_dir = Path("MinRep")
    minrep_include_dir = Path("include")

    f = args.cpp_file[0]

    if not Path(f).is_file():
        sys.exit("File {} does not exist".format(f))

    minrep = MinRep(minrep_dir, minrep_include_dir)
    minrep.writeFile(f)
