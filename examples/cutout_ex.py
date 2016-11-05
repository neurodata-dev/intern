﻿# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This example shows how to work with the Boss' cutout service.  We post a tiny random matrix to the Boss and read it back
While only a 3D matrix is shown, 4D data with a time component is supported as well.
Matrices should be in ZYX or TZYX format.
"""
from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *
import numpy
from requests import HTTPError


rmt = BossRemote('example.cfg')

COLL_NAME = 'gray'
EXP_NAME = 'alpha'
CHAN_NAME = 'ex_EM'

# Create or get a channel to write to
chan_setup = ChannelResource(
    CHAN_NAME, COLL_NAME, EXP_NAME, 'image', 'Example channel.', datatype='uint16')
try:
    chan_actual = rmt.get_project(chan_setup)
except HTTPError:
    chan_actual = rmt.create_project(chan_setup)

print('Data model setup.')

# Ranges use the Python convention where the number after the : is the stop
# value.  Thus, x_rng specifies x values where: 0 <= x < 8.
x_rng = [0, 8]
y_rng = [0, 4]
z_rng = [0, 5]

# Note that the numpy matrix is in Z, Y, X order.
data = numpy.random.randint(1, 3000, (5, 4, 8))
data = data.astype(numpy.uint16)

# Upload the cutout to the channel.
rmt.create_cutout(chan_actual, 0, x_rng, y_rng, z_rng, data)

# Verify that the cutout uploaded correctly.
cutout_data = rmt.get_cutout(chan_actual, 0, x_rng, y_rng, z_rng)
numpy.testing.assert_array_equal(data, cutout_data)

# Get only a small piece of the cutout.
small_cutout_data = rmt.get_cutout(chan_actual, 0, [0, 1], [0, 1], [0, 5])
numpy.testing.assert_array_equal(data[0:5, 0:1, 0:1], small_cutout_data)

# For times series data, the matrix is in t, Z, Y, X order.
time_rng = [0, 3]
time_data = numpy.random.randint(1, 3000, (3, 5, 4, 8), numpy.uint16)

rmt.create_cutout(chan_actual, 0, x_rng, y_rng, z_rng, time_data, time_rng)

time_cutout_data = rmt.get_cutout(chan_actual, 0, x_rng, y_rng, z_rng, time_rng)
numpy.testing.assert_array_equal(time_data, time_cutout_data)

# Clean up.
rmt.delete_project(chan_actual)
