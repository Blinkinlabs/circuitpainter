import math
import argparse
from circuitpainter import CircuitPainter

def lotus_leds(radius, leds):
    painter = CircuitPainter()

    painter.no_designators() # Don't show reference designator names on the board silkscreen
    painter.layer('F_Cu')
    painter.width(.4)

    angle = math.ceil(360/leds)

    start_angle = 190
    end_angle = 300
    resistor_angle = (end_angle-start_angle)/3+start_angle
    led_angle = (end_angle-start_angle)*2/3+start_angle

    for angle in range(0,360,angle):
        painter.layer('F_Cu')
        painter.width(.3)

        painter.push_matrix() # Save the current transformation settings
        painter.rotate(angle)
        painter.translate(radius/2,0)

        painter.push_matrix()
        painter.rotate(resistor_angle)
        painter.translate(radius/2,0)
        painter.rotate(90)
        painter.footprint(0,0,"Resistor_SMD","R_0805_2012Metric",nets=['gnd',f'led_{angle}'])
        painter.pop_matrix()

        painter.push_matrix()
        painter.rotate(led_angle)
        painter.translate(radius/2,0)
        painter.rotate(90)
        painter.footprint(0,0,"LED_SMD","LED_0805_2012Metric",nets=[f'led_{angle}','vcc'])
        painter.pop_matrix()

        painter.arc_track(0,0,radius/2,end_angle,led_angle+3)
        painter.arc_track(0,0,radius/2,led_angle-3,resistor_angle+3)
        painter.arc_track(0,0,radius/2,resistor_angle-3,start_angle)

        painter.push_matrix()
        painter.rotate(start_angle)
        painter.translate(radius/2,0)
        painter.via(0,0)
        painter.pop_matrix()

        painter.push_matrix()
        painter.rotate(end_angle)
        painter.translate(radius/2,0)
        painter.via(0,0)
        painter.pop_matrix()

        painter.layer('F_SilkS')
        painter.width(.6)
        painter.arc(0,0,radius/2,start_angle,end_angle)

        painter.pop_matrix()


        painter.push_matrix() # Save the current transformation settings
        painter.rotate(angle)
        painter.translate(-radius/2,0)
        painter.arc(0,0,radius/2,180-end_angle, 180-start_angle)
        painter.pop_matrix()

    # Fill the back of the board with a copper zone, and assign it to the 'vcc' net
    painter.layer('B_Cu')
    painter.circle_zone(0,0,radius,net='vcc')

    # Add a battery connector to the back
    painter.layer('B_Cu')
    painter.footprint(0,0,"Battery","BatteryHolder_Keystone_3002_1x2032",nets=['vcc','vcc','gnd'])

    # Add label
    painter.layer('B_SilkS')
    painter.text(0,12,"Made with CircuitPainter",mirrored=True)
    painter.text(0,14,"HaD Berlin 2024",mirrored=True)

    # Make the board shape to a circle
    painter.layer("Edge_Cuts")
    painter.circle(0,0,radius)

    return painter


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lotus LED board generator")
    parser.add_argument('-l','--leds',type=int,default=9, help="Number of LED radials")
    parser.add_argument('-r','--radius',type=float,default=18, help="Board radius (mm)")
    args = parser.parse_args()

    painter = lotus_leds(radius=args.radius, leds=args.leds)
    painter.preview()
    painter.save("lotus_leds")