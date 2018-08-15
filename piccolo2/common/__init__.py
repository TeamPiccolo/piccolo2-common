# Copyright 2018- The Piccolo Team
#
# This file is part of piccolo2-common.
#
# piccolo2-common is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# piccolo2-server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with piccolo2-common.  If not, see <http://www.gnu.org/licenses/>.

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution('piccolo2-common').version
except DistributionNotFound:
    # package is not installed
    pass

from PiccoloSpectra import *
from PiccoloStatus import *
from PiccoloWorkerThread import *
