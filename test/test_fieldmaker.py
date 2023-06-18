from MpApi.fieldmaker import (
    application,
    modules,
    module,
    moduleItem,
    dataField,
    virtualField,
    systemField,
)
from MpApi.fieldmaker import vocabularyReference, repeatableGroup
from MpApi.fieldmaker import UnknownModuleTypeError
from mpapi.module import Module
from lxml import etree
from lxml.etree import _Element
import pytest


def test_app():
    a = application()
    assert a

    doc = a.element
    # print(a.tostring())
    assert isinstance(doc, _Element)

    with pytest.raises(TypeError):
        a.wrap()


def test_modules():
    ms = modules()
    assert ms

    nodes = ms.element
    assert isinstance(nodes, _Element)

    a = ms.wrap()  # module="Object"
    assert a.count_elements() == 2
    # print(a.tostring())


def test_module():
    m = module(name="Object")
    assert m

    nodes = m.element
    assert isinstance(nodes, _Element)

    a = m.wrap()  # module="Object"
    assert a.count_elements() == 3

    with pytest.raises(UnknownModuleTypeError):
        m = module(name="blabla")


def test_moduleItem():
    mi = moduleItem(ID=1234)

    nodes = mi.element
    assert isinstance(nodes, _Element)

    a = mi.wrap(mtype="Object")
    assert a.count_elements() == 4

    # Let's be pythonic, not anal and not test argument types
    # with pytest.raises(TypeError):
    #    mi = moduleItem(ID="1234")
    # print(a.tostring())


def test_dataField():
    df = dataField(name="ObjTechnicalTermClb")
    assert df

    df = dataField(name="ObjTechnicalTermClb", dataType="Clob")
    assert df

    a = df.wrap(mtype="Object", ID=1234)
    assert a.count_elements() == 5

    df = dataField(name="ObjTechnicalTermClb", dataType="Clob", value="Langhalslaute")
    a = df.wrap(mtype="Object", ID=1234)
    assert a.count_elements() == 6
    # print(a.tostring())


def test_virField():
    vf = virtualField(name="ObjObjectArchiveContentVrt")
    assert vf

    a = vf.wrap(mtype="Object", ID=1234)
    assert a.count_elements() == 6
    # print(a.tostring())


def test_systemField():
    sf = systemField(name="__lastModifiedUser")
    assert sf
    sf = systemField(dataType="Varchar", name="__lastModifiedUser")
    assert sf
    sf.wrap(mtype="Object", ID=1234)

def test_vocabularyReference():
    """
    <vocabularyReference name="ObjCategoryVoc" id="30349" instanceName="ObjCategoryVgr">
      <vocabularyReferenceItem id="3206642" name="Musikinstrument">
        <formattedValue language="de">Musikinstrument</formattedValue>
      </vocabularyReferenceItem>
    </vocabularyReference>
    """

    vocRef = vocabularyReference(
        name="ObjCategoryVoc", ID=30349, instanceName="ObjCategoryVgr"
    )
    assert vocRef
    vocRefItem = vocRef.item(ID=3206642, name="Musikinstrument")
    a = vocRef.wrap(mtype="Object", ID=1234)
    assert a.count_elements() == 6
    assert vocRefItem

    vocRef = vocabularyReference(
        name="ObjCategoryVoc", ID=30349, instanceName="ObjCategoryVgr"
    )
    vocRef.item(ID=3206642, name="Musikinstrument", language="de", formattedValue="Musikinstrument")    
    a = vocRef.wrap(mtype="Object", ID=1234)
    assert a.count_elements() == 7

    #print(a.tostring())
    # a.validate()


def test_repeatableGroup():
    """
    <repeatableGroup name="ObjObjectNumberGrp" size="1">
      <repeatableGroupItem id="20774606" uuid="1ee6ad1d-93d1-4e0b-ab74-2176d2f1991d">
        <dataField dataType="Varchar" name="InventarNrSTxt">
          <value>I C 7703</value>
        </dataField>
        <dataField dataType="Varchar" name="ModifiedByTxt">
          <value>EM_ER</value>
        </dataField>
        ...        
        <moduleReference name="InvNumberSchemeRef" targetModule="InventoryNumber" multiplicity="N:1" size="1">
          <moduleReferenceItem moduleItemId="93" uuid="93">
            <formattedValue language="de">EM-Süd- und Südostasien I C</formattedValue>
          </moduleReferenceItem>
        </moduleReference>
      </repeatableGroupItem>
    </repeatableGroup>
    """
    rGrp = repeatableGroup(name="ObjObjectNumberGrp")
    assert rGrp
    
    rgi = rGrp.item(ID=20774606)
    assert rgi
    a = rGrp.wrap(mtype="Object", ID=1234)
    assert a.count_elements() == 6
    rgi.add(dataField(name="InventarNrSTxt", value="I C 7703"))
    rgi2 = rGrp.item()
    rgi2.add(dataField(name="InventarNrSTxt", value="I C 7703"))
    size = rGrp.update_size()
    assert size == 2
    # print(a.tostring())

def test_xpath():
    df = dataField(name="InventarNrSTxt", value="I C 7703")
    a = df.wrap(mtype="Object", ID=1234)
    assert a
    assert a.count_elements() == 6
    assert a.xpath("/application")[0] is not None
    #print(a.tostring())

def test_module():
    df = dataField(name="InventarNrSTxt", value="I C 7703")
    a = df.wrap(mtype="Object", ID=1234)
    a.tofile("debug.xml")
    #print (a.tostring())
    m = Module(file="debug.xml")
    assert m

    m = Module(xml=a.tostring())
    assert m
    
    m = Module(xml="""
        <application xmlns="http://www.zetcom.com/ria/ws/module">
          <modules>
            <module name="Object" totalSize="1">
              <moduleItem hasAttachments="true" id="993084" uuid="993084">
                <systemField dataType="Long" name="__id">
                  <value>993084</value>
                </systemField>
              </moduleItem>
            </module>
          </modules>
        </application>
    """)
    
    assert m
    
    # not clear why this does not work
    # doc = etree.ElementTree(a.element)
    # m = Module(tree=doc)
    # assert m
    
    #print (m)
    #print (f"wrapping inside module: length {len(m)}")
    #assert m
    
    m2 = Module()
    m2.toFile(path="debug2.xml")
    
    
def test_moduleTotalSize():
    df = dataField(name="InventarNrSTxt", value="I C 7703")
    a = df.wrap(mtype="Object", ID=1234)
    print(a.tostring())
    assert a