from circuitpainter import CircuitPainter
from argparse import ArgumentParser
import math
import random

def asterix(arms,min_leds_per_arm,max_leds_per_arm):
    painter = CircuitPainter()

    # Start drawing at a nicer location
    painter.translate(100,100)

    arm_led_spacing = 10 # Space between LEDS on arm, in mm
    arm_width = 8 # Width of an arm, in MM


    center_diameter = arm_width/2/math.tan(math.pi/arms)

    # Fill the center with copper
    l = arm_width/2/math.sin(math.pi/arms)
    points = []
    for i in range(0,arms):
        x = l*(math.cos(2*math.pi/arms*(i+.5)))
        y = l*(math.sin(2*math.pi/arms*(i+.5)))
        points.append([x,y])

    painter.layer("F_Cu")
    painter.poly_zone(points,net="5V")
    painter.layer("B_Cu")
    painter.poly_zone(points,net="gnd")

    led_num = 1

    # Add connector
    painter.push_matrix()
    painter.translate(center_diameter-4,0)
    painter.footprint(0, 2,
                        "Connector_JST","JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
                        angle=90,
                        nets=["5V",f"d{led_num}","gnd"],
                        reference=f"J1"
                        )
    
    painter.layer("B_SilkS")
    painter.text(-5,-2,"GND",mirrored=True)
    painter.text(-5,0,"DIN",mirrored=True)
    painter.text(-5,2,"5V",mirrored=True)
    painter.pop_matrix()
    
    # Step through arms backwards, to make data routing cleaner
    for arm in range(arms-1,-1,-1):
        leds = random.randrange(min_leds_per_arm,max_leds_per_arm+1)

        arm_length = leds*arm_led_spacing

        painter.push_matrix()
        painter.rotate((arm+1)/arms*360)
        painter.translate(center_diameter,0)

        # Draw arm outline
        painter.width(0.1)
        painter.layer("Edge_Cuts")
        painter.line(0,arm_width/2,arm_length,arm_width/2)
        painter.line(arm_length,arm_width/2,arm_length,-arm_width/2)
        painter.line(arm_length,-arm_width/2,0,-arm_width/2)

        # Draw power and ground rects
        painter.layer("F_Cu")
        painter.rect_zone(0,-arm_width/2,arm_length,arm_width/2,net="5V")
        painter.layer("B_Cu")
        painter.rect_zone(0,-arm_width/2,arm_length,arm_width/2,net="gnd")

        arm_led_nums = []

        # Place LEDs on this arm
        painter.width(0.254)
        painter.layer("F_Cu")
        for led in range(0,leds):
            painter.footprint((led+.5)*arm_led_spacing, 0,
                              "LED_SMD","LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm",
                              angle=180,
                              nets=["5V",f"d{led_num+1}","gnd",f"d{led_num}"],
                              reference=f"LED{led_num}"
                              )
           
            # Add a ground via under the LED
            gnd_pad = painter.get_object_position(painter.get_pads(f"LED{led_num}")[2])
            painter.track(gnd_pad[0],gnd_pad[1],gnd_pad[0]+1.5,gnd_pad[1])
            painter.via(gnd_pad[0]+1.5,gnd_pad[1])

            arm_led_nums.append(led_num)
            led_num += 1

        # Connect data lines between LEDs on arm
        for a,b in zip(arm_led_nums[:-1],arm_led_nums[1:]):
            src_pad = painter.get_object_position(painter.get_pads(f"LED{a}")[1])
            dest_pad = painter.get_object_position(painter.get_pads(f"LED{b}")[3])
            painter.track(src_pad[0],src_pad[1],dest_pad[0],dest_pad[1])

        # Bring first data line back to asterix center
        if arm != arms - 1:
            first_pad = painter.get_object_position(painter.get_pads(f"LED{arm_led_nums[0]}")[3])
            painter.track(first_pad[0],first_pad[1],first_pad[0],arm_width/2-1)
            painter.track(first_pad[0],arm_width/2-1,-1,arm_width/2-1)
        else:
            first_pad = painter.get_object_position(painter.get_pads(f"LED{arm_led_nums[0]}")[3])
            din_pad = painter.get_object_position(painter.get_pads(f"J1")[1])
            painter.track(first_pad[0],first_pad[1],din_pad[0],din_pad[1])


        # Connect previous data line
        if arm != arms-1:
            last_local = painter._world_to_local(lastDataCoord[0],lastDataCoord[1])
            painter.track(last_local[0],last_local[1],-1,arm_width/2-1)


        # Bring final data line back to asterix center
        if arm != 0:
            last_pad = painter.get_object_position(painter.get_pads(f"LED{arm_led_nums[-1]}")[1])
            painter.track(last_pad[0],last_pad[1],last_pad[0],-arm_width/2+1)
            painter.track(last_pad[0],-arm_width/2+1,-1,-arm_width/2+1)
            lastDataCoord = painter._local_to_world(-1,-arm_width/2+1)

        painter.pop_matrix()

    return painter

if __name__ == "__main__":
    parser = ArgumentParser(description="Asterix")
    parser.add_argument('--arms',type=int,default=25, help="Number of arms")
    parser.add_argument('--min-leds',type=int,default=8, help="Minimum number of LEDs per arm")
    parser.add_argument('--max-leds',type=int,default=12, help="Maximum number of LEDs per arm")
    parser.add_argument('--save',action="store_true",help="Save the design to a KiCad file")
    args = parser.parse_args()

    painter = asterix(args.arms,args.min_leds,args.max_leds)
    if args.save:
        painter.export_gerber('asterix')
    else:
        painter.preview()


