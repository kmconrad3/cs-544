import grpc
import numstore_pb2
import numstore_pb2_grpc
import random
import time
import threading
import numpy as np
import sys


class Client(threading.Thread):
    
    def __init__(self, id1, port):
        threading.Thread.__init__(self)
        self.id1 = id1
        self.port = port
        self.channel = grpc.insecure_channel('localhost:' + str(self.port))
        self.stub = numstore_pb2_grpc.NumStoreStub(self.channel)
        for i in range(100):
            self.keys = str(i)
        self.times = []
        self.cache_hits = 0
        self.requests = 0
    
    def run(self):
        for i in range(1,100):
            random_request = random.choice(["SetNum", "Fact"])
            key = random.choice(self.keys)
            if random_request == "SetNum":
                value = random.randint(1, 15)
                request = numstore_pb2.SetNumRequest(key=key, value=value)
                time0 = time.time()
                response = self.stub.SetNum(request)
                time1 = time.time()
                self.times.append(time1 - time0)
            else:
                request = numstore_pb2.FactRequest(key=key)
                time0 = time.time()
                response = self.stub.Fact(request)
                time1 = time.time()
                self.times.append(time1 - time0)
                if response.hit:
                    self.cache_hits += 1
            self.requests += 1
        
    def get_times(self):
        return self.times
    
    def get_hit_rate(self):  
        if self.requests != 0:  
            return self.cache_hits / self.requests
        else:
            return 0

        
        
if __name__ == '__main__':
    port = sys.argv[1]
    threads = []
    for i in range(8):
        thread = Client(i, port)
        threads.append(thread)
        thread.start()
    for i in threads:
        i.join() 
    response_time_list = []
    cache_hits = 0
    all_requests = 0
    for i in threads:
        response_time_list += i.get_times()
        cache_hits += i.get_hit_rate() * i.requests
        all_requests += i.requests
    print("Cache Hit Rate:", cache_hits / all_requests)
    print("p50 Response Time:", np.percentile(response_time_list, 50)) 
    print("p99 Response Time:", np.percentile(response_time_list, 99))