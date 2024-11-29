from Canvas import Canvas
from ShapeManager import ShapeManager
from Shapes import *
from UndoRedoManager import *
from Drawer import *
import cv2 as cv


class Drawer:
    """
    The Drawer class manages a drawing canvas, allowing users to draw shapes, erase parts of the canvas,
    crop sections, and perform other drawing-related actions. It provides an interactive interface using OpenCV
    and supports undo/redo functionality.

    Attributes:
        canvas (Canvas): The canvas on which the drawing is performed.
        draw_color (tuple): The color used for drawing shapes.
        shape_manager (ShapeManager): Manages all the shapes drawn on the canvas.
        undo_redo_manager (UndoRedoManager): Manages undo and redo actions for shapes.
        drawer_tool (DrawingTool): Tool that handles shape drawing, erasing, and cropping.
        active_mode (str): The current drawing mode (e.g., circle, rectangle, polygon).
    """

    def __init__(self, width=800, height=800, background=(255, 255, 255)):
        """
        Initializes the drawing application with a canvas, shape manager, undo/redo manager, 
        and a drawing tool for handling shapes.

        Args:
            width (int): The width of the canvas.
            height (int): The height of the canvas.
            background (tuple): The background color of the canvas.
        """
        self.canvas = Canvas(width, height, background)
        self.draw_color = self._get_opposite_color(background)
        self.shape_manager = ShapeManager()
        self.undo_redo_manager = UndoRedoManager()
        self.drawer_tool = DrawingTool(
            self.canvas, self.shape_manager, self.undo_redo_manager, self.draw_color)
        self.active_mode = None
        self.undo_redo_manager.add_action(DrawAction(
            self.shape_manager.get_shapes(), self.canvas.get_canvas()))

    def run(self):
        """
        Starts the drawing application and listens for keyboard and mouse events to 
        interactively draw shapes, crop, erase, rotate the canvas, and manage undo/redo actions.

        This method runs an OpenCV window that responds to user inputs and updates the canvas.
        """
        cv.namedWindow(self.canvas.canvas_name)
        cv.setMouseCallback(self.canvas.canvas_name, self._mouse_callback)

        while True:
            self.canvas.draw_canvas()
            key = cv.waitKey()

            if key == ord('q'):
                break
            elif key == ord('c'):
                self.active_mode = "circle"
            elif key == ord('r'):
                self.active_mode = "rectangle"
            elif key == ord('p'):
                self.active_mode = "polygon"
            elif key == ord('s') and self.active_mode == "polygon":
                self.drawer_tool.finalize_polygon()
            elif key == ord('x'):
                self.active_mode = "crop"
            elif key == ord('e'):
                self.active_mode = "erase"
            elif key == ord('a'):
                self.drawer_tool.rotate_canvas(-90)
            elif key == ord('d'):
                self.drawer_tool.rotate_canvas(90)
            elif key == ord('z'):
                self.undo_redo_manager.undo(self.canvas, self.shape_manager)
            elif key == ord('y'):
                self.undo_redo_manager.redo(self.canvas, self.shape_manager)
        cv.destroyAllWindows()

    def _get_opposite_color(self, bgr):
        """
        Calculates the opposite color of the given background color by inverting the RGB values.

        Args:
            bgr (tuple): The background color in BGR format.

        Returns:
            tuple: The opposite color in BGR format.
        """
        return tuple(255 - c for c in bgr)

    def _mouse_callback(self, event, x, y, flags, param):
        """
        Handles mouse events for drawing shapes, erasing, cropping, and other actions based on 
        the active drawing mode. It calls the appropriate method from the DrawingTool.

        Args:
            event (int): The OpenCV mouse event type.
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
            flags (int): The OpenCV event flags.
            param: Additional parameters passed to the callback (not used).
        """
        # Call the corresponding function for the current mode
        if self.active_mode == "polygon":
            self.drawer_tool.draw_polygon(event, x, y)
        elif self.active_mode == "crop":
            self.drawer_tool.handle_crop_mode(event, x, y)
        elif self.active_mode == "erase":
            self.drawer_tool.handle_erase_mode(event, x, y)
        elif self.active_mode == "circle":
            self.drawer_tool.draw_circle(event, x, y)
        elif self.active_mode == "rectangle":
            self.drawer_tool.draw_rectangle(event, x, y)
