#!/usr/bin/env python

from pcbnew import *
import math
import numpy

# References:
# /usr/lib/python3/dist-packages/pcbnew.py
# https://github.com/cooked/kimotor/blob/master/kimotor_action.py

class _TransformMatrix():
    """ Matrix transform to handle translations and rotations"""

    def __init__(self):
        self.reset()

    def reset(self):
        """ Reset the matrix transform """
        self.matrix = [[1,0,0],[0,1,0],[0,0,1]]
        self.states = []
    
    def push(self):
        """ Save the transform state on a stack """
        self.states.append(self.matrix)

    def pop(self):
        """ Restore the last transform state from the stack

        If the stack was empty, reset the transform
        """
        if len(self.states) > 0:
            self.matrix = self.states.pop()
        else:
            self.reset()

    def getAngle(self):
        """ Get the current rotation angle from the transform

        We restrict the transform to translate/rotate only, so angle is well
        defined.
        """
        return -math.degrees(math.acos(self.matrix[0][0]))

    def translate(self,x,y):
        """ Apply a linear transformation

        x: x component of translation vector
        y: y component of translation vector
        """
        m = [[1,0,x],[0,1,y],[0,0,1]]

        self.matrix = numpy.matmul(m,self.matrix)

    def rotate(self,angle):
        """ Apply a rotation

        angle: Rotation angle (degrees)
        """
        r = numpy.radians(angle)
        m = [[math.cos(r), -math.sin(r), 0],
             [math.sin(r), math.cos(r), 0],
             [0, 0, 1]]

        self.matrix = numpy.matmul(m,self.matrix)

    def project(self,x,y):
        """ Apply the transformation to a coordinate

        x: x component of point to transform
        y: y component of point to transform
        returns: x', y' transformed coordinate
        """
        p = [x,y,1]

        result = numpy.matmul(self.matrix,p)
        return float(result[0]),float(result[1])

    def inverse_project(self,x,y):
        """ Apply an inverse transformation to a coordinate

        x: x component of point to transform
        y: y component of point to transform
        returns: x', y' transformed coordinate
        """
        p = [x,y,1]

        inv = numpy.linalg.inv(self.matrix)

        result = numpy.matmul(inv,p)
        return float(result[0]),float(result[1])

class PCB_Painter:
    def __init__(self, pcb=None, libpath=None):
        """ Construct a PCB builder

        pcb: (optional) If specified, work with the given PCB. If not
             specified, start with a blank PCB
        libpath: (optional) Path to the footprint libraries
        """

        if pcb != None:
            self.pcb = pcb
        else:
            self.pcb = CreateEmptyBoard()


        if libpath != None:
            self.library_base = libpath
        else:
            self.library_base = "/usr/share/kicad/footprints/"

        self.transform = _TransformMatrix()
        self.next_designator = 1

    def pushMatrix():
        """ Save the state of the current transformation matrix """
        self.transform.push()

    def popMatrix():
        """ Restore the state of the last transformation matrix """
        self.transform.pop()

    def translate(self, x,y):
        """ Translate all following graphics commands by the given amounts

        x: x translation (mm)
        y: y translation (mm)
        """
        self.transform.translate(x,y)

    def rotate(self,angle):
        """ Rotate all following graphics commands by the given angle

        angle: rotation angle (degrees)
        """

        self.transform.rotate(angle)

    def _localToWorld(self,x,y):
        """ Convert a local coordinate in mm, to a board coordinate """
        return VECTOR2I_MM(*self.transform.project(x,y))

    def _worldToLocal(self,x,y):
        """ Convert a board coordinate, to a local coordinate in mm """
        absolute = ToMM(VECTOR2I(x,y))
        return self.transform.inverse_project(*absolute)

    def getObjectPosition(self, o):
        """ Get a local coordinate for a PCB object

        Can be a pad, footprint, etc

        o: Object to find coordinate for
        """

        return self._worldToLocal(*o.GetPosition())

    def _findNet(self, name):
        """ Find an electical net

        Electrical nets are used to connect conductive parts (tracks, vias,
        zones, fills, pads) together. A typical design will have at least
        ground (gnd), and some form of power rail (5V, 12V, etc).

        This function will return a reference to the net with the given name,
        or if no net with this name exists, it will create one and then return
        a reference to the new net.

        name: Net name (for example: gnd)
        """

        net = self.pcb.FindNet(name)

        if net == None:
            net = NETINFO_ITEM(self.pcb, name)
            self.pcb.Add(net)

        return net
    
    def track(self,x1,y1,x2,y2,layer,net=None,width=0.1):
        """ Place a PCB track
    
        x1,y1: starting point (mm)
        x2,y2: ending point (mm)
        layer: board layer to place track on
        net: (optional) Net to connect track to
        width: (optional) line thickness (mm)
        """
    
        track = PCB_TRACK(self.pcb)
        track.SetWidth(FromMM(width))
        track.SetStart(self._localToWorld(x1,y1))
        track.SetEnd(self._localToWorld(x2,y2))
        track.SetLayer(layer)
        if net != None:
            track.SetNet(self._findNet(net))

        self.pcb.Add(track)
        return track
    
    def via(self,x,y,net=None,d=.3,w=.6):
        """ Place a via
    
        x,y: via coordinate (mm)
        net: net to connect via to
        d: (optional) drill diameter (mm)
        w: (optional) annular ring diameter (mm)
        """
    
        via = PCB_VIA(self.pcb)
        via.SetPosition(self._localToWorld(x,y))
        via.SetDrill(FromMM(d))
        via.SetWidth(FromMM(w))
        if net != None: 
            via.SetNet(self._findNet(net))

        self.pcb.Add(via)
        return via
    
    def polyZone(self,points,layer,net=None):
        """ Place a polygonal zone
    
        Zones can be placed on both copper and non-copper layers
    
        points: List of x,y coordinates that make up the polygon (mm)
        layer: Layer to place zone on
        net: (optional) net to connect zone to.
        """
        v = VECTOR_VECTOR2I([self._localToWorld(point[0],point[1]) for point in points])
    
        zone = ZONE(self.pcb)
        zone.AddPolygon(v)
        zone.SetLayer(layer)
        if net != None:
            zone.SetNet(self._findNet(net))
    
        self.pcb.Add(zone)
        return zone
    
    def rectZone(self,x1,y1,x2,y2,layer,net=None):
        """ Place a rectangular zone
    
        Zones can be placed on both copper and non-copper layers
    
        x1,y1: first corner of rectangle (mm)
        x2,y2: second corner of rectangle (mm)
        layer: Layer to place rectangle on
        net: (optional) net to connect rectangle to
        """
    
        points = [[x1,y1],[x1,y2],[x2,y2],[x2,y1]]
        return self.polyZone(points,layer,net)
   
    def footprint(self,x,y,library,name,reference=None,angle=0,nets=None):
        """ Place a footprint

        Places a footprint from the given library onto the board

        x: x coordinate (mm)
        y: y coordinate (mm)
        library: Library name, relative to the system library path. To change
                 the system library path, edit the 'library_base' variable.
                 For example: 'LED_SMD'
        name: Part name, for example: LED_1210_3225Metric
        reference: (optional) Reference designator to assign to part. For
                   example: LED1. If the reference designator is not
                   specified, a generic one will be assigned.
        angle: (optional) Angle to rotate the part before placement (degrees)
        nets: (optional) List of nets to assign to the footprint pads, in
              order that they are referenced in the part. Caution: Be sure to
              double check that the right nets are assigned! This script knows
              nothing about how the parts are meant to be used and will
              happily make connections that will damage your part.
        """

        #print(FootprintEnumerate(library))

        if reference == None:
            reference = f'P_{self.next_designator}'
            self.next_designator += 1

        footprint = FootprintLoad(self.library_base+library+".pretty", name)
        footprint.SetPosition(self._localToWorld(x,y))
        footprint.SetOrientation(EDA_ANGLE(angle+self.transform.getAngle(), DEGREES_T))
        footprint.SetReference(reference)

        if nets != None:
            if len(nets) != len(footprint.Pads()):
                print(f'Incorrect number of nets provided, expected:{len(nets)} got:{len(footprint.Pads())}')
                exit(1)

            for net, pad in zip(nets, footprint.Pads()):
                pad.SetNet(self._findNet(net))

        self.pcb.Add(footprint)
        return footprint

    def getPads(self,reference):
        """ Get a list of the pads in the specified footprint 
        
        reference: Reference designator to retrieve pads from. For example:
                   LED1
        """

        for footprint in self.pcb.GetFootprints():
            if reference == footprint.GetReference():
                return footprint.Pads()
    
            #for pad in footprint.Pads():
            #    print('pad ', pad.GetName(),
            #          ToMM(pad.GetPosition()),
            #          ToMM(pad.GetOffset()),
            #          pad.GetNet().GetNetname()
            #          )

        return None


    def line(self,x1,y1,x2,y2,layer,width=0.1):
        """ Draw a line from x1,y1 to x2,y2
    
        A line is a graphical object, and can be used to make a board outline
        soldermask, for example, but not to make a conductive track.
    
        x1,y1: starting point (mm)
        x2,y2: eneding point (mm)
        layer: board layer to place line on
        width: (optional) line thickness (mm)
        """
        line = PCB_SHAPE(self.pcb, SHAPE_T_SEGMENT)
        line.SetWidth(FromMM(width))
        line.SetStart(self._localToWorld(x1,y1))
        line.SetEnd(self._localToWorld(x2,y2))
        line.SetLayer(layer)
    
        self.pcb.Add(line)
        return line
    
    def arc(self,x,y,radius,start,end,layer,width=0.1):
        """ Draw an arc
    
        An arc is a graphical object, and can be used to make a board outline
        soldermask, for example, but not to make a conductive track.

        x,y: center of arc (mm)
        radius: arc radius (mm)
        start: starting angle of arc (degrees)
        end: ending angle of arc (degrees)
        layer: board layer
        width: (optional) line thickness (mm)
        """
        start_x = x + radius*math.cos(math.radians(start))
        start_y = y + radius*math.sin(math.radians(start))


        arc = PCB_SHAPE(self.pcb, SHAPE_T_ARC)
        arc.SetWidth(FromMM(width))
        arc.SetCenter(self._localToWorld(x,y))
        arc.SetStart(self._localToWorld(start_x,start_y))
        arc.SetArcAngleAndEnd(EDA_ANGLE(end-start, DEGREES_T))
        arc.SetLayer(layer)
    
        self.pcb.Add(arc)
        return arc
    
    def circle(self,x,y,radius,layer,width=0.1,filled=True):
        """ Draw a circle
    
        A circle is a graphical object, and can be used to make a cutout in a
        soldermask, for example, but not to make a conductive track.
    
        x,y: center of circle (mm)
        radius: radius of circle (mm)
        layer: board layer
        width: (optional) line thickness (mm)
        filled: (optional) If true, fill the circle
        """
        circle = PCB_SHAPE(self.pcb, SHAPE_T_CIRCLE)
        circle.SetCenter(self._localToWorld(x,y))
        # Note: there isn't a SetRadius() function
        circle.SetStart(self._localToWorld(x,y))
        circle.SetEnd(self._localToWorld(x,y+radius))
        circle.SetLayer(layer)
        circle.SetWidth(FromMM(width))
        circle.SetFilled(filled)
    
        self.pcb.Add(circle)
        return circle
   
    def poly(self,points,layer,width=0.1,filled=True):
        """ Draw a polygon
    
        A polygon is a graphical object, and can be used to make a cutout in
        a soldermask, for example, but not to make a conductive track.
       
        points: List of points to add to the polygon (mm)
        layer: Layer to place polygon on
        width: (optional) line thickness (mm)
        filled: (optional) If true, fill the polygon
        """
        v = VECTOR_VECTOR2I([self._localToWorld(point[0],point[1]) for point in points])

        poly = PCB_SHAPE(self.pcb, SHAPE_T_POLY)
        poly.SetPolyPoints(v)
        poly.SetLayer(layer)
        poly.SetWidth(FromMM(width))
        poly.SetFilled(filled)
    
        self.pcb.Add(poly)
        return poly

    def rect(self,x1,y1,x2,y2,layer,width=0.1,filled=True):
        """ Draw a rectangle
    
        A rectangle is a graphical object, and can be used to make a cutout in
        a soldermask, for example, but not to make a conductive track.

        Note: Rectangles are created as polygon objects, so that they can
        support rotation.
        
        x1,y1: first corner of rectangle (mm)
        x2,y2: second corner of rectangle (mm)
        layer: Layer to place rectangle on
        width: (optional) line thickness (mm)
        filled: (optional) If true, fill the rectangle 
        """
    
        points = [[x1,y1],[x1,y2],[x2,y2],[x2,y1]]
        return self.poly(points,layer,width,filled)

    def text(self,x,y,message,layer,mirrored=False,bold=False,italic=False,knockout=False):
        """ Draw text

        Text is is a graphical object, and can be used to make a cutout in
        a soldermask, for example, but not to make a conductive track.

        x: x coordinate to place text (mm)
        y: y coordinate to place text (mm)
        message: Text string to display (single line only)
        layer: Layer to place text on
        """

        text = PCB_TEXT(self.pcb)
        text.SetText(message)
        text.SetTextPos(self._localToWorld(x,y))
        text.SetTextAngle(EDA_ANGLE(self.transform.getAngle(), DEGREES_T))
        text.SetLayer(layer)
        text.SetMirrored(mirrored)
        text.SetBold(bold)
        text.SetItalic(italic)
        text.SetIsKnockout(knockout)

        self.pcb.Add(text)
        return text
