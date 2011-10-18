import pywbem.cim_obj as cobj
import schemas
from schemas import std_xml_namespaces
from stdcli.trace_decorator import traceLog, getLog


class WSInstance(cobj.CIMInstance):
    def __init__(self, *args, **kargs):
        print "WSInstance.__init__(%s, %s)" % (args, kargs)
        print "WSInstance.__class__.mro() = %s" % self.__class__.mro()
        for cls in self.__class__.mro():
            self.set_class_vals(cls, args, kargs)
        super(WSInstance, self).__init__(*args, **kargs)

    def to_wsxml(self):
        raise NotImplemented("still working on it.")

    def set_class_vals(self, cls, args, kargs):
        kargs["classname"] = kargs.get("classname", cls.__name__)
        for (i,typ) in getattr(cls, "_property_list", {}).items():
            # next line may look loop invariant, but we dont want to add a property_list karg unless a 
            # class has a _property_list
            kargs["property_list"] = kargs.get("property_list", [])
            kargs["property_list"].append(i)

            # dont add 'properties' karg unless we absolutely need it
            kargs["properties"] = kargs.get("properties", {})
            # if no property present, add an empty none-type version
            if not kargs["properties"].has_key(i):
                kargs["properties"][i] = cobj.CIMProperty(i, None, type=typ)
            

class CIM_ManagedElement(WSInstance):
    _property_list  = {"InstanceID": "string", "Caption": "string", "Description": "string", "ElementName": "string"}

class CIM_BIOSAttribute(CIM_ManagedElement):
    _property_list  = {"AttributeName": "string", "CurrentValue": "string", "PendingValue": "string", "IsOrderedList": "string", "IsReadOnly": "string", "DefaultValue": "string"}

class CIM_BIOSEnumeration(CIM_BIOSAttribute):
    _property_list  = {"PossibleValues":"string", "PossibleValuesDescription": "string"}

class CIM_BIOSString(CIM_BIOSAttribute):
    _property_list  = {"StringType": "uint32", "MinLength": "uint64", "MaxLength": "uint64", "ValueExpression": "string",}

class CIM_BIOSInteger(CIM_BIOSAttribute):
    _property_list  = {"LowerBound": "uint64", "UpperBound": "uint64", "ProgrammaticUnit": "string", "ScalarIncrement": "uint32"}

class DCIM_Mixin(object):
    _property_list  = {"FQDD": "string"}

    def serialize_ini(self, ini):
        name = self["attributename"]
        if self.has_key("groupid") and self["groupid"]:
            name = self["groupid"] + "#" + name

        for sec in ("main", self["fqdd"]):
            if not ini.has_section(sec):
                ini.add_section(sec)
        ini.set(self["fqdd"], name, self["currentvalue"])
        ini.set("main", self["fqdd"], 'subsys')

    def generateUpdateXML(self, *args, **kargs):
        # check IsReadOnly first.
        #etree.SubElement(root, "{%s}Target" % ns).text = target
        #etree.SubElement(root, "{%s}AttributeName" % ns).text = attribute_name
        #etree.SubElement(root, "{%s}AttributeValue" % ns).text = attribute_value
        pass

class DCIM_BIOSString(CIM_BIOSString, DCIM_Mixin): pass
class DCIM_BIOSInteger(CIM_BIOSInteger, DCIM_Mixin): pass
class DCIM_BIOSEnumeration(CIM_BIOSEnumeration, DCIM_Mixin): pass

class_map = {  
        std_xml_namespaces['bios_enum']: DCIM_BIOSEnumeration, 
        std_xml_namespaces['bios_str']: DCIM_BIOSString, 
        std_xml_namespaces['bios_int']: DCIM_BIOSInteger, 
        'default': CIM_BIOSAttribute,
    }

def attributes_from_xml_factory(item_list, subsys=None):
    for elem in list(item_list):
        yield single_attribute_from_xml_factory(elem, subsys)

def single_attribute_from_xml_factory(elem, subsys=None):
    namespace = elem.tag.split("}")[0][1:]
    cls = elem.tag.split("}")[1]
    kargs = {}
    for child in list(elem):
        attr_ns = child.tag.split("}")[0][1:]
        attr = child.tag.split("}")[1]
        if attr_ns != namespace:
            continue
        kargs[attr] = child.text

    i = class_map.get(namespace, class_map.get("default"))()
    i.update_existing(kargs)
    return i




# monkeypatch cim_obj because it doesnt use super() and this will screw us up
# also, old __init__ doesnt take *args, **kargs, so we have to manually clean up arg list
def newinit(self, *args, **kargs):
    newkargs = {}
    index = 0
    # remove all the args that we consume from kargs
    for argname in ["classname", "properties", "qualifiers", "path", "property_list"]:
        newkargs[argname] = kargs.get(argname)
        if kargs.has_key(argname):
            del(kargs[argname])
        if len(args) > index:
            newkargs[argname] = args[index]
        index = index + 1
    super(cobj.CIMInstance,self).__init__(**kargs)
    self.oldinit(**newkargs)

def CIMProperty_towsxml(self):
    if self.is_array:
        value = self.value
        if value is not None:
            if value:
                if self.embedded_object is not None:
                    value = [v.tocimxml().toxml() for v in value]
            value = VALUE_ARRAY([VALUE(atomic_to_cim_xml(v)) for v in value])

        return PROPERTY_ARRAY(
            self.name,
            self.type,
            value,
            self.array_size,
            self.class_origin,
            self.propagated,
            qualifiers = [q.tocimxml() for q in self.qualifiers.values()],
            embedded_object = self.embedded_object)

    elif self.type == 'reference':

        value_reference = None
        if self.value is not None:
            value_reference = VALUE_REFERENCE(self.value.tocimxml())

        return PROPERTY_REFERENCE(
            self.name,
            value_reference,
            reference_class = self.reference_class,
            class_origin = self.class_origin,
            propagated = self.propagated,
            qualifiers = [q.tocimxml() for q in self.qualifiers.values()])

    else:
        value = self.value
        if value is not None:
            if self.embedded_object is not None:
                value = value.tocimxml().toxml()
            else:
                value = atomic_to_cim_xml(value)
            value = VALUE(value)

        return PROPERTY(
            self.name,
            self.type,
            value,
            class_origin = self.class_origin,
            propagated = self.propagated,
            qualifiers = [q.tocimxml() for q in self.qualifiers.values()],
            embedded_object = self.embedded_object)


    pass

if not hasattr(cobj.CIMInstance, "oldinit"):
    # monkey-patch CIMInstance to fix __init__ method
    cobj.CIMInstance.oldinit  = cobj.CIMInstance.__init__
    cobj.CIMInstance.__init__  = newinit

    # monkey patch our towsxml methods


