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

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class Port(Object):
    def __init__(self, name, type):
        super().__init__(name, ObjectType.Port)
        self.port_type = type


class Line:
    def __init__(self, points):
        self.points = points


class Schema:
    def __init__(self):
        self.ports = {}
        self.objects = {}
        self.lines = []

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
        for line in json["lines"]:
            points = []
            for point in line["points"]:
                points.append(point["name"])
            result.lines.append(Line(points))
        return result


class JsonReader:
    def read(self, filename):
        with open(filename) as file:
            return json.load(file)


class SchemaVizuailzer:
    def vizualize(self, schema):
        graph = "digraph G {\n"
        graph += "graph [rankdir = LR];\n"
        graph += "node[shape=record];\n"
        for object in schema.objects:
            object = schema.objects[object]
            if object.type == ObjectType.AndGate:
                graph += object.name + '[label="{ {<i1>i1|<i2>i2}|' + object.name + '|{<o>o} }"];\n'
        for object in schema.ports:
            object = schema.ports[object]
            if object.type == ObjectType.Port:
                if (object.port_type == PortType.Input):
                    graph += object.name + '[label="{ ' + object.name + '|<i>i }"];\n'
                if (object.port_type == PortType.Output):
                    graph += object.name + '[label="{ <o>o|' + object.name + ' }"];\n'
        for line in schema.lines:
            first_point = line.points[0]
            second_point = line.points[1]
            graph += first_point[0] + ":" + first_point[1] + \
            ' -> ' + second_point[0] + ":" + second_point[1] + ';\n'
        graph += "}"
        return graph


class Application:
    def run(self, input_file):
        json = JsonReader().read(input_file)
        #print(json)
        schema = SchemaBuilder().build(json)
        #pprint(schema)
        print(SchemaVizuailzer().vizualize(schema))


if __name__ == '__main__':
    app = Application()
    app.run("input.json")





