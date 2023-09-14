from circuitpainter import CircuitPainter
painter = CircuitPainter()

painter.no_designators() # Don't show reference designator names on the board silkscreen
painter.layer('F_Cu')
painter.width(.2)

for angle in range(0,360,36):
    painter.push_matrix() # Save the current transformation settings
    painter.rotate(angle)
    painter.translate(5,0)
    painter.footprint(0,0,"Resistor_SMD","R_0805_2012Metric",nets=['gnd',f'led_{angle}'])
    painter.footprint(5,0,"LED_SMD","LED_0805_2012Metric",nets=[f'led_{angle}','vcc'])
    painter.track(1,0,4,0) # Connect the resistor to the LED
    painter.track(-1,0,-2,0) # Connect the resistor to ground
    painter.via(-2,0)
    painter.track(6,0,7,0) # Connect the LED to vcc
    painter.via(7,0)
    painter.pop_matrix()

# Fill the back of the board with a copper zone, and assign it to the 'vcc' net
painter.layer('B_Cu')
painter.circle_zone(0,0,14,net='vcc')

# Add a battery connector to the back
painter.layer('B_Cu')
painter.footprint(0,0,"Battery","BatteryHolder_Keystone_3000_1x12mm",nets=['vcc','vcc','gnd'])

# Make the board shape to a circle
painter.layer("Edge_Cuts")
painter.circle(0,0,14)

painter.preview()
