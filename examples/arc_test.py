from circuitpainter import CircuitPainter
from argparse import ArgumentParser

def arc_test(cols, rows, spacing):
    # Create a new Circuit Painter
    painter = CircuitPainter()

    # Draw a board outline
    painter.layer("Edge_Cuts")
    painter.rect(-spacing,-spacing,(cols)*spacing,(rows)*spacing)

    painter.layer("F_Cu")
    painter.rect_zone(-spacing,-spacing,(cols)*spacing,(rows)*spacing,"vbat")
    painter.layer("B_Cu")
    painter.rect_zone(-spacing,-spacing,(cols)*spacing,(rows)*spacing,"gnd")

    painter.layer("F_Cu")
    painter.width(.4)
    for col in range(0,cols):
        for row in range(0,rows):
            painter.push_matrix()
            painter.translate(col*spacing,row*spacing)

            painter.via(0,0,"gnd")
            zone=painter.circle_zone(0,0,2,"gnd")
            zone.SetAssignedPriority(1)

            if row == 0 and col%2 == 0:
                painter.arc_track(0,0,spacing/2,180,270+180)

            if row == rows - 1 and col%2 == 0:
                painter.arc_track(0,0,spacing/2,0,270)

            elif row == rows - 1 and col%2 == 1:
                painter.arc_track(0,0,spacing/2,180,270)

            elif row == 0 and col%2 == 1:
                painter.arc_track(0,0,spacing/2,0,90)

            elif row%2 == 0:
                painter.arc_track(0,0,spacing/2,270,270+180)

            else:
                painter.arc_track(0,0,spacing/2,90,270)

            painter.pop_matrix()

    return painter

if __name__ == "__main__":
    parser = ArgumentParser(description="Asterix")
    parser.add_argument('--cols',type=int,default=9, help="Number of columns")
    parser.add_argument('--rows',type=int,default=6, help="Number of rows")
    parser.add_argument('--spacing',type=int,default=5, help="Spacing between rows (mm()")
    parser.add_argument('--save',action="store_true",help="Save the design to a KiCad file")
    args = parser.parse_args()

    painter = arc_test(args.cols, args.rows, args.spacing)
    if args.save:
        painter.export_gerber('arc_test')
    else:
        painter.preview()
