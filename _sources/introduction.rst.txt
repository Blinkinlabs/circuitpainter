What is Circuit Painter?
========================

Circuit painter is a creative coding tool for making functional printed
circuit boards.

Unlike traditional CAD tools, where you design a PCB by using a GUI to place
parts on a board by hand, in Circuit Painter, you design PCBs by writing code.
You could think of it as similar to how `OpenSCAD <https://openscad.org/>`_
works for 3d modeling, but for PCBs.

Projects that are a good fit for Circuit Painter
------------------------------------------------

* Explore / generative shapes
* Have a lot of simple, repetitive elements (LEDs, test points, mounting
  holes, ...)
* Use things that are very hard to make with traditional CAD- arcs, spirals

See the :doc:`examples` page for a gallery of boards made with Circuit Painter.

Projects that are not a good fit for Circuit Painter
----------------------------------------------------

* Complex, non-repetitive designs such as a microcontroller development board
* Need integration with a traditional workflow

Note that you still can integrate scripted elements into a manually designed
board! For example, Circuit Painter was used to create the spiral track
elements in this `Charlieplexed watch <https://social.v.st/@th/111646753350070002>`_
by Trammell Hudson.

What's under the hood?
----------------------

Circuit painter works as a front end / wrapper for `KiCad's pcbnew <https://www.kicad.org>`_.
It uses the `SWIG bindings <https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/>`_
to create and add objects to a KiCad PCB.