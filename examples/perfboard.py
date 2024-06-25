from circuitpainter import CircuitPainter
from argparse import ArgumentParser

def Perfboard(x_count,y_count,spacing,hole_d,ring_d):
    painter = CircuitPainter()

    # Make the board shape
    painter.layer("Edge_Cuts")
    painter.rect(0,0,spacing*x_count,spacing*y_count)

    painter.width(0.05)
    painter.fill()

    for x_pos in [spacing*(x+0.5) for x in range(0,x_count)]:
        for y_pos in [spacing*(y+0.5) for y in range(0,y_count)]:
            painter.layer('F_Cu')
            painter.via(x_pos,y_pos,d=hole_d,w=ring_d)

            # By default, vias are tented (covered). Draw circlular openings
            # in the soldermask layers to make them untented, instead of
            # changing the board-level setting.
            painter.layer('F_Mask')
            painter.circle(x_pos,y_pos,ring_d/2)
            painter.layer('B_Mask')
            painter.circle(x_pos,y_pos,ring_d/2)


    return painter

if __name__ == "__main__":
    parser = ArgumentParser(description="perfboard generator")
    parser.add_argument('-x',type=int,default=9, help="Number of holes in the x direction")
    parser.add_argument('-y',type=int,default=10, help="Number of holes in the y direction")
    parser.add_argument('-s','--spacing',type=float,default=2.54, help="Spacing between the holes (mm)")
    parser.add_argument('-d','--hole_diameter',type=float,default=1.02, help="Hole diameter (mm)")
    parser.add_argument('-r','--ring_diameter',type=float,default=2, help="Ring diameter (mm)")
    parser.add_argument('--save',action="store_true",help="Save the design to a KiCad file")
    args = parser.parse_args()

    painter = Perfboard(args.x, args.y, args.spacing, args.hole_diameter,args.ring_diameter)
    if args.save:
        painter.export_gerber('perfboard')
    else:
        painter.preview()
