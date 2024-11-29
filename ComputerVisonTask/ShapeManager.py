import cv2 as cv
import numpy as np


class ShapeManager:
    """
    Manages a collection of shapes and provides functionality
    to add, remove, and draw shapes on a canvas.
    """

    def __init__(self):
        self.shapes = []

    def add_shape(self, Shape):
        """
        Adds a shape to the shape manager.

        Parameters:
            Shape (Shape): The shape object to be added.
        """
        self.shapes.append(Shape)

    def remove_shape(self, Shape):
        """
        Removes a shape from the shape manager if it exists.

        Parameters:
            Shape (Shape): The shape object to be removed.
        """
        if Shape in self.shapes:
            self.shapes.remove(Shape)

    def draw_all(self, canvas):
        """
        Draws all the shapes in the shape manager on the provided canvas.

        Parameters:
            canvas (Canvas): The canvas where shapes will be drawn.
        """
        for shape in self.shapes:
            shape.draw(canvas)

    def set_shapes(self, shapes):
        """
        Sets a new list of shapes.

        Parameters:
            shapes (list): A list of Shape objects to replace the current ones.
        """
        self.shapes = shapes

    def get_shapes(self):
        """
        Returns a copy of the current list of shapes.

        Returns: list: A copy of the list of shapes.
        """
        return self.shapes.copy()
