import pywbem.cim_obj as cobj
import schemas
from schemas import std_xml_namespaces, etree
from stdcli.trace_decorator import traceLog, getLog
import lcctool

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

# Outline:
#  The idea with this module is that we should be able to use the python pywbem
# module to save ourselves a lot of work. Unfortunately, the schema for WSMAN
# CIM objects is completely different from WBEM CIM objects, even though they
# use the same underlying class layout.
#
# So, this module does impedance maching... it reads WSMAN XML schemas and
# creates PYWBEM objects. It also has helper methods for serializing to INI, as
# well as a class layout to let you specify the properties of a specific CIM
# class. (Eventually we should be able to read MOF files to get the class
# layout instead of manually specifying them. Manual specification is sort of a
# hack to get everything up and running quickly.)
#


class WSInstance(cobj.CIMInstance):
    def __init__(self, wsman=None, *args, **kargs):
        self.wsman=wsman
        # look up all the classes in our inheritance heirarchy and add the
        # property_list parameters
        for cls in self.__class__.mro():
            self.set_class_vals(cls, args, kargs)
        cobj.CIMInstance.__init__(self, *args, **kargs)

    # set up property_list parameter based on class _property_list attribute
    def set_class_vals(self, cls, args, kargs):
        kargs["classname"] = kargs.get("classname", cls.__name__)
        for (i,typ) in getattr(cls, "_property_list", {}).items():
            # next line may look loop invariant, but we dont want to add a
            # property_list karg unless a class has a _property_list, so we can
            # only do it in the loop
            kargs["property_list"] = kargs.get("property_list", [])
            kargs["property_list"].append(i)

            # dont add 'properties' karg unless we absolutely need it
            kargs["properties"] = kargs.get("properties", {})
            # if no property present, add an empty none-type version
            if not kargs["properties"].has_key(i):
                kargs["properties"][i] = cobj.CIMProperty(i, None, type=typ)


    # this should really use CIMArgument, et al.
    @traceLog()
    def call_method(self, uri, schema, method, *args, **kargs):
        return lcctool.call_method(self.wsman, uri, schema, method, *args, **kargs)


# Dell-specfic mixin class that implements some standard methods that are
# useful for setting bios/nic/drac/raid settings. Also, all the dell classes
# have the "FQDD" property.
class DCIM_Mixin(object):
    _property_list  = {"FQDD": "string"}

    @traceLog()
    def get_service_uri(self):
        # cache the uri
        if not self.associated_service_class.get("uri", None):
            self.associated_service_class["uri"] = lcctool.get_service_uri(self.wsman, self.associated_service_class["name"]._ns)
        method = self.associated_service_class["set_method"]
        multi_method = self.associated_service_class["multi_set_method"]
        uri = self.associated_service_class["uri"]
        return {'uri': uri, 'ns': self.associated_service_class["name"]._ns, 'set_method': method, 'multi_set_method': multi_method}

    @traceLog()
    def get_name(self):
        name = self["attributename"]
        if self.has_key("groupid") and self["groupid"]:
            name = self["groupid"] + "#" + name
        return name

    @traceLog()
    def deserialize_ini(self, ini):
        retval = False
        if ini.has_section(self["fqdd"]) and ini.has_option(self["fqdd"], self.get_name()):
            newval = ini.get(self["fqdd"], self.get_name())
            if newval != self["currentvalue"]:
                moduleVerboseLog.debug("setPending: [%s] %s = %s" % (self["fqdd"], self.get_name(), newval))
                self.update_existing({'PendingValue': newval})
                retval = True
            else:
                moduleVerboseLog.debug("Option has not changed: [%s] %s" % (self["fqdd"], self.get_name()))
        else:
            moduleVerboseLog.debug("could not find new section/option: [%s] %s" % (self["fqdd"], self.get_name()))

        return retval

    @traceLog()
    def serialize_ini(self, ini):
        name = self.get_name()
        for sec in ("main", self["fqdd"]):
            if not ini.has_section(sec):
                ini.add_section(sec)

        if self.has_key("isreadonly") and self["isreadonly"].lower() == "true":
            name = "#readonly#  %s" % name

        value = self["currentvalue"]
        if value is None:
            value = ''

        ini.set(self["fqdd"], name, value)


@traceLog()
def cim_instance_from_wsxml(wsman, elem):
    namespace = elem.tag.split("}")[0][1:]
    cls = elem.tag.split("}")[1]
    kargs = {}
    for child in list(elem):
        attr_ns = child.tag.split("}")[0][1:]
        attr = child.tag.split("}")[1]
        if attr_ns != namespace:
            continue
        kargs[attr] = child.text

    i = find_class(namespace, cls)(classname=cls, wsman=wsman)
    i.update_existing(kargs)
    i.raw_xml_str = etree.tostring(elem)
    i.raw_xml_elem = elem
    return i

class ClassNotFound(Exception): pass

@traceLog()
def find_class(namespace, classname=None):
    for cls in itersubclasses(WSInstance):
        if getattr(cls, "_ns", None) == namespace:
            if classname is None or cls.__name__ == classname:
                return cls

    raise ClassNotFound("Could not find match for class: %s in namespace %s" % (classname, namespace))
    #return WSInstance

## helper function to iterate subclasses
@traceLog()
def itersubclasses(cls, _seen=None):
    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with new-style classes, not %.100r' % cls)
    if _seen is None: _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError: # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub

import wscim_classes
