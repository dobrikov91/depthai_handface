import zmq
import struct

class ZmqPub:
    def __init__(self, topic) -> None:
        self.topic = topic
        ctx = zmq.Context.instance()

        self.publisher = ctx.socket(zmq.PUB)
        self.publisher.connect("tcp://127.0.0.1:4545")
    
    def sendDoubles(self, data) -> None:
        message = struct.pack('c'+'d'*len(data), str.encode(self.topic), *data)
        self.publisher.send(message)