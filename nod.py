import asyncio
import json
import multiprocessing
import logging

LOGGER = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
data = {

}

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
                LOGGER.info('Recived response: ', node_resp)
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
            LOGGER.info('Sending data...')
            writer.write(payload)
            yield from writer.drain()


    def start(self):
        serv = asyncio.start_server(self.responde, self.ip, self.port, loop=self.loop)
        proxy = self.loop.run_until_complete(serv)
        try:
            LOGGER.info('Node started on port: %s', self.port)
            self.loop.run_forever()
        except Exception:
            LOGGER.info('Node error ! %s', Exception)
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
    node =Node(mast=master, port=port, slaves=slaves)
    node.start()


if __name__ == "__main__":
    node1 = multiprocessing.Process(target=start_node, args=(False, 1111, []))
    node2 = multiprocessing.Process(target=start_node, args=(True, 1112, [1111, 1113, 1114]))
    node3 = multiprocessing.Process(target=start_node, args=(False, 1113, []))
    node4 = multiprocessing.Process(target=start_node, args=(True, 1114, [1112, 1115, 1116]))
    node5 = multiprocessing.Process(target=start_node, args=(False, 1115, []))
    node6 = multiprocessing.Process(target=start_node, args=(False, 1116, []))

    node1.start()
    node2.start()
    node3.start()
    node4.start()
    node5.start()
    node6.start()
