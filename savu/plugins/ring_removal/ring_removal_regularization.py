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
.. module:: Remove stripe artefacts  
   :platform: Unix
   :synopsis: A plugin working in sinogram space to remove stripe artefacts     
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>    
   
"""
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.data.plugin_list import CitationInformation
import numpy as np


@register_plugin
class RingRemovalRegularization(Plugin, CpuPlugin):
    """

    Method to remove stripe artefacts in a sinogram (<-> ring artefacts in a\ 
    reconstructed image) using a regularization-based method. 
    A simple improvement to handle partial stripes is included.    
    :param alpha: The correction strength. Smaller is stronger. Default: 0.005
    :param number_of_chunks: Divide the sinogram to many chunks of rows. \
    Default: 1
    """

    def __init__(self):
        super(RingRemovalRegularization, self).__init__(
            "RingRemovalRegularization")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', 'single')
        out_pData[0].plugin_data_setup('SINOGRAM', 'single')

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()
        width_dim = in_pData[0].get_data_dimension_by_axis_label('detector_x')
        height_dim = in_pData[0].get_data_dimension_by_axis_label(
            'rotation_angle')
        sino_shape = list(in_pData[0].get_shape())
        self.width1 = sino_shape[width_dim]
        self.height1 = sino_shape[height_dim]
        alpha = self.parameters['alpha']
        tau = 2.0 * np.arcsinh(np.sqrt(alpha) * 0.5)
        ilist = np.arange(0, self.width1)
        jlist = np.arange(0, self.width1)
        matjj, matii = np.meshgrid(jlist, ilist)
        mat1 = np.abs(matii - matjj)
        mat2 = matii + matjj
        mat1a = np.cosh((self.width1 - 1 - mat1) * tau)
        mat2a = np.cosh((self.width1 - mat2) * tau)
        self.mat_coe = -(np.tanh(0.5 * tau) /
                         (alpha * np.sinh(self.width1 * tau))) * (mat1a + mat2a)

    def process_frames(self, data):
        sinogram = np.copy(data[0])
        num_mean = np.mean(sinogram)
        sinogram[sinogram <= 0.0] = num_mean  # Note performance
        sinogram = -np.log(sinogram)
        num_chunks = np.clip(
            np.int16(self.parameters['number_of_chunks']), 1, self.height1)
        list_pos = np.array_split(np.arange(self.height1), num_chunks)
        list_grad = np.zeros(self.width1, dtype=np.float32)
        mat_grad = np.zeros((self.width1, self.width1), dtype=np.float32)
        for pos in list_pos:
            bindex = pos[0]
            eindex = pos[-1] + 1
            list_mean = np.mean(sinogram[bindex:eindex, :], axis=0)
            list_grad[1:-1] = - np.diff(list_mean, 2)
            list_grad[0] = list_mean[0] - list_mean[1]
            list_grad[-1] = list_mean[-1] - list_mean[-2]
            mat_grad[:] = list_grad
            list_corr = np.sum(mat_grad * self.mat_coe, axis=1)
            mat_corr = np.zeros(
                (eindex - bindex, self.width1), dtype=np.float32)
            mat_corr[:] = list_corr
            sinogram[bindex:eindex, :] = sinogram[bindex:eindex, :] + mat_corr
        return np.exp(-sinogram)

    def get_citation_information(self):
        cite_info = CitationInformation()
        cite_info.description = \
            ("The code of ring removal is the implementation of the work of \
            Sofya Titarenko et al. taken from this paper.")
        cite_info.bibtex = \
            ("@article{TITARENKO20101489,\n" +
             "title={An analytical formula for ring artefact suppression in \
             X-ray tomography},\n" +
             "author={Sofya Titarenko, Philip J. Withers and \
             Anatoly Yagola},\n" +
             "journal={Applied Mathematics Letters},\n" +
             "volume={23},\n" +
             "number={12},\n" +
             "pages={1489 - 1495},\n" +
             "year={2010},\n" +
             "publisher={Elsevier}" +
             "}")
        cite_info.doi = "doi: DOI: 10.1016/j.aml.2010.08.022"
        return cite_info
