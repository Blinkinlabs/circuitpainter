.. Circuit Painter documentation master file, created by
   sphinx-quickstart on Mon Jun 24 12:21:15 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Circuit Painter
===============

.. image:: _static/images/lotus_leds.png
  :width: 400

Circuit painter is a creative coding tool for making functional printed
circuit boards.

Inspired by the simplifed drawing language of Processing, this tool provides
an environment for designing PCBs using basic geometric shapes such as lines,
arcs, and polygons. The tool maintains a drawing 'context' that applies a
translation and rotation matrix to all calls, making it simple to replicate
circuit features at differnt points across a circuit board. Functional PCB
components such as part footprints can also be placed, and connected together
logically using 'nets'.

Circuit painter works as a front end / wrapper for `KiCad's pcbnew <https://www.kicad.org>`_.

For more backgrond on the project, see `Matt's Hackaday Berlin talk <https://www.youtube.com/watch?v=9XV9PSsmMkk>`_ about Circuit painter.

.. toctree::
   :hidden:
   :caption: Introduction

   introduction
   concepts

.. toctree::
   :hidden:
   :caption: Getting Started

   installation
   getting_started
   examples

.. toctree::
   :hidden:
   :caption: Advanced topics

   advanced_usage
   notes
   api

.. toctree::
   :hidden:
   :caption: External links

   Source Code on Github <https://github.com/blinkinlabs/circuitpainter>
   PyPi Project <https://pypi.org/project/circuitpainter/>
   Blinkinlabs <https://blinkinlabs.com>
