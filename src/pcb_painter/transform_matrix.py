import math
import numpy

class TransformMatrix():
    """ Matrix transform to handle translations and rotations"""

    def __init__(self):
        self.reset()

    def reset(self):
        """ Reset the matrix transform """
        self.matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        self.states = []

    def push(self):
        """ Save the transform state on a stack """
        self.states.append(self.matrix)

    def pop(self):
        """ Restore the last transform state from the stack

        If the stack was empty, reset the transform
        """
        if len(self.states) > 0:
            self.matrix = self.states.pop()
        else:
            self.reset()

    def get_angle(self):
        """ Get the current rotation angle from the transform

        We restrict the transform to translate/rotate only, so angle is well
        defined.
        """
        return math.degrees(math.atan2(self.matrix[0][1], self.matrix[0][0]))

    def translate(self, x, y):
        """ Apply a linear transformation

        x: x component of translation vector
        y: y component of translation vector
        """
        m = [[1, 0, x], [0, 1, y], [0, 0, 1]]

        self.matrix = numpy.matmul(self.matrix, m)

    def rotate(self, angle):
        """ Apply a rotation

        angle: Rotation angle (degrees)
        """
        r = numpy.radians(angle)
        m = [[math.cos(r), -math.sin(r), 0],
             [math.sin(r), math.cos(r), 0],
             [0, 0, 1]]

        self.matrix = numpy.matmul(self.matrix, m)

    def project(self, x, y):
        """ Apply the transformation to a coordinate

        x: x component of point to transform
        y: y component of point to transform
        returns: x', y' transformed coordinate
        """
        p = [x, y, 1]

        result = numpy.matmul(self.matrix, p)
        return float(result[0]), float(result[1])

    def inverse_project(self, x, y):
        """ Apply an inverse transformation to a coordinate

        x: x component of point to transform
        y: y component of point to transform
        returns: x', y' transformed coordinate
        """
        p = [x, y, 1]

        inv = numpy.linalg.inv(self.matrix)

        result = numpy.matmul(inv, p)
        return float(result[0]), float(result[1])
