# use http://localhost:8787/status to see the dask status, its quite cool

from distributed import Client
client = Client()
print(client)

from time import sleep
from random import random

import numpy as np

def savu_plugin_runner(x, clazz=None):
    plugin = clazz()
    plugin._populate_default_parameters()
    return plugin.process_frames([x])

from Queue import Queue
input_q = Queue()
remote_q = client.scatter(input_q)
from savu.plugins.filters.denoise_bregman_filter import DenoiseBregmanFilter
breg_q = client.map(savu_plugin_runner, remote_q, clazz=DenoiseBregmanFilter)
from savu.plugins.filters.image_interpolation import ImageInterpolation
interp_q = client.map(savu_plugin_runner, breg_q, clazz=ImageInterpolation)
from savu.plugins.reshape.downsample_filter import DownsampleFilter
down_q = client.map(savu_plugin_runner, interp_q, clazz=DownsampleFilter)
result_q = client.gather(down_q)

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
        print("getting item %i from queue, (%i,%i) mean value is %f" % (j, data.shape[0], data.shape[1], data.mean()))
    sleep(1)

 



