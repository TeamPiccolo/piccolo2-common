# Copyright 2014-2016 The Piccolo Team
#
# This file is part of piccolo2-common.
#
# piccolo2-common is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# piccolo2-common is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with piccolo2-common.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

setup(
    name = "piccolo2-common",
    version = "0.1",
    namespace_packages = ['piccolo2'],
    packages = find_packages(),

    # metadata for upload to PyPI
    author = "Magnus Hagdorn, Alasdair MacArthur, Iain Robinson",
    description = "Part of the piccolo2 system. This package provides common modules",
    license = "GPL",
    url = "https://bitbucket.org/uoepiccolo/piccolo2-common",
)
