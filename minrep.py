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
import shutil
import sys
import re

class PatternSearch(object):
    @staticmethod
    def include(string):
        include_pattern = re.compile('(\*/)?(\s*#include\s*["<])([/.a-zA-Z0-9_]*)([">])')
        inc = include_pattern.search(string)
        if inc:
            return inc.group(3)
        else:
            return None

class MinRep(object):
    """
    Should write some documentation here...
    """
    def __init__(self, minrep_dir, minrep_include_dir, overwrite = False):
        self.collected_include_files = []
        self.minrep_dir = minrep_dir
        self.minrep_include_dir = minrep_include_dir
        self.new_file = minrep_dir / Path(f).name

        if minrep_dir.is_dir():
            if overwrite:
                shutil.rmtree(str(minrep_dir))
            else:
                raise RuntimeError("Dir {} already exists".format(minrep_dir))

        minrep_dir.mkdir()
        path_to_inc = minrep_dir / minrep_include_dir
        path_to_inc.mkdir()

    def _parseFile(self, path_to_file, subfolder = None):
        if subfolder:
            new_dest_file = self.minrep_dir / self.minrep_include_dir / path_to_file.name
        else:
            new_dest_file = self.minrep_dir / path_to_file.name
        with open(str(path_to_file), "r") as header_file, open(str(new_dest_file), "w") as dest_file:
            for line in header_file.readlines():
                include = PatternSearch.include(line)
                if include:
                    header_source = path_to_file.parent / Path(include)
                    if header_source.is_file():
                        header_source = header_source.resolve()
                        new_header_source = \
                                self.minrep_dir / self.minrep_include_dir / header_source.name
                        dest_file.writelines('#include "{}"\n'.format(new_header_source.name))
                        if not header_source in self.collected_include_files:
                            self.collected_include_files.append(header_source)
                            self._parseFile(header_source, self.minrep_include_dir)
                    else:
                        dest_file.writelines(line)
                else:
                    dest_file.writelines(line)

    def writeFile(self, src_file):
        if not Path(src_file).is_file():
            raise RuntimeError("File {} does not exist".format(src_file))
        else:
            self._parseFile(Path(src_file))

if __name__ == "__main__":
    parser = ap.ArgumentParser(description = "Provide a source file")
    parser.add_argument("-d", "--destination", default = "MinRep", help = "Provide destination directory")
    parser.add_argument("-f", "--force", action = "store_true", help = "Force overwrite destination directory")
    parser.add_argument("cpp_file", nargs = 1, help = "Only one file!")
    args = parser.parse_args()

    minrep_dir = Path(args.destination)
    minrep_include_dir = Path("include")

    f = args.cpp_file[0]

    minrep = MinRep(minrep_dir, minrep_include_dir, args.force)
    minrep.writeFile(f)
