# use http://localhost:8787/status to see the dask status, its quite cool

from distributed import Client
from savu.data.plugin_list import PluginList
client = Client()
print(client)

from time import sleep
from random import random

import numpy as np

pl = PluginList()
pl._populate_plugin_list("/media/mark/_scratch/git/Savu/test_data/test_process_lists/denoise_bregman_test.nxs")

def savu_plugin_runner(x, clazz=None):
    plugin = clazz()
    plugin._populate_default_parameters()
    return plugin.process_frames([x])

from savu.plugins.filters.denoise_bregman_filter import DenoiseBregmanFilter
from savu.plugins.filters.image_interpolation import ImageInterpolation
from savu.plugins.reshape.downsample_filter import DownsampleFilter
plugins = [DenoiseBregmanFilter, ImageInterpolation, DownsampleFilter]


from Queue import Queue
input_q = Queue()

steps = [client.scatter(input_q)]

for plugin in plugins:
    steps.append(client.map(savu_plugin_runner, steps[-1], clazz=plugin))

result_q = client.gather(steps[-1])



#remote_q = client.scatter(input_q)
#breg_q = client.map(savu_plugin_runner, remote_q, clazz=DenoiseBregmanFilter)
#interp_q = client.map(savu_plugin_runner, breg_q, clazz=ImageInterpolation)
#down_q = client.map(savu_plugin_runner, interp_q, clazz=DownsampleFilter)
#result_q = client.gather(down_q)

print(result_q.qsize()) 

def load_data(q):
    i = 0
    while i < 100:
        print("putting %i" %(i))
        q.put(np.random.rand(1,500,500))
        sleep(random())
        i += 1

from threading import Thread
load_thread = Thread(target=load_data, args=(input_q,))
load_thread.start()

for i in range(100):
    print("Size of queue is %i" % (result_q.qsize()))
    for j in range(result_q.qsize()):
        data = result_q.get()
        print("getting item %i from queue, %i(%i,%i) mean value is %f" % (j, len(data.shape), data.shape[0], data.shape[1], data.mean()))
    sleep(1)

 



