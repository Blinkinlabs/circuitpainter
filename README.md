# Circuit Painter

Circuit painter is a creative coding tool for making functional printed
circuit boards.

Inspired by the simplifed drawing language of Processing, this tool provides
an environment for drawing basic geometric shapes such as lines, arcs, and
polygons onto a PCB. The tool maintains a drawing 'context' that applies a
translation and rotation matrix to all calls, making it simple to replicate
circuit features at differnt points across a circuit board. Functional PCB
components such as part footprints can also be placed, and connected together
logically using 'nets'.

Circuit painter works as a front end / wrapper for KiCad's pcbnew.

# Installation

Release versions are available on PyPi:

    pip install circuitpainter

In addition to the python library, you'll also need KiCad 7.x. The library is
tested on Ubuntu 22.04, with KiCad 7.0.6 installed from theofficial package
(https://www.kicad.org/download/), and Python 3.10.7 (the Ubuntu default).

It should work with any Linux distro,  and might work in Mac/Windows if the
pcbnew library is set up correctly in Python. It should also work with any
recent version of Python 3, but will probably only work with KiCad 7.0.6 or
higher as their API is not stable.

# Example usage

Start by creating a drawing context:

	from circuitpainter import CircuitPainter
	painter = CircuitPainter()

Using the painter object, you can draw non-conductive and conductve shapes,
footprints, and text onto the PCB.

First, set the layer to place the object on (tip: use
print(painter.layers.keys()) to show all available layers):

	painter.set_layer('F_SilkS')

Next, draw some non-conductive objects:

	painter.circle(0,0,3) # Draw a circle with radius 3 at the board origin
	painter.line(0,0,10,0) # Draw a line from the board origin to (10,10)
	painter.circle(10,10,3) # Draw a circle with raidus 3 at position (10,10)

To change the width of lines, use the width() command:

	painter.width(0.5)
	painter.line(0,0,10,0) # line with width 0.5mm
	painter.width(1)
	painter.line(0,5,10,5) # line with width 1mm
	painter.width(2)
	painter.line(0,10,10,10) # line with width 2mm

You can change where and at what angle features are added, by using the
translate() and rotate() features:

	painter.translate(10,10)
	painter.rotate(30)
	painter.rect(-5,-5,5,5) # Rectangle is drawn at a 30 degreen angle, centered at (10,10).

Calling them multiple times will stack the transformations (they are
calculated as a 2d transformation matrix)

	painter.translate(10,10)
	painter.rect(-5,-5,5,5) # Rectangle is drawn centered at (10,10).
	painter.translate(10,10)
	painter.rect(-5,-5,5,5) # Rectangle is drawn centered at (20,20).
	painter.translate(10,10)
	painter.rect(-5,-5,5,5) # Rectangle is drawn centered at (30,30).

Saving and restoring the applied tranformation is done using push_matrix()
and pop_matrix(). (Note: This is implemented as a stack, and multiple pushes can be nested):

	painter.push_matrix() # Save the current transformation settings
	painter.translate(10,10)
	painter.rotate(30)
	painter.rect(-5,-5,5,5) # Rectangle is drawn at a 30 degreen angle, centered at (10,10).
	painter.pop_matrix() # Restore previous transformation settigns
	painter.rect(-5,-5,5,5) # Rectangle is drawn centered at (10,10).


For more complete examples, see the scripts in the examples directory.

# Advanced usage

The goal of circuitpainter is to make the most common parts of PCB generation
easy, and you might want to do things that this API doesn't directly support.
To facilitate this, all functions that create a PCB object will also return
a reference to that object, so that you can modify it.

For example, create a rectangular zone, and save the reference to it:

    painter.layer("F_Cu") 
    zone = painter.rect_zone(0,0,10,10)

Then, modify the zone properties using the pcbnew api:


    zone.SetIsRuleArea(True)
    zone.SetDoNotAllowCopperPour(True)
    zone.SetDoNotAllowVias(False)
    zone.SetDoNotAllowTracks(False)
    zone.SetDoNotAllowPads(False)

Note that the API is not finished, and will likely be different between even
minor KiCad versions. Using the python help() function on these object
references is a good way to explore their options, though it gets complicated
because they are themselves thin wrappers over the C-language pcbnew library.

A second tip is that many of the board configuration options (stackup, DRC
rules, etc) are stored in the board design settings, and that there are some
good convenience functions available in pcbnew that you might need if you
are interacting with them directly. For example, to create a 4-layer board
with some different DRC settings:

    import pcbnew
    settings = painter.pcb.GetDesignSettings()
    settings.SetCopperLayerCount(4) # Change to a 4-layer board design
    settings.m_CopperEdgeClearance = pcbnew.FromMM(0.1) # Set the copper-to-edge spacing to 0.1mm

Using the help() function is valuable here, along with combing through the
KiCad source code.

# Credits

CircuitPainter is a simplified interface for KiCad's
[PcbNew](https://www.kicad.org/discover/pcb-design/) library. Their library
does all of the heavy lifting in actually making the PCBs.

CircuitPainter was written by [Matthew Mets](https://github.com/cibomahto)
