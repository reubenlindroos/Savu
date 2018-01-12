from distributed import Client
client = Client()
print(client)

from time import sleep
from random import random


def inc(x):
    from random import random
    sleep(random() * 2)
    return x + 1

def double(x):
    from random import random
    sleep(random())
    return 2 * x

from Queue import Queue
input_q = Queue()
remote_q = client.scatter(input_q)
inc_q = client.map(inc, remote_q)
double_q = client.map(double, inc_q)
result_q = client.gather(double_q)

print(result_q.qsize()) 

def load_data(q):
    i = 0
    while i < 100:
        print("putting %i" %(i))
        q.put(i)
        sleep(random())
        i += 1

from threading import Thread
load_thread = Thread(target=load_data, args=(input_q,))
load_thread.start()

for i in range(100):
    print("Size of queue is %i" % (result_q.qsize()))
    sleep(1)

 



