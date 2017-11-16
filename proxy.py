import asyncio
import json
import dicttoxml
import logging

LOGGER = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
class Proxy:
    def __init__(self, ip='localhost', port='1110'):
        self.ip = ip
        self.port = port
        self.loop = asyncio.get_event_loop()
        with open("conf.json") as config:
            self.config = json.load(config)


    @asyncio.coroutine
    def responde(self, reader, writer):
        data = []
        message = json.loads((yield from reader.read(1024)).decode('utf-8'))
        sort = message.get('sort')
        filt = message.get('filter')
        print(filt)
        for node in self.config:
            master = self.config[node]['master']
            try:
                if master:
                    port = self.config[node]["port"]
                    LOGGER.info('Connecting to %s on port %s', node, port)
                    node_r, node_w = yield from asyncio.open_connection('localhost', port, loop=self.loop)
                    LOGGER.info('Payload')
                    payload = json.dumps({
                        'type': 'command',
                        'command': 'get',
                        'filter': filt
                    }).encode('utf-8')
                    LOGGER.info('Sending payload...')
                    node_w.write(payload)
                    node_response = json.loads((yield from node_r.read(1024)).decode('utf-8')).get('payload')
                    print(node_response)
                    LOGGER.info('Recived data from node.')
                    data += node_response
                    if sort:
                        data = self.sort(data)
            except Exception:
                LOGGER.debug('Error, cannot get data from nodes ! %s', Exception)
                pass
        if message.get('xml'):
            xml = dicttoxml.dicttoxml(data, attr_type=False, custom_root="items").decode()
            payload = json.dumps({
                'type': 'response',
                'payload': xml,
            }).encode('utf-8')
            writer.write(payload)
            yield from writer.drain()
        else:
            payload = json.dumps({
                'type': 'response',
                'payload': json.dumps(data),
            }).encode("utf-8")
            writer.write(payload)
            yield from writer.drain()

    def start(self):
        LOGGER.info('Proxy starting on port: %s', self.port)
        serv = asyncio.start_server(self.responde, self.ip, self.port, loop=self.loop)
        proxy = self.loop.run_until_complete(serv)
        try:
            LOGGER.info('Proxy started on port: %s', self.port)
            self.loop.run_forever()
        except Exception:
            LOGGER.error('ERROR ', Exception)
            pass
        proxy.close()
        self.loop.run_until_complete(proxy.wait_closed())
        self.loop.close()

    @staticmethod
    def sort(self, data):
        return sorted(data)


if __name__ == "__main__":
    proxy = Proxy()
    proxy.start()
