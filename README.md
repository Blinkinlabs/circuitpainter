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

# Setup

The library is tested on Ubuntu 22.04, with KiCad 7.0.6 installed from the
official package (https://www.kicad.org/download/), and Python 3.10.7 (the
Ubuntu default)

It should work with any Linux distro,  and might work in Mac/Windows if the
pcbnew library is set up correctly in Python. It should also work with any
recent version of Python 3, but will probably only work with KiCad 7.x as
their API is not stable.

You'll also need the python library 'numpy'.

# Example usage

See the examples directory.

