import json
from enum import Enum
from pprint import pprint


class ObjectType(Enum):
    EdgeDetector = 1
    AndGate = 2
    RSTigger = 3
    Port = 4


class PinType(Enum):
    Input = 1
    Output = 2


class PortType(Enum):
    Input = 1
    Output = 2


class Pin:
    def __init__(self, type):
        self.type = type


class Object:
    def __init__(self, name, type):
        self.name = name
        self.type = type


class Port(Object):
    def __init__(self, name, type):
        super().__init__(name, ObjectType.Port)
        self.port_type = type


class Schema:
    def __init__(self):
        self.ports = {}
        self.objects = {}

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class SchemaBuilder:
    def build(self, json):
        result = Schema()
        for object in json["objects"]:
            name = object["name"]
            type = object["type"]
            if type == "INPUT":
                result.ports[name] = Port(name, PortType.Input)
            if type == "OUTPUT":
                result.ports[name] = Port(name, PortType.Output)
            if type == "AND":
                result.objects[name] = Object(name, ObjectType.AndGate)
        return result


class JsonReader:
    def read(self, filename):
        with open(filename) as file:
            return json.load(file)


class Application:
    def run(self, input_file):
        json = JsonReader().read(input_file)
        print(json)
        schema = SchemaBuilder().build(json)
        pprint(schema)


if __name__ == '__main__':
    app = Application()
    app.run("input.json")





