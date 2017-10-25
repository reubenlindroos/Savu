# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. module:: nxfluo_loader
   :platform: Unix
   :synopsis: A class for loading nxfluo data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import numpy as np

from savu.plugins.loaders.mapping_loaders.base_multi_modal_loader \
    import BaseMultiModalLoader

from savu.plugins.utils import register_plugin

# Update this in the class docstring if you change it
DEFAULT_FLUO_PATH = '/entry1/instrument/fluorescence/data'


@register_plugin
class NxfluoLoader(BaseMultiModalLoader):
    """ A class to load tomography data from an NXFluo file.

    :param fluo_offset: fluo scale offset. Default: 0.0.
    :param fluo_gain: fluo gain. Default: 0.01.
    :param name: The name assigned to the dataset. Default: 'fluo'.
    :param fluo_path: The path to the data in the nexus \
        file.  Default:'/entry1/instrument/fluorescence/data' .
    """

    def __init__(self, name='NxfluoLoader'):
        super(NxfluoLoader, self).__init__(name)
        self.default_path = DEFAULT_FLUO_PATH

    def setup(self):
        # check if this is really a standard Nexus file
        path = self.parameters['fluo_path']
        nxfluo = True if path == self.default_path else False
        func = self._get_nx_entry if nxfluo else self._get_nonstandard_entry
        func(path)

    def _get_nx_entry(self, path):
        data_obj, fluo_entry = \
            self.multi_modal_setup('NXfluo', path, self.parameters['name'])

        npts = data_obj.data.shape[self.get_motor_type('None')[0]]
        gain = self.parameters["fluo_gain"]
        energy = np.arange(self.parameters["fluo_offset"], gain*npts, gain)
        mono_path = fluo_entry.name + '/instrument/monochromator/energy'
        mono_energy = data_obj.backing_file[mono_path].value
        monitor_path = fluo_entry.name + '/monitor/data'
        monitor = data_obj.backing_file[monitor_path].value

        data_obj.meta_data.set("energy", energy)
        data_obj.meta_data.set("mono_energy", mono_energy)
        data_obj.meta_data.set("monitor", monitor)
        data_obj.meta_data.set("average", np.ones(npts))

        slice_dir = tuple(range(len(data_obj.data.shape)-1))
        data_obj.add_pattern("SPECTRUM", core_dims=(-1,), slice_dims=slice_dir)

        self.set_data_reduction_params(data_obj)

    def _get_non_standard_entry(self, path):
        pass