from numpy import long
from xml.etree import ElementTree
from tango import DeviceProxy


# scalar internal types
from tango._tango import DevState

IDATA_TYPE_INT_SCALAR = "int_scalar"
IDATA_TYPE_LONG_SCALAR = "long_scalar"
IDATA_TYPE_FLOAT_SCALAR = "float_scalar"
IDATA_TYPE_STRING_SCALAR = "string_scalar"
IDATA_TYPE_BOOLEAN_SCALAR = "boolean_scalar"

# spectrum internal types
IDATA_TYPE_STRING_SPECTRUM = "string_spectrum"
IDATA_TYPE_INT_SPECTRUM = "int_spectrum"
IDATA_TYPE_FLOAT_SPECTRUM = "float_spectrum"
IDATA_TYPE_BOOLEAN_SPECTRUM = "boolean_spectrum"
IDATA_TYPE_LONG_SPECTRUM = "long_spectrum"

# devstate internal type
IDATA_TYPE_STATE = "state"

# tags
OP_TAG_WRITE_ATTRIBUTE = "write_attribute"
OP_TAG_READ_ATTRIBUTE = "read_attribute"
OP_TAG_SET_VARIABLE = "set_variable"
OP_TAG_CYCLE = "cycle"
OP_TAG_WHILE = "while"
OP_TAG_IF = "if"
OP_TAG_COMMAND_INOUT = "command_inout"
OP_TAG_LOG = "log"

# lists
OPERATORS = ["greater", "lesser", "equal","notequal","greaterequal","lesserequal"]


class InternalData:

    def __init__(self, idata_name, idata_value, idata_type):

        self.idata_name = idata_name
        self.idata_type = idata_type
        self.idata_value = None

        if "spectrum" not in idata_type:

            if self.idata_type == IDATA_TYPE_INT_SCALAR:
                self.idata_value = int(idata_value[0])
            elif self.idata_type == IDATA_TYPE_FLOAT_SCALAR:
                self.idata_value = float(idata_value[0])
            elif self.idata_type == IDATA_TYPE_BOOLEAN_SCALAR:
                self.idata_value = bool(idata_value[0])
            elif self.idata_type == IDATA_TYPE_STRING_SCALAR:
                self.idata_value = idata_value[0]
            elif self.idata_type == IDATA_TYPE_STATE:
                if idata_value[0] == "ON":
                    self.idata_value = DevState.ON
                elif idata_value[0] == "OFF":
                    self.idata_value = DevState.OFF
                elif idata_value[0] == "CLOSE":
                    self.idata_value = DevState.CLOSE
                elif idata_value[0] == "OPEN":
                    self.idata_value = DevState.OPEN
                elif idata_value[0] == "INSERT":
                    self.idata_value = DevState.INSERT
                elif idata_value[0] == "EXTRACT":
                    self.idata_value = DevState.EXTRACT
                elif idata_value[0] == "MOVING":
                    self.idata_value = DevState.MOVING
                elif idata_value[0] == "STANDBY":
                    self.idata_value = DevState.STANDBY
                elif idata_value[0] == "FAULT":
                    self.idata_value = DevState.FAULT
                elif idata_value[0] == "INIT":
                    self.idata_value = DevState.INIT
                elif idata_value[0] == "RUNNING":
                    self.idata_value = DevState.RUNNING
                elif idata_value[0] == "ALARM":
                    self.idata_value = DevState.ALARM
                elif idata_value[0] == "DISABLE":
                    self.idata_value = DevState.DISABLE
                elif idata_value[0] == "UNKNOWN":
                    self.idata_value = DevState.UNKNOWN
                else:
                    raise Exception("Invalid devstate of %s variable. Allowed values are %s" % (idata_name, DevState.names))

        #----------------------- idata tipo Spectrum -------------------------------------------------------------------

        else:
            self.idata_value = []
            for each in idata_value:
                if self.idata_type == IDATA_TYPE_INT_SPECTRUM:
                    self.idata_value.append(int(each))
                elif self.idata_type == IDATA_TYPE_FLOAT_SPECTRUM:
                    self.idata_value.append(float(each))
                elif self.idata_type == IDATA_TYPE_STRING_SPECTRUM:
                     self.idata_value.append(each)
                elif self.idata_type == IDATA_TYPE_BOOLEAN_SPECTRUM:
                    self.idata_value.append(bool(each))
                else:
                    raise Exception("idata_type %s not allowed" % idata_type)
                    pass

    @property
    def idata_name(self):
        return self._idata_name

    @idata_name.setter
    def idata_name(self, idata_name):
        self._idata_name = idata_name

    @property
    def idata_value(self):
        return self._idata_value

    @idata_value.setter
    def idata_value(self, idata_value):
        self._idata_value = idata_value

    @property
    def idata_type(self):
        return self._idata_type

    @idata_type.setter
    def idata_type(self, idata_type):
        if idata_type not in [IDATA_TYPE_STRING_SCALAR, IDATA_TYPE_FLOAT_SCALAR, IDATA_TYPE_INT_SCALAR, IDATA_TYPE_BOOLEAN_SCALAR, IDATA_TYPE_BOOLEAN_SPECTRUM, IDATA_TYPE_STRING_SPECTRUM, IDATA_TYPE_FLOAT_SPECTRUM, IDATA_TYPE_INT_SPECTRUM, IDATA_TYPE_STATE]:
            raise Exception("Internal data type error")
        else:
            self._idata_type = idata_type


class Experiment:

    def __init__(self):
        self.variables = {}
        self.devices = {}

    def parse_xml(self, xml_file_path):
        xml_tree = ElementTree.parse(xml_file_path)
        xml_root = xml_tree.getroot()

        variable_nodes = xml_root.findall("variables")[0].findall("variable")
        for variable_node in variable_nodes:
            current_idata_name = variable_node.attrib["name"]
            current_idata_type = variable_node.attrib["type"]
            current_idata_value = []

            element_nodes = variable_node.findall("element")

            for element_node in element_nodes:
                current_idata_value.append(element_node.attrib["value"])

            if "scalar" in current_idata_type and not len(current_idata_value) == 1:
                raise Exception("Incorrect value %s for idata_type %s" % (current_idata_value, current_idata_type))
                pass
            if "state" in current_idata_type and not len(current_idata_value) == 1:
                raise Exception("Incorrect value %s for idata_type %s" % (current_idata_value, current_idata_type))
                pass
            elif "spectrum" in current_idata_type and len(current_idata_value) == 1:
                raise Exception("Incorrect value %s for idata_type %s" % (current_idata_value, current_idata_type))
                pass
            else:
                current_idata = InternalData(current_idata_name, current_idata_value, current_idata_type)
                self.variables[current_idata_name] = current_idata

        device_nodes = xml_root.findall("devices")[0].findall("device")
        for device_node in device_nodes:
            current_device_name = device_node.attrib["name"]
            current_device_tango_path = device_node.attrib["tango_path"]
            current_device_proxy = DeviceProxy(current_device_tango_path)
            self.devices[current_device_name] = current_device_proxy

        operation_nodes = xml_root.findall("operations")[0]
        for operation_node in operation_nodes:
            self.parse_operation(operation_node)

    def parse_operation(self, operation_node):
        if operation_node.tag == OP_TAG_WRITE_ATTRIBUTE:
            self.op_write_attribute(operation_node)
        elif operation_node.tag == OP_TAG_READ_ATTRIBUTE:
            self.op_read_attribute(operation_node)
        elif operation_node.tag == OP_TAG_SET_VARIABLE:
            self.op_set_variable(operation_node)
        elif operation_node.tag == OP_TAG_COMMAND_INOUT:
            self.op_command_inout(operation_node)
        elif operation_node.tag == OP_TAG_WHILE:
            self.op_while(operation_node)
        elif operation_node.tag == OP_TAG_CYCLE:
            self.op_cycle(operation_node)
        elif operation_node.tag == OP_TAG_IF:
            self.op_if(operation_node)
        elif operation_node.tag == OP_TAG_LOG:
            self.op_log(operation_node)
        else:
            raise Exception("Operation tag not recognized: %s" % operation_node.tag)

    def op_write_attribute(self, operation_node):
        # recupero il nome del tango device dal xml
        tango_device_name = operation_node.attrib["tango_device_name"]
        # usa il nome recuperato per cercare in DeviceProxy nel dizionario devices di experiment
        tango_device = None
        if tango_device_name not in self.devices:
            raise Exception("device_name %s not in devices dicionary" % tango_device_name)
        else:
            tango_device = self.devices[tango_device_name]

        # recupero il nome della variabile che contiene il nome dell'attributo tango (stringa
        tango_attr_name = operation_node.attrib["tango_attr_name"]
        tango_attr_value = operation_node.attrib["tango_attr_value"]

        if tango_attr_name.endswith("]"):
            # recupero l'index
            attr_index = int(tango_attr_name[tango_attr_name.index("[") + 1:tango_attr_name.index("]")])
            # recupero in name
            attr_name = tango_attr_name[:tango_attr_name.index("[")]
            attr_to_write = self.variables[attr_name].idata_value[attr_index]

            if tango_attr_value.endswith("]"):
                value_index = int(tango_attr_value[tango_attr_value.index("[") + 1:tango_attr_value.index("]")])
                value_name = tango_attr_value[:tango_attr_value.index("[")]
                # usa il nome recuperato per cercare l'array in ...

                value_to_write = self.variables[value_name].idata_value[value_index]
                tango_device.write_attribute(attr_to_write, int(value_to_write))
            else:
                tango_device.write_attribute(attr_to_write, int(tango_attr_value))
        else:
            if tango_attr_value.endswith("]"):
                value_index = int(tango_attr_value[tango_attr_value.index("[") + 1:tango_attr_value.index("]")])
                value_name = tango_attr_value[:tango_attr_value.index("[")]
                # usa il nome recuperato per cercare l'array in ...

                value_to_write = self.variables[value_name].idata_value[value_index]
                tango_device.write_attribute(tango_attr_name, int(value_to_write))
            else:
                tango_device.write_attribute(tango_attr_name, int(tango_attr_value))

        print("Executing op_write_attribute")

    def op_read_attribute(self, operation_node):
        # recupero il nome del tango device dal xml
        tango_device_name = operation_node.attrib["tango_device_name"]
        # usa il nome recuperato per cercare in DeviceProxy nel dizionario devices di experiment
        tango_device = self.devices[tango_device_name]

        # recupero il nome della variabile che contiene il nome dell'attributo tango (stringa)
        var_attr_name_variable = operation_node.attrib["tango_attr_name"]
        # usa il nome recuperato per cercare in ...
        tango_attr_name = self.variables[var_attr_name_variable].idata_value
        if tango_attr_name.endswith("]"):
            index = int(tango_attr_name[tango_attr_name.index("[") + 1:tango_attr_name.index("]")])

            # recupero il nome della variabile a cui assegnare il valore tornato dalla read_attribute().value()
            name_of_variable_to_write_to = operation_node.attrib["var_name"]

            variable_to_write_to = self.variables[name_of_variable_to_write_to]
            tango_attr_values = tango_device.read_attribute(tango_attr_name).value
            variable_to_write_to.idata_value = tango_attr_values[index]
        else:
            # recupero il nome della variabile a cui assegnare il valore tornato dalla read_attribute().value()
            name_of_variable_to_write_to = operation_node.attrib["var_name"]

            variable_to_write_to = self.variables[name_of_variable_to_write_to]

            variable_to_write_to.idata_value = tango_device.read_attribute(tango_attr_name).value

    def op_command_inout(self, operation_node):

        print("Executing op_command_inout")

        # recupero il nome del tango device dal xml
        tango_device_name = operation_node.attrib["tango_device_name"]
        # usa il nome recuperato per cercare in DeviceProxy nel dizionario devices di experiment
        tango_device = self.devices[tango_device_name]
        command_input = None

        # recupero il nome della variabile che contiene il nome dell'attributo tango (stringa)
        var_attr_name_variable = operation_node.attrib["tango_attr_name"]

        tango_device.command_inout(command_input)


    def op_cycle(self, operation_node):
        print("Executing op_cycle")

        cycle_var_name = operation_node.attrib["var_name"]

        if not operation_node.attrib["cycles"] in self.variables:
            raise Exception("Constant %s not present in experiment dictionary" % operation_node.attrib["cycles"])

        idata_cycles = self.variables[operation_node.attrib["cycles"]]
        if idata_cycles.idata_type == IDATA_TYPE_INT_SCALAR:
            cycle_cycles = idata_cycles.idata_value
        else:
            raise Exception("The type of the variable %s used in cycle is not int" % idata_cycles.idata_name)

        idata_cycle_var = self.variables[cycle_var_name]
        if not cycle_var_name in self.variables:
            raise Exception("Variable %s not in experiment dictionary" % cycle_var_name)

        cycle_step = operation_node.attrib["step"]
        if not cycle_step in self.variables:
            raise Exception("Constant %s not in experiment dictionary" % cycle_step)

        idata_cycle_step = self.variables[cycle_step]

        if (idata_cycle_var.idata_type == IDATA_TYPE_INT_SCALAR and idata_cycle_step.idata_type == IDATA_TYPE_INT_SPECTRUM)  \
            or (idata_cycle_var.idata_type == IDATA_TYPE_FLOAT_SCALAR and idata_cycle_step.idata_type == IDATA_TYPE_FLOAT_SPECTRUM):
            pass
        else:
            print("%s %s" % (idata_cycle_var.idata_type == IDATA_TYPE_FLOAT_SCALAR, idata_cycle_step.idata_type == IDATA_TYPE_FLOAT_SPECTRUM))
            raise Exception("The variable incremented in the cycle %s and the increment %s must be same numerical type"\
                             % (idata_cycle_var.idata_name, idata_cycle_step.idata_name))

        for cnt in range(cycle_cycles):
            for cycle_node in operation_node:
                self.parse_operation(cycle_node)
            self.variables[cycle_var_name].idata_value += self.variables[cycle_step].idata_value

    def op_while(self, operation_node):
        print("Executing op_while")
        var1_name = operation_node.attrib["var1"]
        var2_name = operation_node.attrib["var2"]
        operator_name = operation_node.attrib["operator"]
        var1_idata_value = None
        var2_idata_value = None

        if operator_name not in OPERATORS:
            raise Exception("Invalid assignment for operator_name. Allowed names are: %s" % OPERATORS)

        if "[" in var1_name:
            var1_array_name = var1_name[:var1_name.index("[")]
            index_var1 = int(var1_name[var1_name.index("[")+1:var1_name.index("]")])
            if var1_array_name not in self.variables:
                raise Exception("Variable %s not in Experiment dictionary" % var1_name)
            var1_idata_value = self.variables[var1_array_name].idata_value[index_var1]
        else:
            var1_array_name = var1_name
            if var1_array_name not in self.variables:
                raise Exception("Variable %s not in Experiment dictionary" % var1_name)
            var1_idata_value = self.variables[var1_array_name].idata_value

        if "[" in var2_name:
            var2_array_name = var2_name[:var2_name.index("[")]
            index_var2 = int(var2_name[var2_name.index("[")+1:var2_name.index("]")])
            if var2_array_name not in self.variables:
                raise Exception("Variable %s not in Experiment dictionary" % var2_name)
            var2_idata_value = self.variables[var2_array_name].idata_value[index_var2]
        else:
            var2_array_name = var2_name
            if var2_array_name not in self.variables:
                raise Exception("Variable %s not in Experiment dictionary" % var2_name)
            var2_idata_value = self.variables[var2_array_name].idata_value

        if operator_name == "greater":
            while var1_idata_value > var2_idata_value:
                print("la condizione %s %s %s è verificata" % (var1_name, operator_name, var2_name))
                for op in operation_node:
                    self.parse_operation(op)
        elif operator_name == "lesser":
                while var1_idata_value < var2_idata_value:
                    print("la condizione %s %s %s è verificata" % (var1_name, operator_name, var2_name))
                    for op in operation_node:
                        self.parse_operation(op)
        elif operator_name == "equal":
            while var1_idata_value == var2_idata_value:
                print("la condizione %s %s %s è verificata" % (var1_name, operator_name, var2_name))
                for op in operation_node:
                    self.parse_operation(op)
        elif operator_name == "greaterequal":
            while var1_idata_value >= var2_idata_value:
                print("la condizione %s %s %s è verificata" % (var1_name, operator_name, var2_name))
                for op in operation_node:
                    self.parse_operation(op)
        elif operator_name == "lesserequal":
            while var1_idata_value <= var2_idata_value:
                print("la condizione %s %s %s è verificata" % (var1_name, operator_name, var2_name))
                for op in operation_node:
                    self.parse_operation(op)
        elif operator_name == "notequal":
            while not var1_idata_value == var2_idata_value:
                print("la condizione %s %s %s è verificata" % (var1_name, operator_name, var2_name))
                for op in operation_node:
                    self.parse_operation(op)

    def op_if(self, operation_node):
        print("Executing op_if")
        var1_name = operation_node.attrib["var1"]
        var2_name = operation_node.attrib["var2"]
        operator_name = operation_node.attrib["operator"]
        var1_idata_value = None
        var2_idata_value = None

        if operator_name not in OPERATORS:
            raise Exception("Invalid assignment for operator_name. Allowed names are: %s" % OPERATORS)

        if "[" in var1_name:
            var1_array_name = var1_name[:var1_name.index("[")]
            index_var1 = int(var1_name[var1_name.index("[")+1:var1_name.index("]")])
            if var1_array_name not in self.variables:
                raise Exception("Variable %s not in Experiment dictionary" % var1_name)
            var1_idata_value = self.variables[var1_array_name].idata_value[index_var1]
        else:
            var1_array_name = var1_name
            if var1_array_name not in self.variables:
                raise Exception("Variable %s not in Experiment dictionary" % var1_name)
            var1_idata_value = self.variables[var1_array_name].idata_value

        if "[" in var2_name:
            var2_array_name = var2_name[:var2_name.index("[")]
            index_var2 = int(var2_name[var2_name.index("[")+1:var2_name.index("]")])
            if var2_array_name not in self.variables:
                raise Exception("Variable %s not in Experiment dictionary" % var2_name)
            var2_idata_value = self.variables[var2_array_name].idata_value[index_var2]
        else:
            var2_array_name = var2_name
            if var2_array_name not in self.variables:
                raise Exception("Variable %s not in Experiment dictionary" % var2_name)
            var2_idata_value = self.variables[var2_array_name].idata_value

        if operator_name == "greater":
            if var1_idata_value > var2_idata_value:
                print("la condizione %s %s %s è verificata" % (var1_name, operator_name, var2_name))
                for op in operation_node:
                    self.parse_operation(op)
        elif operator_name == "lesser":
                if var1_idata_value < var2_idata_value:
                    print("la condizione %s %s %s è verificata" % (var1_name, operator_name, var2_name))
                    for op in operation_node:
                        self.parse_operation(op)
        elif operator_name == "equal":
            if var1_idata_value == var2_idata_value:
                print("la condizione %s %s %s è verificata" % (var1_name, operator_name, var2_name))
                for op in operation_node:
                    self.parse_operation(op)
        elif operator_name == "greaterequal":
            if var1_idata_value >= var2_idata_value:
                print("la condizione %s %s %s è verificata" % (var1_name, operator_name, var2_name))
                for op in operation_node:
                    self.parse_operation(op)
        elif operator_name == "lesserequal":
            if var1_idata_value <= var2_idata_value:
                print("la condizione %s %s %s è verificata" % (var1_name, operator_name, var2_name))
                for op in operation_node:
                    self.parse_operation(op)
        elif operator_name == "notequal":
            if not var1_idata_value == var2_idata_value:
                print("la condizione %s %s %s è verificata" % (var1_name, operator_name, var2_name))
                for op in operation_node:
                    self.parse_operation(op)

    def op_log(self, operation_node):

        print("Executing op_log")

        parameter_nodes = operation_node.findall("parameter")
        message = operation_node.attrib["message"]
        parameters = []

        for parameter_node in parameter_nodes:

            var_name = parameter_node.attrib["var"]
            var_idata_value = None

            print("var_name %s" % var_name)

            if "[" in var_name:
                var_array_name = var_name[:var_name.index("[")]
                index_var = int(var_name[var_name.index("[") + 1:var_name.index("]")])

                if var_array_name not in self.variables:
                    raise Exception("Variable %s not in Experiment dictionary" % var_name)

                var_idata_value = self.variables[var_array_name].idata_value[index_var]
            else:
                if var_array_name not in self.variables:
                    raise Exception("Variable %s not in Experiment dictionary" % var_name)

                var_idata_value = self.variables[var_name].idata_value

            print("idata_value %s" % var_idata_value)

            parameters.append(var_idata_value)
            f_message = message.format(*parameters)
            print(f_message)




