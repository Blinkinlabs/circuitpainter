Core concepts
=============

Circuit Painter works by drawing objects onto PCB layers.

PCB layers
----------

There are a lot of layers that make up a PCB! Fortunately, we only need to
focus on a few of them:

* Edge cuts
* Top silkscreen
* Top soldermask
* Top copper
* Bottom copper
* Bottom soldermask
* Bottom silkscreen

In Circuit Painter, you set the active drawing layer by calling the layer()
function:

    .. code:: python

        painter.layer('F_Cu')

Any objects created afterwards will be drawn on that layer, until it is
updated by another layer() call. Note that some objects, particularly the
conductive ones, can only be placed on a copper layer.

Taxonomy of objects
-------------------

Circuit Painter allows you to create two categories of objects- conductive,
and non-conductive. Conductive objects are used to carry electricity, and
are assigned to 'nets'. Non-conductive objects are used for making graphics,
markings, and defining the board outline.


Conductive:

* Tracks
* Arc Tracks
* Polygons
* Footprints
* Vias

Non-Conductive:

* Lines
* Arcs
* Cirles
* Polygons
* Rect
* Text

Object attribues
----------------

Many objects have attributes that need to be set when calling them. For
example, the width of a line or track is set by the width() function.

Global attributes are:

* width
* fill / no fill
* layer
* designators / no designators

Drawing coordinates
-------------------

Circuit Painter features a virtual transformation matrix, to make scripting
similar arrangements of objects anywhere on a board. It supports both linear
and rotational transformations for all objects, allowing for example LEDs to
be aligned around a circle.