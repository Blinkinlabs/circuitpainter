import math
import argparse
from circuitpainter import CircuitPainter

class Path:
    def __init__(self, points = None):
        # TODO: If we just do points = [], then that [] is shared between all instaces, 
        if points:
            self.points = points
        else:
            self.points = []
    
    def add_point(self, x, y):
        self.points.append([x,y])

    def draw_as_line(self, painter):
        for a,b in zip(self.points[:-1], self.points[1:]):
            painter.line(*a,*b)

    def _segment_length(self, segment):
        start = self.points[segment]
        end = self.points[segment+1]

        return math.dist(start, end)
    
    def _path_length(self):
        length = 0

        segments = len(self.points) - 1

        for segment in range(0, segments):
            length += self._segment_length(segment)
        
        return length

    def _get_point_along_segment(self, segment, distance):
        start = self.points[segment]
        end = self.points[segment+1]

        dist_x = end[0] - start[0]
        dist_y = end[1] - start[1]
        length = self._segment_length(segment)

        percent = distance/length
        return [start[0] + dist_x * percent, start[1] + dist_y * percent]
    
    def _get_angle_along_segment(self, segment, distance):
        start = self.points[segment]
        end = self.points[segment+1]

        y = (end[1] - start[1])
        x = (end[0] - start[0])
        h = math.dist(start, end)

        angle = math.degrees(math.acos(abs(y/h)))

        if x > 0  and y < 0:
            angle = 180 + angle
        elif x < 0 and y < 0:
            angle = 180 - angle
        elif x > 0 and y > 0:
            angle = 360 - angle

        return angle

    def _is_closed(self, precision = 0.001):
        return math.dist(self.points[0], self.points[-1]) < precision


    def space_along_path(self, painter, count, place_function):
        path_length = self._path_length()

        if self._is_closed:
            spacing = path_length / count
        else:
            spacing = path_length / (count-1)

        self.place_along_path(painter, spacing, place_function)

    def place_along_path(self, painter, spacing, place_function):
        distance = spacing

        segments = len(self.points) - 1

        for segment in range(0,segments):
            position_on_segment = 0

            remaining_segment_length = self._segment_length(segment)
            while distance + remaining_segment_length >= spacing:
                travel = spacing - distance
                position_on_segment += travel
                remaining_segment_length -= travel
                distance = 0

                # print('   ',
                #       f'{self._segment_length(segment):02f}',
                #       f'{position_on_segment:02f}',
                #       f'{remaining_segment_length:02f}',
                #       f'{distance:02f}',
                #       f'{travel:02f}'
                #       )

                position = self._get_point_along_segment(segment, position_on_segment)
                angle = self._get_angle_along_segment(segment, position_on_segment)

                painter.push_matrix()
                painter.translate(*position)
                painter.rotate(angle)
                place_function(painter)
                painter.pop_matrix()

            # If there is any left over spacing, save it to distance
            distance += remaining_segment_length


def place_via(painter):
    # painter.via(0,0)
    painter.footprint(0,0,"LED_SMD","LED_0805_2012Metric",nets=[f'led_x','vcc'])


def path_test():
    painter = CircuitPainter()

    path = Path()

    radius = 15
    divisions = 10

    for division in range(0,divisions+1):
        angle = 360*division/divisions
        path.add_point(radius*math.cos(math.radians(angle)),
                       radius*math.sin(math.radians(angle)))

    painter.layer('F_Cu')
    path.draw_as_line(painter)
    path.space_along_path(painter, 16, place_via)

    path2 = Path()
    x_step = 10
    y_step = 13
    segments = 13

    for segment in range(0,segments):
        path2.add_point(x_step*segment, y_step if segment%2 else -y_step)

    painter.translate(0,50)
    path2.draw_as_line(painter)
    path2.space_along_path(painter, 50, place_via)


    return painter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Path test")
    parser.add_argument('-s','--save',action="store_true",help="Save the design to a KiCad file")
    args = parser.parse_args()

    painter = path_test()

    if args.save:
        painter.save(f"lotus_leds_l={args.leds}_r={args.radius}_p={args.led_radius_percent}")
    else:
        painter.preview()