#!/usr/bin/env python

import math
import subprocess
import glob
import os
from tempfile import TemporaryDirectory
import pcbnew
from circuitpainter.transform_matrix import TransformMatrix

# References:
# /usr/lib/python3/dist-packages/pcbnew.py
# https://github.com/KiCad/kicad-source-mirror/tree/master/pcbnew
# https://github.com/cooked/kimotor/blob/master/kimotor_action.py


class CircuitPainter:
    # Board layers, from pcbnew
    layers = {
        "F_Cu": pcbnew.F_Cu,
        "In1_Cu": pcbnew.In1_Cu,
        "In2_Cu": pcbnew.In2_Cu,
        "In3_Cu": pcbnew.In3_Cu,
        "In4_Cu": pcbnew.In4_Cu,
        "In5_Cu": pcbnew.In5_Cu,
        "In6_Cu": pcbnew.In6_Cu,
        "In7_Cu": pcbnew.In7_Cu,
        "In8_Cu": pcbnew.In8_Cu,
        "In9_Cu": pcbnew.In9_Cu,
        "In10_Cu": pcbnew.In10_Cu,
        "In11_Cu": pcbnew.In11_Cu,
        "In12_Cu": pcbnew.In12_Cu,
        "In13_Cu": pcbnew.In13_Cu,
        "In14_Cu": pcbnew.In14_Cu,
        "In15_Cu": pcbnew.In15_Cu,
        "In16_Cu": pcbnew.In16_Cu,
        "In17_Cu": pcbnew.In17_Cu,
        "In18_Cu": pcbnew.In18_Cu,
        "In19_Cu": pcbnew.In19_Cu,
        "In20_Cu": pcbnew.In20_Cu,
        "In21_Cu": pcbnew.In21_Cu,
        "In22_Cu": pcbnew.In22_Cu,
        "In23_Cu": pcbnew.In23_Cu,
        "In24_Cu": pcbnew.In24_Cu,
        "In25_Cu": pcbnew.In25_Cu,
        "In26_Cu": pcbnew.In26_Cu,
        "In27_Cu": pcbnew.In27_Cu,
        "In28_Cu": pcbnew.In28_Cu,
        "In29_Cu": pcbnew.In29_Cu,
        "In30_Cu": pcbnew.In30_Cu,
        "B_Cu": pcbnew.B_Cu,
        "B_Adhes": pcbnew.B_Adhes,
        "F_Adhes": pcbnew.F_Adhes,
        "B_Paste": pcbnew.B_Paste,
        "F_Paste": pcbnew.F_Paste,
        "B_SilkS": pcbnew.B_SilkS,
        "F_SilkS": pcbnew.F_SilkS,
        "B_Mask": pcbnew.B_Mask,
        "F_Mask": pcbnew.F_Mask,
        "Dwgs_User": pcbnew.Dwgs_User,
        "Cmts_User": pcbnew.Cmts_User,
        "Eco1_User": pcbnew.Eco1_User,
        "Eco2_User": pcbnew.Eco2_User,
        "Edge_Cuts": pcbnew.Edge_Cuts,
        "Margin": pcbnew.Margin,
        "B_CrtYd": pcbnew.B_CrtYd,
        "F_CrtYd": pcbnew.F_CrtYd,
        "B_Fab": pcbnew.B_Fab,
        "F_Fab": pcbnew.F_Fab,
        "User_1": pcbnew.User_1,
        "User_2": pcbnew.User_2,
        "User_3": pcbnew.User_3,
        "User_4": pcbnew.User_4,
        "User_5": pcbnew.User_5,
        "User_6": pcbnew.User_6,
        "User_7": pcbnew.User_7,
        "User_8": pcbnew.User_8,
        "User_9": pcbnew.User_9,
        "Rescue": pcbnew.Rescue,
    }

    def __init__(
            self,
            filename=None,
            library_path="/usr/share/kicad/footprints"):
        """ Create a Circuit Builder context

        pcb: (optional) If specified, work with the given PCB. If not
             specified, start with a blank PCB
        library_path: (optional) Path to the footprint libraries
        """

        self.tempdir = TemporaryDirectory()

        if filename is not None:
            self.filename = filename
            self.pcb = pcbnew.LoadBoard(filename)
        else:
            # Note: Use NewBoard here because CreateEmptyBoard is buggy, see:
            # https://gitlab.com/kicad/code/kicad/-/issues/15619
            self.filename = f"{self.tempdir.name}/board.kicad_pcb"
            self.pcb = pcbnew.NewBoard(self.filename)

        self.library_path = library_path

        self.transform = TransformMatrix()
        self.next_designators = {}

        # Default draw settings
        self.draw_width = 0.1
        self.draw_layer = "F_Cu"
        self.draw_fill = False
        self.show_reference_designators = True

        # Put all generated items into a group, to make them easier to
        # identify.
        self.group = pcbnew.PCB_GROUP(self.pcb)
        self.pcb.Add(self.group)

        # Keep a list of all components added to the board
        self.uuids = []

        # Workaround for another issue: https://gitlab.com/kicad/code/kicad/-/issues/14901
        # We can only run DRC once, but if any DRC settings are updated with
        # GetDesignSettings(), the magic DRC function has to be run afterwards
        # in order to apply them. So we can't run DRC during init, because
        # it would prevent modifying the design rules. Instead, we run the DRC
        # once before the _fill_zones command is called.
        self.is_drc_run = False

    def width(self, width):
        """ Set the width to use for drawing commands

        Sets the width for objects like lines, tracks, arcs, etc.

        width: Width (mm)
        """
        self.draw_width = width

    def layer(self, layer):
        """ Set the PCB drawing layer

        layer: Layer to use, for example "F_Cu"
        """
        self.draw_layer = layer

    def fill(self):
        """ Enable fills for drawing commands

        Drawing objects such as circles, rectangles, and polygons will have
        their fill property set to true.
        """
        self.draw_fill = True

    def no_fill(self):
        """ Disable fills for drawing commands

        Drawing objects such as circles, rectangles, and polygons will have
        their fill property set to false.
        """
        self.draw_fill = False

    def designators(self):
        """ Enable silkscreen reference designtors for placed footprints """
        self.show_reference_designators = True

    def no_designators(self):
        """ Disable silkscreen reference designtors for placed footprints """
        self.show_reference_designators = False

    def push_matrix(self):
        """ Save the state of the current transformation matrix """
        self.transform.push()

    def pop_matrix(self):
        """ Restore the state of the last transformation matrix """
        self.transform.pop()

    def translate(self, x, y):
        """ Translate all following graphics commands by the given amounts

        x: x translation (mm)
        y: y translation (mm)
        """
        self.transform.translate(x, y)

    def rotate(self, angle):
        """ Rotate all following graphics commands by the given angle

        angle: rotation angle (degrees)
        """

        self.transform.rotate(angle)

    def _local_to_world(self, x, y):
        """ Convert a local coordinate in mm, to a board coordinate """
        xp, yp = self.transform.project(x, y)
        return pcbnew.VECTOR2I_MM(round(xp, 3), round(yp, 3))

    def _world_to_local(self, x, y):
        """ Convert a board coordinate, to a local coordinate in mm """
        absolute = pcbnew.ToMM(pcbnew.VECTOR2I(x, y))
        return self.transform.inverse_project(*absolute)

    def _add_item(self, item):
        """ Add an item to the PCB

        item: Item to add
        """
        self.pcb.Add(item)
        self.group.AddItem(item)
        self.uuids.append(item.m_Uuid)
        return item

    def get_object_position(self, o):
        """ Get a local coordinate for a PCB object

        Can be a pad, footprint, etc

        o: Object to find coordinate for
        """

        return self._world_to_local(*o.GetPosition())

    def _find_net(self, name):
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

        if net is None:
            net = pcbnew.NETINFO_ITEM(self.pcb, name)
            self.pcb.Add(net)

        return net

    def track(self, x1, y1, x2, y2, net=None):
        """ Place a PCB track

        x1,y1: starting point (mm)
        x2,y2: ending point (mm)
        net: (optional) Net to connect track to
        """

        track = pcbnew.PCB_TRACK(self.pcb)
        track.SetWidth(pcbnew.FromMM(self.draw_width))
        track.SetLayer(self.layers[self.draw_layer])
        track.SetStart(self._local_to_world(x1, y1))
        track.SetEnd(self._local_to_world(x2, y2))
        if net is not None:
            track.SetNet(self._find_net(net))

        return self._add_item(track)

    def arc_track(self, x, y, radius, start, end, net=None):
        """ Draw an arc-shaped PCB track

        Note that arc-shaped tracks are a little weirder than normal arcs. The
        DRC engine expects them to be connected at both ends (like a normal
        track), and the PCB Editor considers it a DRC violation to place
        certain objects (like vias) on them.

        x,y: center of arc (mm)
        radius: arc radius (mm)
        start: starting angle of arc (degrees)
        end: ending angle of arc (degrees)
        net: (optional) Net to connect track to
        """
        start_x = x + radius * math.cos(math.radians(start))
        start_y = y + radius * math.sin(math.radians(start))

        mid_angle = (end - start) / 2 + start
        mid_x = x + radius * math.cos(math.radians(mid_angle))
        mid_y = y + radius * math.sin(math.radians(mid_angle))

        end_x = x + radius * math.cos(math.radians(end))
        end_y = y + radius * math.sin(math.radians(end))

        track = pcbnew.PCB_ARC(self.pcb)
        track.SetWidth(pcbnew.FromMM(self.draw_width))
        track.SetLayer(self.layers[self.draw_layer])
        track.SetStart(self._local_to_world(start_x, start_y))
        track.SetMid(self._local_to_world(mid_x, mid_y))
        track.SetEnd(self._local_to_world(end_x, end_y))
        if net is not None:
            track.SetNet(self._find_net(net))

        return self._add_item(track)

    def via(self, x, y, net=None, d=.3, w=.6):
        """ Place a via

        x,y: via coordinate (mm)
        net: net to connect via to
        d: (optional) drill diameter (mm)
        w: (optional) annular ring diameter (mm)
        """

        via = pcbnew.PCB_VIA(self.pcb)
        via.SetPosition(self._local_to_world(x, y))
        via.SetDrill(pcbnew.FromMM(d))
        via.SetWidth(pcbnew.FromMM(w))
        if net is not None:
            via.SetNet(self._find_net(net))

        return self._add_item(via)

    def poly_zone(self, points, net=None):
        """ Place a polygonal zone

        Zones can be placed on both copper and non-copper layers

        points: List of x,y coordinates that make up the polygon (mm)
        net: (optional) net to connect zone to.
        """
        p_world = [self._local_to_world(point[0], point[1]) for point in points]
        v = pcbnew.VECTOR_VECTOR2I(p_world)

        zone = pcbnew.ZONE(self.pcb)
        zone.SetLayer(self.layers[self.draw_layer])
        zone.AddPolygon(v)
        zone.SetIsFilled(True)
        if net is not None:
            zone.SetNet(self._find_net(net))

        return self._add_item(zone)

    def rect_zone(self, x1, y1, x2, y2, net=None):
        """ Place a rectangular zone

        Zones can be placed on both copper and non-copper layers

        x1,y1: first corner of rectangle (mm)
        x2,y2: second corner of rectangle (mm)
        net: (optional) net to connect rectangle to
        """

        points = [[x1, y1], [x1, y2], [x2, y2], [x2, y1]]
        return self.poly_zone(points, net)

    def circle_zone(self, x, y, radius, net=None):
        """ Place a circular zone

        Zones can be placed on both copper and non-copper layers

        Note that the zone is made of a line segments that approximate the
        circle.

        x,y: center of circle (mm)
        radius: radius of circle (mm)
        net: (optional) net to connect rectangle to
        """

        resolution = 0.5  # approximation resolution, in mm

        c = 2 * math.pi * radius
        segments = int(c / resolution)

        angles = [s / segments * 2 * math.pi for s in range(0, segments)]
        points = [[x + radius * math.cos(a),
                   y + radius * math.sin(a)] for a in angles]

        return self.poly_zone(points, net)

    def footprint(
            self,
            x,
            y,
            library,
            name,
            reference='P?',
            angle=0,
            nets=None,
            library_path=None):
        """ Place a footprint

        Places a footprint from the given library onto the board

        x: x coordinate (mm)
        y: y coordinate (mm)
        library: Library name, relative to the system library path. To change
                 the system library path, edit the 'library_path' variable.
                 For example: 'LED_SMD'
        name: Part name, for example: LED_1210_3225Metric
        reference: (optional) Reference designator to assign to part. There
                   are three options:
                   1. If you don't care about the designator, leave this as
                   the default, and the footprints will be assigned sequential
                   reference designators P1, P2, ...
                   2. If you want more conventional naming, specify a leading
                   portion of the designator followed by a question mark
                   (for example: LED?), and the footprints will be assigned
                   sequential reference designators based on their type.
                   3. If you want to assign sequence numbers yourself,
                   specify a designator string that does not end in a question
                   mark (for example: LED3). In this case, the supplied
                   designator will be used without modification.
        angle: (optional) Angle to rotate the part before placement (degrees)
        nets: (optional) List of nets to assign to the footprint pads, in
              order that they are referenced in the part. Caution: Be sure to
              double check that the right nets are assigned! This script knows
              nothing about how the parts are meant to be used and will
              happily make connections that will damage your part.
        """

        if reference.endswith('?'):
            designator = self.next_designators.get(reference, 1)
            self.next_designators[reference] = designator + 1
            reference = f'{reference[:-1]}{designator}'

        if library_path is None:
            library_path = self.library_path

        # TODO: This creates DRC warinings; possibly the footprint needs to be loaded through
        # library that's already linked to the project?
        footprint = pcbnew.FootprintLoad(
            f"{library_path}/{library}.pretty", name)
        if footprint is None:
            raise IOError(
                f"Footprint {name} in library:{library_path}/{library}.pretty not found")

        footprint.SetPosition(self._local_to_world(x, y))
        footprint.SetOrientation(
            pcbnew.EDA_ANGLE(
                angle +
                self.transform.get_angle(),
                pcbnew.DEGREES_T))
        footprint.SetReference(reference)
        footprint.Reference().SetVisible(self.show_reference_designators)

        if nets is not None:
            if len(nets) != len(footprint.Pads()):
                print(
                    f'Incorrect number of nets provided, expected:{len(footprint.Pads())} got:{len(nets)}')
                exit(1)

            for net, pad in zip(nets, footprint.Pads()):
                pad.SetNet(self._find_net(net))

        self._add_item(footprint)

        # Move the footprint to the back side if we are on the B_Cu layer
        # TODO: do this based on the 'side' of the current layer?
        if self.draw_layer == 'B_Cu':
            footprint.SetLayerAndFlip(self.layers['B_Cu'])

        return footprint

    def get_pads(self, reference):
        """ Get a list of the pads in the specified footprint

        reference: Reference designator to retrieve pads from. For example:
                   LED1
        """

        for footprint in self.pcb.GetFootprints():
            if reference == footprint.GetReference():
                return footprint.Pads()

        return None

    def line(self, x1, y1, x2, y2):
        """ Draw a line from x1,y1 to x2,y2

        A line is a graphical object, and can be used to make a board outline
        soldermask, for example, but not to make a conductive track.

        x1,y1: starting point (mm)
        x2,y2: eneding point (mm)
        """
        line = pcbnew.PCB_SHAPE(self.pcb, pcbnew.SHAPE_T_SEGMENT)
        line.SetWidth(pcbnew.FromMM(self.draw_width))
        line.SetLayer(self.layers[self.draw_layer])
        line.SetStart(self._local_to_world(x1, y1))
        line.SetEnd(self._local_to_world(x2, y2))

        return self._add_item(line)

    def arc(self, x, y, radius, start, end):
        """ Draw an arc

        An arc is a graphical object, and can be used to make a board outline
        soldermask, for example, but not to make a conductive track.

        x,y: center of arc (mm)
        radius: arc radius (mm)
        start: starting angle of arc (degrees)
        end: ending angle of arc (degrees)
        """

        start_x = x + radius * math.cos(math.radians(start))
        start_y = y + radius * math.sin(math.radians(start))

        end_x = x + radius * math.cos(math.radians(end))
        end_y = y + radius * math.sin(math.radians(end))

        arc = pcbnew.PCB_SHAPE(self.pcb, pcbnew.SHAPE_T_ARC)
        arc.SetWidth(pcbnew.FromMM(self.draw_width))
        arc.SetLayer(self.layers[self.draw_layer])
        arc.SetCenter(self._local_to_world(x, y))
        arc.SetStart(self._local_to_world(start_x, start_y))
        arc.SetEnd(self._local_to_world(end_x, end_y))

        return self._add_item(arc)

    def circle(self, x, y, radius):
        """ Draw a circle

        A circle is a graphical object, and can be used to make a cutout in a
        soldermask, for example, but not to make a conductive track.

        x,y: center of circle (mm)
        radius: radius of circle (mm)
        """
        circle = pcbnew.PCB_SHAPE(self.pcb, pcbnew.SHAPE_T_CIRCLE)
        circle.SetWidth(pcbnew.FromMM(self.draw_width))
        circle.SetLayer(self.layers[self.draw_layer])
        circle.SetFilled(self.draw_fill)
        circle.SetCenter(self._local_to_world(x, y))
        # Note: there isn't a SetRadius() function
        circle.SetStart(self._local_to_world(x, y))
        circle.SetEnd(self._local_to_world(x, y + radius))

        return self._add_item(circle)

    def poly(self, points):
        """ Draw a polygon

        A polygon is a graphical object, and can be used to make a cutout in
        a soldermask, for example, but not to make a conductive track.

        points: List of points to add to the polygon (mm)
        """
        points_world = [
            self._local_to_world(
                point[0],
                point[1]) for point in points]
        v = pcbnew.VECTOR_VECTOR2I(points_world)

        poly = pcbnew.PCB_SHAPE(self.pcb, pcbnew.SHAPE_T_POLY)
        poly.SetWidth(pcbnew.FromMM(self.draw_width))
        poly.SetLayer(self.layers[self.draw_layer])
        poly.SetFilled(self.draw_fill)
        poly.SetPolyPoints(v)

        return self._add_item(poly)

    def rect(self, x1, y1, x2, y2):
        """ Draw a rectangle

        A rectangle is a graphical object, and can be used to make a cutout in
        a soldermask, for example, but not to make a conductive track.

        Note: Rectangles are created as polygon objects, so that they can
        support rotation.

        x1,y1: first corner of rectangle (mm)
        x2,y2: second corner of rectangle (mm)
        """

        points = [[x1, y1], [x1, y2], [x2, y2], [x2, y1]]
        return self.poly(points)

    def text(
            self,
            x,
            y,
            message,
            angle=0,
            mirrored=False,
            bold=False,
            italic=False,
            knockout=False):
        """ Draw text

        Text is is a graphical object, and can be used to make a cutout in
        a soldermask, for example, but not to make a conductive track.

        x: x coordinate to place text (mm)
        y: y coordinate to place text (mm)
        message: Text string to display (single line only)
        angle: angle to rotate text (degrees)
        mirrored: If true, draw text backwards
        bold: If true, use a bold font
        italic: If true, use an italic font
        knockout: If true, draw the text as a filled rect with the text cut from the rectangle
        """

        text = pcbnew.PCB_TEXT(self.pcb)
        text.SetLayer(self.layers[self.draw_layer])
        text.SetText(message)
        text.SetTextPos(self._local_to_world(x, y))
        text.SetTextAngle(
            pcbnew.EDA_ANGLE(
                self.transform.get_angle() +
                angle,
                pcbnew.DEGREES_T))
        text.SetMirrored(mirrored)
        text.SetBold(bold)
        text.SetItalic(italic)
        text.SetIsKnockout(knockout)

        return self._add_item(text)

    def dimension(self, x1, y1, x2, y2, height):
        """ Draw a linear dimension line

        Dimension lines can be used to document importanat sizes or spacings
        between objects. They aren't needed by a computer to process the
        board files, but are helpful for humans who are inspecting board
        files. Common things that you might want to add dimensions for are
        the bounding box of the PCB edges (to show how big the PCB is), or
        distances between a reference point and mounting holes or test points.

        Dimension lines are usually placed on the 'Dwgs_User' layer.

        x1,y1: starting point (mm)
        x2,y2: eneding point (mm)
        height: Spacing between measured points and dimension line
        """

        dim = pcbnew.PCB_DIM_ALIGNED(self.pcb, pcbnew.PCB_DIM_ALIGNED_T)

        dim.SetStart(self._local_to_world(x1, y1))
        dim.SetEnd(self._local_to_world(x2, y2))
        dim.SetHeight(pcbnew.FromMM(height))

        dim.SetPrecision(pcbnew.DIM_PRECISION_X_XX)
        dim.SetUnits(pcbnew.EDA_UNITS_MILLIMETRES)
        dim.SetUnitsMode(pcbnew.DIM_UNITS_MODE_MILLIMETRES)

        return self._add_item(dim)

    def _fill_zones(self):
        """ Re-pour copper zones on the PCB

        This is performed automatically by the save, preview, drc, and
        export_gerber functions.
        """
        # Workaround to enable some hidden state. Calling WriteDRCReport()
        # fixes something, that then allows the zone_filler to properly apply
        # (at least) board clearance rules.
        if not self.is_drc_run:
            pcbnew.WriteDRCReport(
                self.pcb,
                f"{self.tempdir.name}/.drc",
                pcbnew.EDA_UNITS_MILLIMETRES,
                False)
            self.is_drc_run = True

        # Re-build connectivity, otherwise the zone filler won't connect
        # zones to objects with the same net names
        self.pcb.BuildConnectivity()

        filler = pcbnew.ZONE_FILLER(self.pcb)
        zones = self.pcb.Zones()

        filler.Fill(zones)

    def _auto_set_origin(self):
        # Sets the board origin at the bottom-left hand corner of the pcb
        # edge bounding box. If the edge is not well-defined, it should
        # resolve to no offset.
        boundary = self.pcb.GetBoardEdgesBoundingBox()
        x = boundary.GetX()
        y = boundary.GetY() + boundary.GetHeight()

        settings = self.pcb.GetDesignSettings()
        settings.SetAuxOrigin(pcbnew.VECTOR2I(x, y))

    def save(self, filename):
        """ Save the board design to a KiCad board file

        filename: File name to write to
        """
        self._fill_zones()
        self._auto_set_origin()

        self.pcb.Save(f"{filename}.kicad_pcb")

    def preview(self):
        """ Preview the output file in KiCad

        This saves the file to a temporary loation, then opens it using pcbnew.
        """
        self._fill_zones()
        self._auto_set_origin()

        with TemporaryDirectory() as tmpdir:
            self.save(f"{tmpdir}/preview")
            subprocess.check_call(["pcbnew", f"{tmpdir}/preview.kicad_pcb"])

#    def drc(self, filename):
#        """ Run the DRC tool, and save the output to a file
#
#        filename: Name of DRC file to write
#        """
#        self._fill_zones()
#
#        pcbnew.WriteDRCReport(
#            self.pcb,
#            f"{filename}_drc.txt",
#            pcbnew.EDA_UNITS_MILLIMETRES,
#            False)

    def export_gerber(self, filename, layers=[]):
        """ Export the design to gerbers / drill file

        This saves the file to a temporary loation, uses the kicad command
        line interface to render gerber outputs, and finally places the
        gerbers in a zip file.

        filename: Name of zip file to write to
        """
        self._fill_zones()
        self._auto_set_origin()

        # Map pcbnew layer names to a format recognized by kicad-cli
        # Note that if the layer list is empty, kicad-cli will choose some
        # default set automatically
        layers_csv = ','.join(layers).replace('_', '.')

        with TemporaryDirectory() as tmpdir_kicad, TemporaryDirectory() as tmpdir_gerber:
            # Write the kicad pcb out to a temporary location
            self.save(f"{tmpdir_kicad}/{filename}")

            # Generate gerbers to yet another location
            # TODO: Remove empty layers?
            subprocess.check_call(["kicad-cli",
                                   "pcb",
                                   "export",
                                   "gerbers",
                                   "--use-drill-file-origin",
                                   "-l",
                                   layers_csv,
                                   f"{tmpdir_kicad}/{filename}.kicad_pcb"],
                                  cwd=tmpdir_gerber)
            subprocess.check_call(["kicad-cli",
                                   "pcb",
                                   "export",
                                   "drill",
                                   "--drill-origin",
                                   "plot",
                                   f"{tmpdir_kicad}/{filename}.kicad_pcb"],
                                  cwd=tmpdir_gerber)

            # Don't copy the gbrjob file
            if os.path.exists(f"{tmpdir_gerber}/{filename}-job.gbrjob"):
                os.remove(f"{tmpdir_gerber}/{filename}-job.gbrjob")

            # Zip up the gerbers
            files = glob.glob(f"{tmpdir_gerber}/*")

            subprocess.check_call(
                ["zip",
                 "-j",
                 f"{filename}_gerbers.zip", *files],
                cwd=tmpdir_gerber)

            subprocess.check_call(
                ["cp",
                 f"{tmpdir_gerber}/{filename}_gerbers.zip",
                 "./"])

    def export_svg(self, filename):
        """ Export the design to an SVG

        This saves the file to a temporary loation, uses the kicad command
        line interface to render an svg, then copies it to the specified
        location

        filename: Name of output file
        """
        self._fill_zones()
        self._auto_set_origin()

        with TemporaryDirectory() as tmpdir_kicad:
            # Write the kicad pcb out to a temporary location
            self.save(f"{tmpdir_kicad}/{filename}")

            subprocess.check_call(["kicad-cli",
                                   "pcb",
                                   "export",
                                   "svg",
                                   "--page-size-mode",
                                   "2",
                                   "--exclude-drawing-sheet",
                                   "-l",
                                   ','.join([i.replace('_',
                                                       '.') for i in self.layers.keys()]),
                                   f"{tmpdir_kicad}/{filename}.kicad_pcb"])

    def export_pos(self, filename):
        """ Export a pick-and-place file

        This saves the file to a temporary loation, uses the kicad command
        line interface to render a pnp file, then copies it to the specified
        location

        filename: Name of output file
        """
        self._fill_zones()
        self._auto_set_origin()

        with TemporaryDirectory() as tmpdir_kicad:
            # Write the kicad pcb out to a temporary location
            self.save(f"{tmpdir_kicad}/{filename}")

            subprocess.check_call(["kicad-cli",
                                   "pcb",
                                   "export",
                                   "pos",
                                   "--format","csv",
                                   "--units","mm",
                                   "--bottom-negate-x",
                                   "--use-drill-file-origin",
                                   "--output", f"{filename}_pos.csv",
                                   f"{tmpdir_kicad}/{filename}.kicad_pcb"])
