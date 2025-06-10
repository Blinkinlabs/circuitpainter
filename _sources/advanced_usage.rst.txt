Advanced Usage
==============

The goal of circuitpainter is to make the most common parts of PCB generation
easy, and you might want to do things that this API doesn't directly support.

Note that the underlying pcbnew API is not finished, and will likely be
different between even minor KiCad versions. Using the python help() function
on these object references is a good way to explore their options, though it
gets complicated because they are themselves thin wrappers over the C-language
pcbnew library. Eventually, you'll need to dig through the KiCad source
to figure out how things are supposed to work, and don't forget to check the
bug tracker if things aren't working correctly, because it probably is a bug
and there might be a workaround / fix.

Extended object properties
--------------------------

Circuit painter aims to keep circuit creation simple, but there are extra configuration
settings on many objects that you might want access to. To facilitate this, all
functions that create a PCB object will also return a reference to that object,
so that you can modify it.

For example, create a rectangular zone, and save the reference to it:

    .. code:: python

        p = CircuitPainter()
        p.layer("F_Cu") 
        zone = p.rect_zone(0,0,10,10)

Then, modify the zone properties using the pcbnew api:

    .. code:: python

        zone.SetIsRuleArea(True)
        zone.SetDoNotAllowCopperPour(True)
        zone.SetDoNotAllowVias(False)
        zone.SetDoNotAllowTracks(False)
        zone.SetDoNotAllowPads(False)

Board configuration
-------------------

Many of the board configuration options (stackup, DRC rules, etc) are
stored in the board design settings. For example, to create a 4-layer board
with some different DRC settings:

    .. code:: python
        
        import pcbnew
        settings = p.pcb.GetDesignSettings()
        settings.SetCopperLayerCount(4) # Change to a 4-layer board design
        settings.m_CopperEdgeClearance = pcbnew.FromMM(0.1) # Set the copper-to-edge spacing to 0.1mm

Note that we are importing 'pcbnew' here, in order to use the FromMM() function
to convert a measurement from mm to KiCad's internal units.

Updating boards / adding manual edits
-------------------------------------

Circuit Painter is great for automating parts of designs that are highly repetitive,
but is less effective for more mundane tasks such as wiring up a fancy LED array to
a microcontroller. On this end, everything that CircuitPainter creates is placed into
a single group. When you make manual additions to the board, be sure not to put your
changes into the auto-generated group. Later, if you want to re-generate the automated
portion of your design, you should be able to just delete that group, then start
Circuit Painter by passing it the file name:

    .. code:: python

        p = CircuitPainter('my_file.kicad_pcb')

New objects will then be added to that board, in a new group.

.. autosummary::
   :toctree: generated