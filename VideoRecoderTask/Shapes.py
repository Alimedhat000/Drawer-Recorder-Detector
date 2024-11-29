
import cv2 as cv
import numpy as np


class Shape:
    """
    Abstract base class representing a geometric shape. 
    Subclasses must implement the draw and get_data methods.
    """

    def __init__(self, color, thickness=2):
        """
        Initializes the shape with the specified color and default thickness.

        Parameters:
            color (tuple): The RGB color of the shape.
        """
        self.color = color
        self.thickness = thickness

    def draw(self, canvas):
        """
        Draws the shape on the specified canvas. This is an abstract method
        and must be implemented by subclasses.

        Parameters:
            canvas (Canvas): The canvas to draw the shape on.
        """
        pass

    def get_data(self):
        """
        Returns the data associated with the shape. This is an abstract method
        and must be implemented by subclasses.

        Returns:
            dict: A dictionary containing the shape's data.
        """
        pass


class Circle(Shape):
    """
    Represents a circle shape with a specified center, radius, and color.
    """

    def __init__(self, center, radius, color):
        """
        Initializes the circle with the given center, radius, and color.

        Parameters:
            center (tuple): The (x, y) coordinates of the center.
            radius (int): The radius of the circle.
            color (tuple): The RGB color of the circle.
        """
        super().__init__(color)
        self.center = center
        self.radius = radius

    def draw(self, Canvas):
        """
        Draws the circle on the canvas.

        Parameters:
            Canvas (Canvas): The canvas to draw the circle on.
        """
        if self.center and self.radius > 0:
            cv.circle(Canvas.canvas, self.center,
                      self.radius, self.color, self.thickness)

    def get_data(self):
        """
        Returns the data of the circle.

        Returns:
            dict: A dictionary containing the circle's center and radius.
        """
        return {
            'type': 'circle',
            'center': self.center,
            'radius': self.radius,
        }


class Rectangle(Shape):
    """
    Represents a rectangle shape with specified top-left and bottom-right corners.
    """

    def __init__(self, top_left, bottom_right, color):
        """
        Initializes the rectangle with the given corners and color.

        Parameters:
            top_left (tuple): The (x, y) coordinates of the top-left corner.
            bottom_right (tuple): The (x, y) coordinates of the bottom-right corner.
            color (tuple): The RGB color of the rectangle.
        """
        super().__init__(color)
        self.top_left = top_left
        self.bottom_right = bottom_right

    def draw(self, Canvas):
        """
        Draws the rectangle on the canvas.

        Parameters:
            Canvas (Canvas): The canvas to draw the rectangle on.
        """
        if self.top_left and self.bottom_right:
            cv.rectangle(Canvas.canvas, self.top_left,
                         self.bottom_right, self.color, self.thickness)

    def get_data(self):
        """
        Returns the data of the rectangle.

        Returns:
            dict: A dictionary containing the top-left and bottom-right corners.
        """
        return {
            'type': 'rectangle',
            'top_left': self.top_left,
            'bottom_right': self.bottom_right,
        }


class Polygon(Shape):
    """
    Represents a polygon shape with a list of points and a specified color.
    """

    def __init__(self, points, color):
        """
        Initializes the polygon with the given points and color.

        Parameters:
            points (list): A list of (x, y) points defining the polygon's vertices.
            color (tuple): The RGB color of the polygon.
        """
        super().__init__(color)
        self.points = np.array(points, dtype=np.int32).reshape((-1, 1, 2))

    def draw(self, canvas):
        """
        Draws the polygon on the canvas.

        Parameters:
            canvas (Canvas): The canvas to draw the polygon on.
        """
        cv.polylines(canvas.canvas, [self.points],
                     isClosed=True, color=self.color, thickness=2)

    def get_data(self):
        """
        Returns the data of the polygon.

        Returns:
            dict: A dictionary containing the list of points defining the polygon.
        """
        if len(self.points) > 0:
            return {
                'type': 'polygon',
                'points': np.array(self.points.tolist()),
            }
