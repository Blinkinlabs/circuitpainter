from circuitpainter import CircuitPainter

# Create a new Circuit Painter
painter = CircuitPainter()

# Start drawing at position 50, 50 on the circuit board canvas, so that it
# fits in the sheet nicely.
painter.translate(50,50)

cols = 9
rows = 10
spacing = 5

# Draw a board outline for a 50x20mm PCB

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

painter.save("arc_test")
