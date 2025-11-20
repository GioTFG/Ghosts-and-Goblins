from .actor import Point

def center(pos: Point, size: Point) -> Point:
    """
    Calculates the central pixel of a given rectangle, given its top-left pixel position and its size.
    :param pos: The position of the top-left pixel.
    :param size: The size, so a tuple that says width and height of the rectangle.
    :return: The (absolute) position of the central pixel.
    """
    x, y, w, h = pos + size
    return x + w / 2, y + h / 2

def remove_pos(pos1: Point, pos2: Point) -> Point:
    """
    Makes a subtraction between two points, component-by-component.\n
    Es: (10, 9) - (4, 1) = (6, 8)
    """
    return pos1[0] - pos2[0], pos1[1] - pos2[1]