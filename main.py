import json
import sys
from enum import Enum
from pprint import pprint


class ObjectType(Enum):
    EdgeDetector = 1
    AndGate = 2
    RSTrigger = 3
    Port = 4


class PinType(Enum):
    Input = 1
    Output = 2


class PortType(Enum):
    Input = 1
    Output = 2


class Pin:
    def __init__(self, type, name, object):
        self.type = type
        self.name = name
        self.line = None
        self.object = object

    def set_line(self, line):
        self.line = line

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class InputPin(Pin):
    def __init__(self, name, object):
        super().__init__(PinType.Input, name, object)


class OutputPin(Pin):
    def __init__(self, name, object):
        super().__init__(PinType.Output, name, object)


class Object:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.input_pins = []
        self.output_pins = []
        if type == ObjectType.AndGate:
            self.input_pins.append(InputPin("i1", self))
            self.input_pins.append(InputPin("i2", self))
            self.output_pins.append(OutputPin("o", self))
        if type == ObjectType.RSTrigger:
            self.input_pins.append(InputPin("s", self))
            self.input_pins.append(InputPin("c", self))
            self.input_pins.append(InputPin("r", self))
            self.output_pins.append(OutputPin("q", self))
            self.output_pins.append(OutputPin("nq", self))
        if type == ObjectType.EdgeDetector:
            self.input_pins.append(InputPin("x", self))
            self.output_pins.append(OutputPin("e", self))

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class Port(Object):
    def __init__(self, name, type):
        super().__init__(name, ObjectType.Port)
        self.port_type = type
        if type == PortType.Input:
            self.output_pins.append(OutputPin("i", self))
        if type == PortType.Output:
            self.input_pins.append(InputPin("o", self))


class Line:
    def __init__(self):
        self.first_point = None
        self.second_point = None

    def set_points(self, first_point, second_point):
        self.first_point = first_point
        self.second_point = second_point

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class Schema:
    def __init__(self):
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
                result.objects[name] = Port(name, PortType.Input)
            if type == "OUTPUT":
                result.objects[name] = Port(name, PortType.Output)
            if type == "AND":
                result.objects[name] = Object(name, ObjectType.AndGate)
            if type == "RST":
                result.objects[name] = Object(name, ObjectType.RSTrigger)
            if type == "ED":
                result.objects[name] = Object(name, ObjectType.EdgeDetector)
        for line in json["lines"]:
            points = []
            for point in line["points"]:
                points.append(point["name"])
            line = Line()
            first_point = next((x for x in result.objects[points[0][0]].output_pins if x.name == points[0][1]), None)
            first_point.set_line(line)
            second_point = next((x for x in result.objects[points[1][0]].input_pins if x.name == points[1][1]), None)
            second_point.set_line(line)
            line.set_points(first_point, second_point)
            result.lines.append(line)
        return result


class JsonReader:
    def read(self, filename):
        with open(filename) as file:
            return json.load(file)


class SchemaVizuailzer:
    def vizualize(self, schema):
        def declare_object(object):
            def pin(i):
                return "<"+i.name+">"+i.name
            graph = ""
            graph += object.name + '[label="{ '
            if object.input_pins:
                graph += '{' + "|".join(pin(i) for i in object.input_pins) + "}|"
            graph += object.name
            if object.output_pins:
                graph += '|{' + "|".join(pin(i) for i in object.output_pins) + "}"
            graph += ' }"];\n'
            return graph

        graph = "digraph G {\n"
        graph += "graph [rankdir = LR];\n"
        graph += "node[shape=record];\n"
        for name in schema.objects:
            graph += declare_object(schema.objects[name])
        for line in schema.lines:
            first_point = line.first_point
            second_point = line.second_point
            graph += first_point.object.name + ":" + first_point.name + \
            ' -> ' + second_point.object.name + ":" + second_point.name + \
            '[label="' + first_point.object.name + ":" + first_point.name + '"];\n'
        graph += "}"
        return graph


class TimeMoment(Enum):
    Current = 1
    Previous = 2


class DependencyList:
    def __init__(self):
        self.deps = {}

    def add(self, var, variables, vector):
        self.deps[var] = (variables, vector)

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class NamesManager:
    def pin_name(self, pin):
        return pin.object.name + ":" + pin.name

    def line_name(self, line):
        return self.pin_name(line.first_point)


class DependencyBuilder:
    def build(self, schema, names):
        list = DependencyList()
        for line in schema.lines:
            variables = []
            vector = ()
            first_point = line.first_point
            object = first_point.object
            object_type = object.type
            if object_type == ObjectType.Port:
                pass
            elif object_type == ObjectType.EdgeDetector:
                variables.append((\
                                  names.line_name(object.input_pins[0].line), \
                                  TimeMoment.Previous))
                variables.append((\
                                  names.line_name(object.input_pins[0].line), \
                                  TimeMoment.Current))
                vector = (0, 1, 0, 0)
            elif object_type == ObjectType.AndGate:
                variables.append((\
                                  names.line_name(object.input_pins[0].line), \
                                  TimeMoment.Current))
                variables.append((\
                                  names.line_name(object.input_pins[1].line), \
                                  TimeMoment.Current))
                vector = (0, 0, 0, 1)
            elif object_type == ObjectType.RSTrigger:
                variables.append((\
                                  names.line_name(object.input_pins[0].line), \
                                  TimeMoment.Current))
                variables.append((\
                                  names.line_name(object.input_pins[1].line), \
                                  TimeMoment.Current))
                variables.append((\
                                  names.line_name(object.input_pins[2].line), \
                                  TimeMoment.Current))
                variables.append((\
                                  names.pin_name(first_point), \
                                  TimeMoment.Previous))
                if first_point.name == "q":
                    vector = (0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, None, None)
                else:
                    vector = (1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, None, None)
            variable = names.pin_name(first_point)
            list.add(variable, variables, vector)
        return list


class Application:
    def process(self, prev, curr, dependencies):
        def check_dependoncies(vars):
            for var, moment in vars:
                if moment == TimeMoment.Previous and var in prev:
                    continue
                elif moment == TimeMoment.Previous or var not in curr:
                    return (False, var)
            return (True,)

        while len(prev) != len(curr):
            def iter(var):
                d = dependencies.deps[var]
                res = check_dependoncies(d[0])
                if not res[0]:
                    iter(res[1])
                else:
                    pos = 0
                    for v, moment in d[0]:
                        pos *= 2
                        pos += prev[v] if moment == TimeMoment.Previous else curr[v]
                    curr[var] = d[1][pos]
            iter(next((x for x in prev if x not in curr), None))
        return curr


    def run(self, input_file):
        json = JsonReader().read(input_file)
        #print(json)
        schema = SchemaBuilder().build(json)
        #pprint(schema)
        print(SchemaVizuailzer().vizualize(schema))
        deps = DependencyBuilder().build(schema, NamesManager())

        prev_moment = {'ed_1:e':0, 'rs_1:q':0, 'rs_2:q':0, 'rs_1:nq':1, 'rs_2:nq':1, 'and_1:o':0, 'ed_2:e':0, 'and_2:o':0, 'rs_3:q':0, 'rs_3:nq':0, 'rs_4:q':0, 'rs_4:nq':0,\
                       'c_1:i':0, 'c_2:i':0, 'r_1:i':0, 'r_2:i':0, 's_1:i':0, 's_2:i':0}
        curr_moment = {'c_1:i':1, 'c_2:i':0, 'r_1:i':0, 'r_2:i':0, 's_1:i':1, 's_2:i':1}
        #print(self.process(prev_moment, curr_moment, deps))


if __name__ == '__main__':
    app = Application()
    app.run(sys.argv[1])
