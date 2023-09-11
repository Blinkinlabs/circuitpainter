from circuitpainter import CircuitPainter

# Create a new circuit board
painter = CircuitPainter()

# Start drawing at position 50, 50 on the circuit board canvas, so that it
# fits in the sheet nicely.
painter.translate(50,50)

# Draw a board outline for a 50x20mm PCB
painter.layer("Edge_Cuts")
painter.rect(0,0,50,20)

painter.layer("F_Cu")
painter.rect_zone(0,0,50,20,"vbat")
painter.layer("B_Cu")
painter.rect_zone(0,0,50,20,"gnd")


# Add a battery to the PCB
painter.footprint(10,10,
                  "Battery","BatteryHolder_Keystone_3001_1x12mm",
                  nets=['gnd','gnd','vbat']
                  )

# Add an LED to the PCB
painter.footprint(30,10,
                  "LED_THT","LED_D5.0mm",
                  angle=90,nets=['gnd','vbat']
                  )
painter.preview()
painter.save("hello_painter")
