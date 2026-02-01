#!/usr/bin/env python
from circuitpainter import CircuitPainter
from argparse import ArgumentParser
import math
import pcbnew

def to_polar(x,y):
    angle = math.degrees(math.atan2(y,x))
    distance = math.sqrt(math.pow(x,2)+math.pow(y,2))
    return angle, distance

def ring_pcb(led_count, diameter):
    # Create a new Circuit Painter
    painter = CircuitPainter(library_path='/home/matt/repos/bl_parts/kicad')

    painter.translate(50,50)

    pcb_width = 5
    led_stepback = 1.2 # Distance from outer edge of PCB to LED center

    # Draw a board outline
    painter.layer("Edge_Cuts")
    painter.circle(0,0,diameter/2)
    painter.circle(0,0,diameter/2-pcb_width)

    # LEDs and resistors
    painter.layer("F_Cu")
    for led_num in range(0,led_count):
        angle = 360*((led_num+0.5)/led_count)
        
        painter.push_matrix()
        painter.rotate(-angle)
        painter.translate(diameter/2,0)

        led = painter.footprint(-led_stepback, 0,
                          "bl_footprints","SK6812SIDE-A-RVS-001",
                          angle=90,
                          nets=[f"d{led_num}","5V",f"d{led_num+1}","gnd"],
                          reference=f"LED{led_num+1}"
                          )

        cap = painter.footprint(-led_stepback-2, 0,
                          "bl_footprints","CAPC1005X06L",
                          angle=90,
                          nets=["5V","gnd"],
                          reference=f"C{led_num+1}"
                          )

        painter.width(0.5)

        led_vcc_pad_pos = painter.get_object_position(painter.get_pads(f"LED{led_num+1}")[1])
        cap_vcc_pad_pos = painter.get_object_position(painter.get_pads(f"C{led_num+1}")[0])
        painter.track(led_vcc_pad_pos[0],led_vcc_pad_pos[1],cap_vcc_pad_pos[0],cap_vcc_pad_pos[1])
        painter.track(led_vcc_pad_pos[0],led_vcc_pad_pos[1],led_vcc_pad_pos[0]+1,led_vcc_pad_pos[1])
        painter.via(led_vcc_pad_pos[0]+1,led_vcc_pad_pos[1])

        led_gnd_pad_pos = painter.get_object_position(painter.get_pads(f"LED{led_num+1}")[3])
        cap_gnd_pad_pos = painter.get_object_position(painter.get_pads(f"C{led_num+1}")[1])
        gnd_via_pos = [led_gnd_pad_pos[0]-1.2,led_gnd_pad_pos[1]+.5]
        painter.track(led_gnd_pad_pos[0],led_gnd_pad_pos[1],gnd_via_pos[0],gnd_via_pos[1])
        painter.track(cap_gnd_pad_pos[0],cap_gnd_pad_pos[1],gnd_via_pos[0],gnd_via_pos[1])
        painter.via(gnd_via_pos[0],gnd_via_pos[1])

        painter.pop_matrix()

    # Input and output connection pads
    pads = [
        {'angle':45, 'd':'d0','t':'DI'},
        {'angle':135, 'd':'d0','t':'DI'},
        {'angle':225, 'd':'d24','t':'DO'},
        {'angle':315, 'd':'d24','t':'DO'},
        ]
    for pad in pads:
        painter.push_matrix()
        painter.rotate(-pad['angle'])
        painter.translate(diameter/2-pcb_width/2,0)

        off_x = 1.2
        off_y = 1.6

        text_off_x = -.3
        text_off_y = 2

        angle = -40

        painter.layer("B_Cu")
        p_pad = painter.footprint(off_x, off_y,
                          "bl_footprints","TestPoint_Pad_1.2x1.6mm",
                          angle=angle,
                          nets=["5V"],
                          reference=f"ppad{angle}"
                          )

        painter.layer("B_SilkS")
        painter.text(off_x+text_off_x,off_y+text_off_y,"5V",size=1,mirrored=True, angle=-90)

        painter.layer("B_Cu")
        g_pad = painter.footprint(0, 0,
                          "bl_footprints","TestPoint_Pad_1.2x1.6mm",
                          angle=angle,
                          nets=[pad['d']],
                          reference=f"dpad{angle}"
                          )

        painter.layer("B_SilkS")
        painter.text(text_off_x,text_off_y,pad['t'],size=1,mirrored=True, angle=-90)

        painter.layer("B_Cu")
        g_pad = painter.footprint(-off_x, -off_y,
                          "bl_footprints","TestPoint_Pad_1.2x1.6mm",
                          angle=angle,
                          nets=["gnd"],
                          reference=f"gpad{angle}"
                          )

        painter.layer("B_SilkS")
        painter.text(-off_x+text_off_x-.1,-off_y+text_off_y+.3,"GND",size=1,mirrored=True, angle=-90)

        painter.pop_matrix()


    # tracks between data input/output pads and LEDs
    painter.layer("B_Cu")
    painter.width(0.2)

    start = painter.get_object_position(painter.get_pads("LED1")[0])
    end = painter.get_object_position(painter.get_pads(f"LED{led_count}")[2])
    angle_in, distance = to_polar(*start)

    painter.push_matrix()
    painter.rotate(angle_in)
    painter.track(diameter/2-pcb_width/2,0,distance,0)
    painter.via(distance,0)
    painter.pop_matrix()

    angle_out, distance = to_polar(*end)
    painter.push_matrix()
    painter.rotate(angle_out)
    painter.track(diameter/2-pcb_width/2,0,distance,0)
    painter.via(distance,0)
    painter.pop_matrix()

    painter.arc_track(0,0,diameter/2-pcb_width/2,angle_in,-135,"d0") # TODO start angle depends on component count
    painter.arc_track(0,0,diameter/2-pcb_width/2,135,angle_out,f"d{led_count}")

    

    # Top ground plane
    painter.layer("F_Cu")
    painter.width(0.1)
    painter.fill()
    tg_zone = painter.circle_zone(0,0,diameter/2,"gnd")
    tg_zone.SetLocalClearance(pcbnew.FromMM(0.2))

    # Bottom ground plane
    painter.layer("B_Cu")
    bg_zone = painter.circle_zone(0,0,diameter/2-pcb_width/2,"gnd")
    bg_zone.SetAssignedPriority(2)
    bg_zone.SetLocalClearance(pcbnew.FromMM(0.2))
    bg_zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)

    # Bottom power plane
    bp_zone = painter.circle_zone(0,0,diameter/2,"5V")
    bp_zone.SetLocalClearance(pcbnew.FromMM(0.2))
    bp_zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)

    # connect data lines between LEDs
    painter.layer("F_Cu")
    painter.width(0.2)

    arc_diameter = diameter/2-.8

    parts = [f'LED{led_num+1}' for led_num in range(0,led_count)]
    for led_num in range(0,len(parts)-1):
        start = painter.get_object_position(painter.get_pads(parts[led_num])[2])
        end = painter.get_object_position(painter.get_pads(parts[led_num+1])[0])

        # Line from center of output pad to radius
        angle, distance = to_polar(*start)
        painter.push_matrix()
        painter.rotate(angle)
        painter.line(distance,0,arc_diameter,0)
        painter.pop_matrix()

        # Line from center of input pad to radius
        angle2, distance = to_polar(*end)
        painter.push_matrix()
        painter.rotate(angle2)
        painter.line(distance,0,arc_diameter,0)
        painter.pop_matrix()

        # Arc to connect them
        painter.arc(0,0,arc_diameter,angle2,angle)

    # Silksreen first LED marker
    painter.push_matrix()
    painter.layer("F_SilkS")
    angle = 360*(0.5/led_count)
    painter.rotate(-angle)
    painter.translate(diameter/2-pcb_width/2,0)
    painter.line(-1.5,-1.5,-1.5,1.5)
    painter.translate(-1.5,-1.5)
    painter.line(0,0,.5,.5)
    painter.line(0,0,-.5,.5)
    painter.pop_matrix()

    # Silksreen text on bottom
    painter.push_matrix()
    painter.layer("B_SilkS")
    painter.translate(diameter/2-pcb_width/2,0)
    painter.text(-0.4,0,"BLINKINLABS.COM",size=1,mirrored=True, angle=-90)
    painter.pop_matrix()

    painter.push_matrix()
    painter.layer("B_SilkS")
    painter.rotate(90)
    painter.translate(diameter/2-pcb_width/2,0)
    painter.text(.7,0,"24x",size=1,mirrored=True, angle=-90)
    painter.text(-.9,0,"SK6812SIDE(OUT)",size=1,mirrored=True, angle=-90)
    painter.pop_matrix()

    painter.push_matrix()
    painter.layer("B_SilkS")
    painter.rotate(180)
    painter.translate(diameter/2-pcb_width/2,0)
    painter.text(.7,0,"Rev C",size=1,mirrored=True, angle=-90)
    painter.text(-.9,0,"2025-06-24",size=1,mirrored=True, angle=-90)
    painter.pop_matrix()
    

    return painter

if __name__ == "__main__":
    parser = ArgumentParser(description="Ring LED generator")
    parser.add_argument('--led_count',type=int,default=24, help="Number of leds")
    parser.add_argument('--diameter',type=int,default=43.4, help="Outer diameter (mm)")
    parser.add_argument('--save',action="store_true",help="Save the design to a KiCad file")
    args = parser.parse_args()

    painter = ring_pcb(args.led_count, args.diameter)
    if args.save:
        painter.export_bom('ring_led')
        painter.export_gerber('ring_led')
        painter.export_pos('ring_led')
        painter.export_step('ring_led')
        painter.export_render('ring_led_top', rotation=[180,0,0])
        painter.export_render('ring_led_bottom', rotation=[0,0,0])
    else:
        painter.preview()
