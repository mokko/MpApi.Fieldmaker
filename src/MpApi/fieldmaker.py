"""
Fieldmaker - Create zml elements easily

This module's primary purpose is to create zml elements; 

Perhaps this module can also be used to parse existing data. If not, it doesn't
really simplify changing existing data.

In other words: We going for a clean interfaces that reduces the lines of code
comparative to using pure lxml.

This module replaces the old "from-scratch" interface from MpApi.Module. 

USAGE
    from Fieldmaker import application, modules, module, moduleItem, dataField

    # ATTENTION: Does module conflicts with mpapi.Module? no

    # Constructors are straight forward
    dF = dataField(name="objObjectCategory",value="blabla")

    # Make a tree with "add"
    mi = moduleItem(ID=1234)
    mi.add(dataField(name="objObjectCategory",value="blabla"))
    dF = mi.add(dataField(name="objObjectCategory",value="blabla"))

    # There are shortcuts for frequently used things
    # Dont do this;  Use the method "wrap" instead
    a = application()
    ms = a.add(modules())
    m = ms.add(module(name="Object)
    m.add(moduleItem(ID=1234)
    doc = a.element

    mi = moduleItem(ID=1234)
    a = mi.wrap()
    doc = a.element 

    produces:
    <application xmlns="http://www.zetcom.com/ria/ws/module">
        <modules>
            <module name="Object">
                <moduleItem id="1234"/>
        </modules>
    </application>
            


Methods
- add()   : appends lxml.element at the right place
    mi = moduleItem(ID=1234)
    mi.add(dataField(name="objObjectCategory",value="blabla"))
    dF = mi.add(dataField(name="objObjectCategory",value="blabla"))
- element: returns lxml element or node
    df = mi.add(dataField(name="objObjectCategory",value="blabla"))
    nodes = df.element
- wrap: wraps application, modules, module around moduleItem or 
- wrap: wraps application, modules, module with 
            name=Object, moduleItem with ID 1233
    df = mi.add(dataField(name="objObjectCategory",value="blabla"))
    a = df.wrap(module=Object) 
    doc = a.element
- xpath: xpath with module default namespace 



 # Fieldmaker
 from MpApi.fieldmaker import dataField
 dataFieldN = dataField(value="Schalenhalslaute", name="ObjTechnicalTermClb", dataType="Clob")

 # PURE LXML

 dataFieldN = etree.Element("dataField", name="ObjTechnicalTermClb", dataType="Clob")
 valueN = etree.Element("value")
 valueN.text = "Schalenhalslaute"
 dataFieldN.append(valueN)

 <vocabularyReference name="ObjCategoryVoc" id="30349" instanceName="ObjCategoryVgr">
  <vocabularyReferenceItem id="3206642" name="Musikinstrument">
    <formattedValue language="de">Musikinstrument</formattedValue>
  </vocabularyReferenceItem>
 </vocabularyReference>

 vocRef = vocRef(name="ObjCategoryVoc", id="30349", instanceName="ObjCategoryVgr")
 vocRef.item (id="3206642" name="Musikinstrument")
 
 pure lxml
    
 vocRefN = etree.Element("vocabularyReference", name="ObjCategoryVoc", id="30349" instanceName="ObjCategoryVgr")
 vocRefItemN = etree.Element("vocabularyReferenceItem", id="3206642", name="Musikinstrument")
 fValueN = etree.Element("formattedValue", language="de") 
 fValueN.text("Musikinstrument")

"""
from __future__ import annotations
from lxml.etree import Element
from lxml import etree
from mpapi.client import MpApi
#from mpapi.constants import NSMAP
import pkgutil
from typing import Optional

# NS = "{http://www.zetcom.com/ria/ws/module}"

# as usual I have trouble with namespaces, so I am not using default namespace NSMAP,
# but old skool NSMAP with m prefix
#NSMAP = {None: "http://www.zetcom.com/ria/ws/module"}
NSMAP = {"m": "http://www.zetcom.com/ria/ws/module"} # for xpath we need apparently prefix

known_module_types = ("Object", "Mulimedia")  # TODO: make this configurable
known_dataTypes = ("Boolean", "Clob", "Date", "Long", "Numeric", "Timestamp", "Varchar")


class UnknownModuleTypeError(Exception):
    pass


class UnknownDataTypeError(Exception):
    pass


class baseField:
    def add(self, child: baseField) -> baseField:
        """
        Appends child to object.
        """
        self.element.append(child.element)
        return child

    def count_elements(self) -> int:
        """
        Counts all elements (starting with 1).
        
        I cant figure out why namespace m does not work here.
        """
        return int(self.xpath("count(//*)"))

    def tostring(self) -> str:
        # root = self.element.getroottree()

        xml = etree.tostring(self.element, pretty_print=True, encoding="unicode")
        #xml = xml.encode() 
        return xml

    def wrap(self, *, mtype: str, ID: int) -> application:
        """
        Wrap application, modules, module and moduleItem elements around fields to
        obtain a complete document. Returns an application object object
        Do we need other parameters for moduleItem?

        At the moment we're assuming this is used from a top-level field

        Should we allow module without name? Probably not. So module is required here.
        Then we have different signature for ms.wrap() and m.wrap(module="Object).
        Perhaps that is not so bad since ms.wrap is not encouraged anyways.

        item
        : top-level field
        : rGrp
            :: 2nd level field
        """
        a = application()
        ms = a.add(modules())
        m = ms.add(module(name=mtype))
        mi = m.add(moduleItem(ID=ID))
        mi.add(self)
        m.update_totalSize()
        return a

    def xpath(self, xpath):  # -> something xpath
        # for xpath we apparently need prefix
        NSMAP = {"m": "http://www.zetcom.com/ria/ws/module"} 
        return self.element.xpath(xpath, namespaces=NSMAP)

    #
    # private
    #

    def _check_dataType(self, dataType: str):
        if dataType not in known_dataTypes:
            raise UnknownDataTypeError(f"ERROR: Unknown dataType '{dataType}'")


class application(baseField):
    def __init__(self) -> None:
        NSMAP = {None: "http://www.zetcom.com/ria/ws/module"}
        self.element = etree.Element("application", nsmap=NSMAP)

    def tofile(self, path:str) -> None:
        doc = etree.ElementTree(self.element)
        doc.write(str(path), pretty_print=True, encoding="UTF-8")

    def _update_totalSize(self) -> None:
        """
        OBSOLETE
        This version updates the totalSize for potentially multiple mtypes, so does 
        not return the actual size in a simple int.
        """
        
        mtypeL = self.xpath("/application/modules/module/@name")
        # print (f"GET HERE! {mtypeL}")
        # print (self.tostring())
        for mtype in mtypeL:
            moduleN = self.xpath(f"/application/modules/module[@name = '{mtype}']")[0]
            totalSize = int(self.xpath(f"count(/application/modules/module[@name = '{mtype}']/moduleItem)"))
            # print (f"module item SIZE {totalSize}")
            moduleN.attrib["totalSize"] = str(totalSize)
        print(self.tostring())

    def validate(self):
        # NAMESPACE ISSUES! DOESN'T WORK!
        xsd_str = pkgutil.get_data("mpapi.client", "data/xsd/module_1_6.xsd")
        xsdN = etree.fromstring(xsd_str)
        xmlschema = etree.XMLSchema(xsdN)
        parser = etree.XMLParser(schema=xmlschema)
        xmlschema.assertValid(self.element)  # , nsmap=NSMAP
        return True

    def wrap(self) -> None:
        raise TypeError("ERROR: Don't wrap in application!")


class modules(baseField):
    def __init__(self) -> None:
        self.element = etree.Element("modules", nsmap=NSMAP)

    def wrap(self) -> application:
        a = application()
        a.add(self)
        return a

class module(baseField):
    def __init__(self, *, name: str, totalSize:Optional[int]=None) -> None:
        # we could test for known module types
        if name not in known_module_types:
            raise UnknownModuleTypeError(f"Error: Unknown module type '{name}')")

        moduleN = etree.Element("module", nsmap=NSMAP, name=name)
        if totalSize is not None:
            moduleN.attrib["totalSize"] = totalSize
        self.element = moduleN
        self.mtype=name

    def update_totalSize(self) -> int:
        totalSize = int(self.xpath("count(//module/moduleItem)"))
        #print (f"module.update_totalSize(): {totalSize}")
        self.element.attrib["totalSize"] = str(totalSize)
        #print (self.tostring())
        return totalSize
        
    def wrap(self) -> application:
        a = application()
        m = modules()
        ms = a.add(m)
        ms.add(self)
        a.update_totalSize()
        print (a.tostring())
        return a

class moduleItem(baseField):
    def __init__(
        self,
        *,
        ID: int,
        hasAttachments: Optional[bool] = None,
        uuid: Optional[str] = None,
    ) -> None:
        # we could test for
        moduleItemN = etree.Element("moduleItem", ID=str(ID), nsmap=NSMAP)
        if hasAttachments is not None:
            if hasAttachments:
                moduleItemN.attrib["hasAttachments"] = "true"
            else:
                moduleItemN.attrib["hasAttachments"] = "false"
        if uuid is not None:
            moduleItemN.attrib["uuid"] = uuid
        self.element = moduleItemN

    def wrap(self, *, mtype: str) -> application:
        a = application()
        ms = a.add(modules())
        m = ms.add(module(name=mtype))
        m.add(self)
        #a.update_totalSize()
        return a


#
# simple fields: dataField, virtualField, systemField
#


class dataField(baseField):
    """
    <dataField dataType="Clob" name="ObjTechnicalTermClb">
        <value>Schalenhalslaute</value>
    </dataField>

    USAGE
        from fieldmaker import dataField
        dataField(name="ObjTechnicalTermClb", dataType="Clob", value="Schalenhalslaute")
        dataFieldN = dataField.element()

    DECIDE: Should the dataField produce an empty value element when no value provided? That is
    the current behavior of the virtualField.
    """

    def __init__(
        self,
        *,
        dataType: Optional[str] = None,
        name: Optional[str] = None,
        value: Optional[str] = None,
    ) -> None:
        dataFieldN = etree.Element("dataField", nsmap=NSMAP)
        if name is not None:
            dataFieldN.attrib["name"] = name
        if dataType is not None:
            self._check_dataType(dataType)
            dataFieldN.attrib["dataType"] = dataType
        if value is not None:
            valueN = etree.Element("value", nsmap=NSMAP)
            valueN.text = value
            dataFieldN.append(valueN)
        self.element = dataFieldN


class systemField(baseField):
    """
    <systemField dataType="Varchar" name="__lastModifiedUser">
      <value>EM_SB</value>
    </systemField>

    systemField
    """

    def __init__(
        self,
        *,
        dataType: Optional[str] = None,
        name: Optional[str] = None,
        value: Optional[str] = None,
    ) -> None:
        sysFieldN = etree.Element("systemField", nsmap=NSMAP)
        if name is not None:
            sysFieldN.attrib["name"] = name
        if dataType is not None:
            self._check_dataType(dataType)
            sysFieldN.attrib["dataType"] = dataType
        if value is not None:
            valueN = etree.Element("value", nsmap=NSMAP)
            valueN.text = value
            sysField.append(valueN)
        self.element = sysFieldN


class virtualField(baseField):
    """
    It seems like a general bad idea to make virtualFields, but if the user really wants
    why do we want to stay in his/her way.

    <virtualField name="ObjUuidVrt">
      <value>993084</value>
    </virtualField>
    """

    def __init__(self, *, name: Optional[str] = None, value: Optional[str] = None):
        virFieldN = etree.Element("virtualField", nsmap=NSMAP)
        if name is not None:
            virFieldN.attrib["name"] = name

        # virtualFields without a value seem to have an empty value element
        valueN = etree.Element("value")
        virFieldN.append(valueN)
        if value is not None:
            valueN.text = value
        self.element = virFieldN


"""
COMPLEX FIELDS
- vocRef
- vocRefItem
- rGrp
- rGrpItem
"""


class moduleReference(baseField):
    """
    <moduleReference name="InvNumberSchemeRef" targetModule="InventoryNumber" multiplicity="N:1" size="1">
      <moduleReferenceItem moduleItemId="93" uuid="93">
        <formattedValue language="de">EM-Süd- und Südostasien I C</formattedValue>
      </moduleReferenceItem>
    </moduleReference>
    """

    def __init__(
        self,
        *,
        name: str = None,
        targetModule: Optional[str] = None,
        multiciplicity: Optional[str] = None,
        size: Optional[int] = None,
    ) -> None:

        modRefN = etree.Element("moduleReference", nsmap=NSMAP)
        sysFieldN.attrib["name"] = name
        if targetModule is not None:
            modRefN.attrib["targetModule"] = targetModule
        if multiplicity is not None:
            modRefN.attrib["multiciplicity"] = multiciplicity
        if size is not None:
            modRefN.attrib["size"] = size
        self.element = modRefN

    def item(
        moduleItemId: int,
        language: str,
        uuid=Optional[int],
        formattedValue: Optional[str] = None,
    ):
        itemN = etree.Element(NS + "moduleReferenceItem")
        modRefN.attrib["moduleItemId"] = str(moduleItemId)
        self.element.append(itemN)

        if formattedValue is not None:
            fvalueN = etree.Element("moduleReferenceItem", nsmap=NSMAP)
            fvalueN.text = formattedValue
            fvalueN.attrib["language"] = language
            itemN.append(fvalueN)


class vocabularyReference(baseField):
    """
    Can I assume that vocRef always has only one item? Then we could prohibit multiple 
    items.

    <vocabularyReference name="ObjPublicationStatusVoc" id="30432" instanceName="ObjPublicationStatusVgr">
      <vocabularyReferenceItem id="4399323" name="vorhanden">
        <formattedValue language="de">vorhanden</formattedValue>
      </vocabularyReferenceItem>
    </vocabularyReference>
    """

    def __init__(
        self, *, name: str, ID: Optional[int] = None, instanceName: Optional[str] = None
    ):

        vocRefN = etree.Element("vocabularyReference", nsmap=NSMAP, name=name)
        if ID is not None:
            vocRefN.attrib["id"] = str(ID)
        if instanceName is not None:
            vocRefN.attrib["instanceName"] = instanceName
        self.element = vocRefN

    def item(
        self,
        *,
        ID: Optional[int] = None,
        name: Optional[str] = None,
        language: Optional[str] = None,
        formattedValue: Optional[str] = None,
    ):
        vocRefItem = vocabularyReferenceItem(ID=ID, name=name, formattedValue=formattedValue)
        self.add(vocRefItem)
        return vocRefItem


class vocabularyReferenceItem(baseField): 
    def __init__(self, *, 
        ID:int, 
        name: Optional[str] = None, 
        language: Optional[str] = None,
        formattedValue: Optional[str] = None,
    )  -> None:
        vocRefItemN = etree.Element("vocabularyReferenceItem", nsmap=NSMAP, id=str(ID))
        if name is not None:
            vocRefItemN.attrib["name"] = name
    
        if formattedValue is not None:
            fValueN = etree.Element("formattedValue", nsmap=NSMAP)
            fValueN.text = formattedValue
            if language is not None:
                fValueN.attrib["language"] = language
            vocRefItemN.append(fValueN)

        self.element = vocRefItemN

class repeatableGroup(baseField):
    """
    <repeatableGroup name="ObjObjectTitleGrp" size="3">
      <repeatableGroupItem id="26502225" uuid="1e565113-eff1-4787-aed0-ecad56bc6b36">
        <dataField dataType="Long" name="SortLnu">
          <value>1</value>
          <formattedValue language="de">1</formattedValue>
        </dataField>
        <dataField dataType="Varchar" name="TitleTxt">
          <value>tritantri vina</value>
        </dataField>
        <dataField dataType="Date" name="ModifiedDateDat">
          <value>2013-08-14</value>
          <formattedValue language="de">14.08.2013</formattedValue>
        </dataField>
        <dataField dataType="Varchar" name="ModifiedByTxt">
          <value>EM_AR</value>
        </dataField>
        <vocabularyReference name="TypeVoc" id="30450" instanceName="ObjTitleTypeVgr">
          <vocabularyReferenceItem id="4398935" name="Originaltitel">
            <formattedValue language="de">Originaltitel</formattedValue>
          </vocabularyReferenceItem>
        </vocabularyReference>
      </repeatableGroupItem>
      ...
    </repeatableGroup>
    """

    def __init__(self, *, name, instanceName: Optional[str] = None, size: Optional[int] = None) -> None:
        rGrpN = etree.Element("repeatableGroup", name=name, nsmap=NSMAP)
        if size is not None:
            rGrpN.attrib["size"] = str(size)
        if instanceName is not None:
            rGrpN.attrib["instanceName"] = instanceName
        self.element = rGrpN

    def item(self, *, ID: Optional[int] = None, uuid: Optional[str] = None):
        """
        <repeatableGroupItem id="26502225" uuid="1e565113-eff1-4787-aed0-ecad56bc6b36">
        """
        rGrpItem = repeatableGroupItem(ID=ID, uuid=uuid)
        #itemN = etree.Element("vocabularyReferenceItem", nsmap=NSMAP)
        self.add(rGrpItem)
        return rGrpItem  

    def update_size(self) -> int:
        """
        set size programmatically according to current number of items
        TODO: test this
        Normal use:
            rGrp.update_size()
        You can get size as well
            size = rGrp.update_size()
        """
        actual_size = int(self.xpath("count(//repeatableGroup/repeatableGroupItem)"))
        #print (f"SIZE {actual_size}")
        rGrpN = self.xpath("//repeatableGroup")[0]
        rGrpN.attrib["size"] = str(actual_size)
        #print(self.tostring())
        return actual_size


class repeatableGroupItem(baseField): 
    def __init__(self, *, ID:Optional[int]=None, uuid: Optional[str] = None) -> None:
        rGrpItem = etree.Element("repeatableGroupItem", nsmap=NSMAP)
        
        if ID is not None:
            rGrpItem.attrib["id"] = str(ID)
        if uuid is not None:
            rGrpItem.attrib["uuid"] = uuid
        self.element = rGrpItem
