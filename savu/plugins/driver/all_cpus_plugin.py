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
.. module:: all_cpus_plugin
   :platform: Unix
   :synopsis: Base class for all plugins which want to use all CPU's on the
       target machine

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging


class AllCpusPlugin(object):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self):
        super(AllCpusPlugin, self).__init__()
        self.available_cpus = 1

    def run_process(self, data, output, processes, process):
        count = 0
        cpu_processes = []
        self.available_cpus = sum(["CPU" in i for i in processes])
        for i in ["CPU0" in i for i in processes]:
            if i:
                cpu_processes.append(count)
                count += 1
            else:
                cpu_processes.append(-1)
        if cpu_processes[process] >= 0:
            logging.debug("Running the CPUS Process %i", process)
            new_processes = [i for i in processes if "CPU0" in i]
            #logging.debug(new_processes)
            #logging.debug(cpu_processes)
            logging.debug("Process is %s",
                          new_processes[cpu_processes[process]])
            self.pre_process(0 if isinstance(data, str) else data.get_data_shape())
            self.process(data, output, new_processes,
                                cpu_processes[process])
            self.post_process()
            return
        logging.debug("Not Running the task as not CPU0")
        return

    def process(self, data, output, processes, process):
        """
        This method is called after the plugin has been created by the
        pipeline framework, self.available_cpus contains the number of
        cpus which can be used by this process

        :param data: The input data object.
        :type data: savu.data.data_structures
        :param data: The output data object
        :type data: savu.data.data_structures
        :param processes: The number of processes which will be doing the work
        :type path: int
        :param path: The specific process which we are
        :type path: int
        """
        logging.error("process needs to be implemented for proc %i of %i :" +
                      " input is %s and output is %s",
                      process, processes, data.__class__, output.__class__)
        raise NotImplementedError("process needs to be implemented")
