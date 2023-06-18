# MpApi.Fieldmaker - Create zml elements easily

This module's primary purpose is to create zml elements; 

Perhaps this module can also be used to parse existing data. If not, it doesn't
really simplify changing existing data.

In other words: We going for a clean interfaces that reduces the lines of code
-- compared to using pure lxml.

This module replaces the old "from-scratch" interface from MpApi.Module. 

USAGE
    from Fieldmaker import application, modules, module, moduleItem, dataField

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
            