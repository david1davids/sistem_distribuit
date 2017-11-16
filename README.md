## `Sistem Distribuit` - function description
The aplication consists of 4 elements, `node`, `client` and `proxy`.
There are 3 auxilary files:
- `json_schema.json` - this is the JSON validation schema;
- `xml_schema.xml` - this is the XML validation schema;
-  `conf.json` - this is the configuration file of the aplication;
- `node_data.py` - this contains the data for every node;

## Description of the `communication protocol` protocol
The communication protocol is based on JSON.
The commands of the protocol are:
- `get` - for requesting for the data;
- `respond` - for sending the data that was needed;

The fields of the communication protocol differ depending on the component that sends the message:
# Client 
- `type` - type of message;
- `command` - the command of the message, it has only the `get` command;
- `sort` - it can be `true` or `false`;
- `filter` - sets the filter parameters;
- `xml` - it can be `true` or `false`, it specifies if the client requests for `xml` data;

# Proxy
- `type` - type of message `command` or `response`;
- `command` - the command;
- `filter` - the filter parameters;
- `payload` - the payload;

# Node
The `node` has the same set of parameters in the communications messages as the `proxy`:
- `type` - type of message `command` or `response`;
- `command` - the command;
- `filter` - the filter parameters;
- `payload` - the payload;

