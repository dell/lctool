import pywbem.cim_obj as cobj
import schemas
from schemas import std_xml_namespaces, etree
from stdcli.trace_decorator import traceLog, getLog

# monkeypatch cim_obj because it doesnt use super() and this will screw us up
# also, old __init__ doesnt take *args, **kargs, so we have to manually clean up arg list
def newinit(self, *args, **kargs):
    newkargs = {}
    index = 0
    for argname in ["classname", "properties", "qualifiers", "path", "property_list"]:
        newkargs[argname] = kargs.get(argname)
        if kargs.has_key(argname):
            del(kargs[argname])
        if len(args) > index:
            newkargs[argname] = args[index]
        index = index + 1
    super(cobj.CIMInstance,self).__init__(**kargs)
    self.oldinit(**newkargs)

cobj.CIMInstance.oldinit, cobj.CIMInstance.__init__ = cobj.CIMInstance.__init__, newinit

class WSInstance(cobj.CIMInstance):
    _property_list = {}
    def __init__(self, *args, **kargs):
        print
        print "self.__class__ = %s" % self.__class__
        print "DEBUG: mro() = %s" % self.__class__.mro()
        for cls in self.__class__.mro():
            self.set_class_vals(cls, args, kargs)
        super(WSInstance, self).__init__(*args, **kargs)

    def to_wsxml(self):
        raise NotImplemented("still working on it.")

    def set_class_vals(self, cls, args, kargs):
        kargs["classname"] = kargs.get("classname", cls.__name__)
        kargs["property_list"] = kargs.get("property_list", [])
        kargs["properties"] = kargs.get("properties", {})
        for (i,typ) in getattr(cls, "_property_list", {}).items():
            kargs["property_list"].append(i)
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

class DCIM_FQDD_Mixin(object):
    _property_list  = {"FQDD": "string"}

class Updateable_Mixin(object):
    def generateUpdateXML(self, *args, **kargs):
        # check IsReadOnly first.
        #etree.SubElement(root, "{%s}Target" % ns).text = target
        #etree.SubElement(root, "{%s}AttributeName" % ns).text = attribute_name
        #etree.SubElement(root, "{%s}AttributeValue" % ns).text = attribute_value
        pass

class DCIM_BIOSString(CIM_BIOSString, DCIM_FQDD_Mixin, Updateable_Mixin): pass
class DCIM_BIOSInteger(CIM_BIOSInteger, DCIM_FQDD_Mixin, Updateable_Mixin): pass
class DCIM_BIOSEnumeration(CIM_BIOSEnumeration, DCIM_FQDD_Mixin, Updateable_Mixin): pass

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
    #kargs['namespace'] = namespace
    for child in list(elem):
        attr_ns = child.tag.split("}")[0][1:]
        attr = child.tag.split("}")[1]
        if attr_ns != namespace:
            print "OOPS: attr_ns != namespace"
            continue
        kargs[attr] = child.text

    print
    print "Namespace: %s" % namespace
    print "class map:"
    for k,v in class_map.items():
        print  "\t%s: %s" % (k,v)
    i = class_map.get(namespace, class_map.get("default"))()
    i.update_existing(kargs)
    return i

