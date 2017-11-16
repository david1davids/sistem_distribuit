import asyncio
import json
from xml.dom.minidom import parseString
from lxml import etree
import jsonschema
import socket
import logging

LOGGER = logging.getLogger(__name__)

class Client:
    def __init__(self, sort, filt, xml, proxy_p = 1110, proxy_ip = 'localhost'):
        self.proxy_p = proxy_p
        self.proxy_ip = proxy_ip
        self.sort = sort
        self.filt = filt
        self.xml = xml

    def start(self):
        LOGGER.debug('Starting client')
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((self.proxy_ip, self.proxy_p))
        payload = json.dumps({
            'type': 'command',
            'command': 'get',
            'sort': self.sort,
            'filter': self.filt,
            'xml': self.xml
        }).encode('utf-8')
        connection.send(payload)
        data_r = json.loads(connection.recv(1024).decode('utf-8')).get('payload')
        return data_r


if __name__ == "__main__":
    xml = True
    filter_field = "age"
    filter_op = "__ge__"
    filter_val = 30
    client = Client(sort=True, filt={
        'field': filter_field,
        'op': filter_op,
        'val': filter_val
        }, xml=xml)

    data = client.start()
    if xml:
        dom = parseString(data)
        print(dom.toprettyxml())
        with open("data.xml", "wb") as f:
            f.write(data.encode())
        xml_name = "data.xml"
        doc = etree.parse(xml_name)
        relaxng_doc = etree.parse("xml_schema.xml")
        relaxng = etree.RelaxNG(relaxng_doc)
        print(relaxng.validate(doc))
        relaxng.assertValid(doc)
    else:
        with open("json_schema.json", "r") as s:
            schema = json.loads(s.read())
        jsonschema.Draft4Validator.check_schema(schema)
        jsonschema.validate(json.loads(data), schema)
        with open("data.json", "wb") as f:
            f.write(data.encode())
