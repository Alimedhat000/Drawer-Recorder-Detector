import cv2 as cv
import numpy as np


class Canvas:
    """
    Represents a drawing canvas with specified width, height, 
    and background color, providing methods to draw and reset the canvas.
    """

    def __init__(self, width, height, backgroundColor=(255, 255, 255), canvas=None, canvas_name="Canvas"):
        """
        Initializes the canvas with the given dimensions and background color.

        Parameters:
            width (int): The width of the canvas.
            height (int): The height of the canvas.
            backgroundColor (tuple): The RGB color tuple for the background color.
            canvas (np.ndarray, optional): An existing canvas to use instead of creating a new one.
        """
        self.width = width
        self.height = height
        self.backgroundColor = backgroundColor
        if canvas is not None:
            self.canvas = canvas
        else:
            self.canvas = self._create_blank_canvas()
        self.canvas_name = canvas_name

    def _create_blank_canvas(self):
        """
        Creates a blank canvas of the specified size with the background color.

        Returns:
            np.ndarray: A NumPy array representing the blank canvas.
        """
        return np.full((self.height, self.width, 3), self.backgroundColor, dtype=np.uint8)

    def draw_canvas(self):
        """Displays the canvas in a window."""

        cv.imshow(self.canvas_name, self.canvas)

    def reset_canvas(self):
        """Resets the canvas to a blank state with the initial background color."""

        self.canvas = self._create_blank_canvas()

    def get_canvas(self):
        """
        Returns a copy of the current canvas.

        Returns:
            np.ndarray: A copy of the canvas.
        """
        return self.canvas.copy()

    def set_canvas(self, newCanvas):
        """
        Sets the canvas value to new canvas.

        Parameters:
            newCanvas (np.ndarray): The new canvas to be set.
        """
        self.canvas = newCanvas
