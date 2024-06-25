from circuitpainter import CircuitPainter
from argparse import ArgumentParser
import math

def UntentedVia(painter,x,y,d,w):
    painter.layer('F_Cu')
    painter.via(x,y,d=d,w=w)

    painter.fill()
    # By default, vias are tented (covered). Draw circlular openings
    # in the soldermask layers to make them untented, instead of
    # changing the board-level setting.
    painter.layer('F_Mask')
    painter.circle(x,y,w/2)
    painter.layer('B_Mask')
    painter.circle(x,y,w/2)

def HexPerfboard(count,spacing,hole_d,ring_d):
    painter = CircuitPainter()

    # Make the board shape
    painter.layer("Edge_Cuts")

    edge_points = []

    # Save a list of edge points, in world coordinates
    # Note this is a good use case for an absolute points class
    for rotation in range(0,361,60):
        painter.push_matrix()
        painter.rotate(rotation)
        edge_points.append(painter._local_to_world((count+1)*spacing,0))
        painter.pop_matrix()

    for a,b in zip(edge_points[:-1],edge_points[1:]):
        painter.line(*painter._world_to_local(*a), *painter._world_to_local(*b))

    painter.width(0.05)
    painter.fill()

    # Center via
    UntentedVia(painter,0,0,hole_d,ring_d)

    # Draw the hex grid, 1/6th at a time:
    for rotation in range(0,360,60):
        painter.push_matrix();
        painter.rotate(rotation)
        painter.translate(spacing,0)
        for y in range(0, count):
            for x in range(0,count-y):
                UntentedVia(painter, x*spacing,0,hole_d,ring_d)

            painter.translate(spacing*math.cos(math.radians(60)),-spacing*math.sin(math.radians(60)))

        painter.pop_matrix();



    return painter

if __name__ == "__main__":
    parser = ArgumentParser(description="hexagonal perfboard generator")
    parser.add_argument('-c',type=int,default=9, help="Number of hex rings")
    parser.add_argument('-s','--spacing',type=float,default=2.54, help="Spacing between the holes (mm)")
    parser.add_argument('-d','--hole_diameter',type=float,default=1.02, help="Hole diameter (mm)")
    parser.add_argument('-r','--ring_diameter',type=float,default=2, help="Ring diameter (mm)")
    parser.add_argument('--save',action="store_true",help="Save the design to a KiCad file")
    args = parser.parse_args()

    painter = HexPerfboard(args.c, args.spacing, args.hole_diameter,args.ring_diameter)
    if args.save:
        painter.export_gerber('hex_perfboard')
    else:
        painter.preview()
