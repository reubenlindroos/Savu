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
.. module:: pyfai_azimuthal_integration_test
   :platform: Unix
   :synopsis: runner for tests using the MPI framework

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import unittest
from savu.test import test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
    run_protected_plugin_runner


class PyfaiFilteredTest(unittest.TestCase):

    def test_pyfai_filtered(self):
        data_file = tu.get_test_data_path('mm.nxs')
        process_file = tu.get_test_process_path('PyFAI_azimuth_test_bragg.nxs')
        run_protected_plugin_runner(tu.set_options(data_file,
                                                   process_file=process_file))
#    def test_pyfai_realdata(self):
#        from savu.test.travis.framework_tests.plugin_runner_test import \
#            run_protected_plugin_runner2
#        run_protected_plugin_runner2()

if __name__ == "__main__":
    unittest.main()
