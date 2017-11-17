import asyncio
import json
import multiprocessing
import logging
import node_data

LOGGER = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

class Node:
    def __init__(self, port, mast, slaves, data, ip='localhost'):
        self.ip = ip
        self.port = port
        self.loop = asyncio.get_event_loop()
        self.master = mast
        self.slaves = slaves
        self.data = data

    @asyncio.coroutine
    def responde(self, reader, writer):
        message = json.loads((yield from reader.read(1024)).decode('utf-8'))
        filtr = message.get('filter')
        if self.master:
            data = []
            nr, n = len(self.slaves), 1
            data = []
            if filtr:
                data += self.filter(self, filtr)
            else:
                data = self.data
            for slave in self.slaves:
                n = n + 1
                payload = json.dumps({
                    'type': 'command',
                    'command': 'get',
                    'filter': filtr
                }).encode('utf-8')
                LOGGER.info('Creating connection...')
                node_r, node_w = yield from asyncio.open_connection('localhost', slave, loop=self.loop)
                node_w.write(payload)
                node_resp = yield from node_r.read(1024)
                data += json.loads(node_resp.decode()).get('payload')
                print(data)
                if n == nr:
                    break
            payload = json.dumps({
                'type': 'response',
                'payload': data,
            }).encode('utf-8')
            writer.write(payload)
            LOGGER.info('Sending data to the proxy...')
            yield from writer.drain()
        else:
            data = self.filter(self=self, filtr=filtr)
            payload = json.dumps({
                'type': 'response',
                'payload' : data,
            }).encode('utf-8')
            LOGGER.info('Sending back to master the data...')
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
    def filter(self, filtr):
        field = filtr['field']
        op = filtr['op']
        val =filtr['val']
        filtered = []
        for dat in self.data:
            operate = getattr(dat[field], op)
            if operate(val):
                filtered.append(dat)
        return filtered


def start_node(master, port, slaves, data):
    node =Node(mast=master, port=port, slaves=slaves, data=data)
    node.start()


if __name__ == "__main__":
    node1 = multiprocessing.Process(target=start_node, args=(False, 1111, [], node_data.node1_data))
    node2 = multiprocessing.Process(target=start_node, args=(True, 1112, [1111, 1113, 1114], node_data.node2_data))
    node3 = multiprocessing.Process(target=start_node, args=(False, 1113, [], node_data.node3_data))
    node4 = multiprocessing.Process(target=start_node, args=(True, 1114, [1112, 1115, 1116], node_data.node4_data))
    node5 = multiprocessing.Process(target=start_node, args=(False, 1115, [], node_data.node5_data))
    node6 = multiprocessing.Process(target=start_node, args=(False, 1116, [], node_data.node6_data))

    node1.start()
    node2.start()
    node3.start()
    node4.start()
    node5.start()
    node6.start()
