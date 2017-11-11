import asyncio
import json
import multiprocessing

class Node:
    def __init__(self, port, mast, slaves, ip='localhost',):
        self.ip = ip
        self.port = port
        self.loop = asyncio.get_event_loop()
        self.master = mast
        self.slaves = slaves

    @asyncio.coroutine
    def responde(self, reader, writer):
        message = json.loads((yield from reader.read(1024)).decode('utf-8'))
        filter = message.get('filter')
        data = []
        if self.master:
            for slave in self.slaves:
                payload = json.dumps({
                    'type': 'command',
                    'command': 'get',
                    'filter': filter
                }).encode('utf-8')
                node_r, node_w = yield from asyncio.open_connection('localhost', slave, loop=self.loop)
                node_w.write(payload)
                node_resp = yield from node_r.read(1024)
                data += json.loads(node_resp.decode().get('payload'))
            payload = json.dumps({
                'type': 'response',
                'payload': data,
            }).encode('utf-8')
            writer.write(payload)
            yield from writer.drain()
        else:
            data = []
            payload = json.dumps({
                'type': 'response',
                'payload' : data,
            }).encode('utf-8')
            yield from writer.drain()


    def start(self):
        serv = asyncio.start_server(self.responde, self.ip, self.port, loop=self.loop)
        proxy = self.loop.run_until_complete(serv)
        try:
            print("Started node", self.port)
            self.loop.run_forever()
        except Exception:
            print("proxy", Exception)
            pass
        proxy.close()
        self.loop.run_until_complete(proxy.wait_closed())
        self.loop.close()

    @staticmethod
    def filter(self, data, filt):
        field = filt['field']
        op = filt['op']
        val =filt['val']
        filtered = []
        for dat in data:
            operate = getattr(dat[field], op)
            if operate(val):
                filtered.append(dat)
        return filtered


def start_node(master, port, slaves):
    node =Node(mast=master, slaves=slaves, port=port)
    node.start()


if __name__ == "__main__":
    node1 = multiprocessing(target=start_node, args=(True, 1111, [1112,1113]))