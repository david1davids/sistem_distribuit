import asyncio
import json

class Proxy:
    def __init__(self, ip='localhost', port='1110'):
        self.ip = ip
        self.port = port
        self.loop = asyncio.get_event_loop()


    @asyncio.coroutine
    def responde(self, reader, writer):
        data = []

    def start(self):
        serv = asyncio.start_server(self.responde, self.ip, self.port, loop=self.loop)
        proxy = self.run_until_complete(serv)
        try:
            print("Proxy started !")
            self.loop.run_forever()
        except Exception:
            print("Proxy ", Exception)
            pass
        proxy.close()
        self.loop.run_until_complete(proxy.wait_closed())
        self.loop.close()

    def sort(self, data):
        return sorted(data)


if __name__ == "__main__":
    proxy = Proxy()
    proxy.start()