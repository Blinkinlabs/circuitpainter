import math
import argparse
from circuitpainter import CircuitPainter

def rotate(x,y,angle):
    """ Rotate a vector around the origin
    
    x,y: extents of the vector
    angle: angle to rotate the vector (in degrees)
    """
    return [
        math.cos(math.radians(angle))*x - math.sin(math.radians(angle))*y,
        math.sin(math.radians(angle))*x + math.cos(math.radians(angle))*y
        ]

def lerp(a,b,percent):
    """ Linear interpolate between two numbers

    a: first number
    b: second number
    percent: position between the two numbers, in percent.
    """
    return a+(b-a)*percent

def lotus_leds(radius, leds,led_radius_percent):
    painter = CircuitPainter()

    anglular_step = math.ceil(360/leds)

    # Compute the radial positions that the component arcs start and stop at
    # Define them in percent so that you can accomodate more vias by making
    # the radius larger
    radius_inner = radius*.05
    radius_outer = radius*.9
    radius_arc = radius*led_radius_percent

    # Determine the starting position of a component art. It should start
    # at an interval of the arc angular step, so that the ends of neighboring
    # arcs will line up
    arc_start_x,arc_start_y = rotate(radius_inner,0,anglular_step*1.5)

    # Make a straight line from the start of the arc, to the end of the arc.
    # The center of this line will be used as a reference for determinig the
    # arc centers.
    line_angle = math.degrees(math.atan2(0-arc_start_y,radius_outer-arc_start_x))
    line_len = math.sqrt(math.pow(0-arc_start_y,2)+math.pow(radius_outer-arc_start_x,2))

    # Limit the arc radius to 1/2 of the line length, otherwise the following
    # computations will fail.
    if radius_arc*2 < line_len:
        radius_arc = line_len/2

    # Calculate the distance from the reference line to the center of the
    # component arc. Also calculate the angular extent of the arc.
    arc_offset = math.sqrt(math.pow(radius_arc,2)-math.pow(line_len/2,2))
    arc_angle = math.degrees(math.asin(line_len/2/radius_arc))

    # Determine the angular position of the resistor and LED along the arc
    resistor_angle = 270-arc_angle/3
    led_angle = 270+arc_angle/3

    for angle in range(0,360,anglular_step):
        painter.push_matrix()

        # Rotate the reference plane to the starting angle for this arc
        painter.rotate(angle)

        # Switch to the top copper layer, and set the track width to 0.3mm
        painter.layer('F_Cu')
        painter.width(.3)

        painter.push_matrix()
        # Change the drawing origin to the center of the component arc
        painter.translate(lerp(arc_start_x,radius_outer,.5),lerp(-arc_start_y,0,.5))
        painter.rotate(-line_angle)
        painter.translate(0,arc_offset)

        # Translate from the center of the componet arc to the center of the
        # resistor, and then place it
        painter.push_matrix()
        painter.rotate(resistor_angle)
        painter.translate(radius_arc,0)
        painter.rotate(90)
        painter.footprint(0,0,"Resistor_SMD","R_0805_2012Metric",nets=['gnd',f'led_{angle}'])
        painter.pop_matrix()

        # Translate from the center of the componet arc to the center of the
        # LED, and then place it
        painter.push_matrix()
        painter.rotate(led_angle)
        painter.translate(radius_arc,0)
        painter.rotate(90)
        painter.footprint(0,0,"LED_SMD","LED_0805_2012Metric",nets=[f'led_{angle}','vcc'])
        painter.pop_matrix()

        # Draw three arc tracks from the resistor to a via, from the resistor
        # to the LED, and from the LED to a via. Note that we don't need to
        # specify the track names here- KiCad will automatically detect that
        # the track overlaps a footprint, and assign the track to the same
        # net as the footprint. If you have a more complex board, then it
        # might be a better strategy to specify the net names explicitly.
        painter.arc_track(0,0,radius_arc,270+arc_angle,led_angle+3)
        painter.arc_track(0,0,radius_arc,led_angle-3,resistor_angle+3)
        painter.arc_track(0,0,radius_arc,resistor_angle-3,270-arc_angle)

        # Create the vias to connect the track ends to the copper fills on the
        # bottom of the board. We don't need to specify the net names here,
        # either, because KiCad will automatically figure them out based on
        # the tracks that the via overlaps.
        painter.push_matrix()
        painter.rotate(270-arc_angle)
        painter.translate(radius_arc,0)
        painter.via(0,0)
        painter.pop_matrix()

        painter.push_matrix()
        painter.rotate(270+arc_angle)
        painter.translate(radius_arc,0)
        painter.via(0,0)
        painter.pop_matrix()

        painter.pop_matrix()

        # Draw arcs on the silkscreen
        painter.layer('F_SilkS')
        painter.width(.3)

        # The first silkscreen arc follows the component arc
        painter.push_matrix()
        painter.translate(lerp(arc_start_x,radius_outer,.5),lerp(-arc_start_y,0,.5))
        painter.rotate(-line_angle)
        painter.translate(0,arc_offset)
        painter.arc(0,0,radius_arc,270-arc_angle,270+arc_angle)
        painter.pop_matrix()

        # The second silkscreen arc is a mirror image
        painter.push_matrix()
        painter.translate(lerp(arc_start_x,radius_outer,.5),lerp(arc_start_y,0,.5))
        painter.rotate(line_angle)
        painter.translate(0,-arc_offset)
        painter.arc(0,0,radius_arc,90-arc_angle,90+arc_angle)
        painter.pop_matrix()

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

    # Make the board shape a circle
    painter.layer("Edge_Cuts")
    painter.circle(0,0,radius)

    return painter


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lotus LED board generator")
    parser.add_argument('-l','--leds',type=int,default=9, help="Number of LED radials")
    parser.add_argument('-r','--radius',type=float,default=18, help="Board radius (mm)")
    parser.add_argument('-p','--led_radius_percent',type=float,default=.55, help="LED arc amount(0.5-3)")
    parser.add_argument('-s','--save',action="store_true",help="Save the design to a KiCad file")
    args = parser.parse_args()

    painter = lotus_leds(radius=args.radius, leds=args.leds, led_radius_percent=args.led_radius_percent)

    if args.save:
        painter.save(f"lotus_leds_l={args.leds}_r={args.radius}_p={args.led_radius_percent}")
    else:
        painter.preview()