import math
import cv2 as cv
import numpy as np
from Shapes import *
from UndoRedoManager import *


class DrawingTool:
    """
    A class for managing drawing actions (circle, rectangle, polygon) and other canvas interactions 
    like erasing, cropping, and rotating.
    """

    def __init__(self, canvas, shape_manager, undo_redo_manager, draw_color=(0, 0, 0)):
        """
        Initializes the DrawingTool with the given canvas, shape manager, undo-redo manager, and draw color.

        Args:
            canvas (Canvas): The canvas to draw on.
            shape_manager (ShapeManager): The manager for storing shapes.
            undo_redo_manager (UndoRedoManager): The manager for undo/redo operations.
            draw_color (tuple, optional): the color to use when drawing shapes, Defaults to (0, 0, 0).
        """
        self.canvas = canvas
        self.shape_manager = shape_manager
        self.undo_redo_manager = undo_redo_manager
        self.draw_color = draw_color
        self.temp_canvas = self.canvas.get_canvas()
        self.start_point = None
        self.drawing = False
        self.polygon_points = []
        self.crop_points = []
        self.eraser_size = 20
        self.is_erasing = False

    def draw_circle(self, event, x, y):
        """
        handels drawing a circle based on mouse events: starts drawing on left click, shows preview on mouse move, 
        and finalizes the circle on left release.

        Args:
            event (int): The type of mouse event (click, move, release).
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
        """
        if event == cv.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
        elif event == cv.EVENT_MOUSEMOVE and self.drawing:
            self.temp_canvas = self.canvas.get_canvas()
            # Calculate the distance between the startpoint and Curpoint
            radius = int(
                math.sqrt((x - self.start_point[0])**2 + (y - self.start_point[1])**2))
            # Draw temp preview circle for the current size
            cv.circle(self.temp_canvas, self.start_point,
                      radius, self.draw_color, 2)
            cv.imshow(self.canvas.canvas_name, self.temp_canvas)

        elif event == cv.EVENT_LBUTTONUP:
            self.drawing = False
            radius = int(
                math.sqrt((x - self.start_point[0])**2 + (y - self.start_point[1])**2))
            new_circle = Circle(self.start_point, radius, self.draw_color)
            self.shape_manager.add_shape(new_circle)
            self.canvas.reset_canvas()
            self.shape_manager.draw_all(self.canvas)
            self.undo_redo_manager.add_action(DrawAction(
                self.shape_manager.get_shapes(), self.canvas.get_canvas()))

    def draw_rectangle(self, event, x, y):
        """
        Draws a rectangle based on mouse events: starts drawing on left click, shows preview on mouse move, 
        and finalizes the rectangle on left release.

        Args:
            event (int): The type of mouse event (click, move, release).
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
        """
        if event == cv.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
        elif event == cv.EVENT_MOUSEMOVE and self.drawing:
            self.temp_canvas = self.canvas.get_canvas()
            cv.rectangle(self.temp_canvas, self.start_point,
                         (x, y), self.draw_color, 2)
            cv.imshow(self.canvas.canvas_name, self.temp_canvas)
        elif event == cv.EVENT_LBUTTONUP:
            self.drawing = False
            new_rect = Rectangle(self.start_point, (x, y), self.draw_color)
            self.shape_manager.add_shape(new_rect)
            self.canvas.reset_canvas()
            self.shape_manager.draw_all(self.canvas)
            self.undo_redo_manager.add_action(DrawAction(
                self.shape_manager.get_shapes(), self.canvas.get_canvas()))

    def draw_polygon(self, event, x, y):
        """
        Draws a polygon based on mouse events: adds points on left click and shows preview on mouse move.

        Args:
            event (int): The type of mouse event (click, move).
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
        """
        if event == cv.EVENT_LBUTTONDOWN:
            self.polygon_points.append((x, y))
            self.drawing = True
        elif event == cv.EVENT_MOUSEMOVE and len(self.polygon_points) > 0 and self.drawing:
            self.temp_canvas = self.canvas.get_canvas()
            if len(self.polygon_points) > 1:
                points = np.array(self.polygon_points,
                                  dtype=np.int32).reshape((-1, 1, 2))
                cv.polylines(self.temp_canvas, [
                             points], isClosed=False, color=self.draw_color, thickness=2)
            cv.line(self.temp_canvas,
                    self.polygon_points[-1], (x, y), self.draw_color, 2)
            cv.imshow(self.canvas.canvas_name, self.temp_canvas)

    def finalize_polygon(self):
        """
        Finalizes and adds the polygon to the canvas after closing the shape.
        """
        if len(self.polygon_points) > 2:
            self.drawing = False
            self.polygon_points.append(self.polygon_points[0])
            points = np.array(self.polygon_points,
                              dtype=np.int32).reshape((-1, 1, 2))
            cv.polylines(self.canvas.get_canvas(), [
                         points], isClosed=True, color=self.draw_color, thickness=2)
            polygon_shape = Polygon(self.polygon_points, self.draw_color)
            self.shape_manager.add_shape(polygon_shape)
            self.shape_manager.draw_all(self.canvas)
            self.undo_redo_manager.add_action(DrawAction(
                self.shape_manager.get_shapes(), self.canvas.get_canvas()))
        self.polygon_points = []

    def handle_erase_mode(self, event, x, y):
        """
        Handles the eraser mode, allowing the user to erase parts of the canvas by drawing over them.

        Args:
            event (int): The type of mouse event (click, move, release).
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
        """
        # center the eraser rect around the mouse
        half_size = self.eraser_size // 2
        top_left = (max(0, x - half_size), max(0, y - half_size))
        bottom_right = (min(self.canvas.width, x + half_size),
                        min(self.canvas.height, y + half_size))

        if event == cv.EVENT_LBUTTONDOWN:
            self.is_erasing = True
        elif event == cv.EVENT_LBUTTONUP:
            self.is_erasing = False
            self.undo_redo_manager.add_action(
                DrawAction(self.shape_manager.get_shapes(),
                           self.canvas.get_canvas())
            )
        self.temp_canvas = self.canvas.get_canvas()
        overlay = self.temp_canvas.copy()

        # Draw preview rectangle
        cv.rectangle(overlay, top_left, bottom_right, (200, 200, 200), -1)
        cv.addWeighted(overlay, 0.5, self.temp_canvas,
                       0.5, 0, self.temp_canvas)

        if event == cv.EVENT_MOUSEMOVE and self.is_erasing:
            # simply draw on the canvas with a solid box with the same color as background
            cv.rectangle(self.canvas.canvas, top_left,
                         bottom_right, (255, 255, 255), -1)

        # Display the canvas with preview
        cv.imshow(self.canvas.canvas_name, self.temp_canvas)

    def rotate_canvas(self, angle):
        """
        Rotates the canvas by the given angle (90 or -90).

        Args:
            angle (int): The angle to rotate the canvas by (90 or -90).
        """
        canvas = self.canvas.get_canvas()

        # rotation of any matrix : transpose and then flipping
        if angle == 90:
            rotated_canvas = cv.transpose(canvas)
            rotated_canvas = cv.flip(rotated_canvas, 1)  # flip horizontally
        elif angle == -90:
            rotated_canvas = cv.transpose(canvas)
            rotated_canvas = cv.flip(rotated_canvas, 0)  # flip vertically

        # update the canvas
        self.canvas.set_canvas(rotated_canvas)
        self.undo_redo_manager.add_action(
            DrawAction(self.shape_manager.get_shapes(),
                       self.canvas.get_canvas())
        )

    def handle_crop_mode(self, event, x, y):
        """
        Handles cropping mode, allowing the user to define a rectangular region to crop.

        Args:
            event (int): The type of mouse event (click, move).
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
        """
        if event == cv.EVENT_LBUTTONDOWN:
            # record the first point
            if len(self.crop_points) == 0:
                self.crop_points = [(x, y)]
            # record the second point and apply the crop
            elif len(self.crop_points) == 1:
                self.crop_points.append((x, y))
                self.apply_crop()

        elif event == cv.EVENT_MOUSEMOVE and len(self.crop_points) == 1:
            # temp canvas for preview
            self.temp_canvas = self.canvas.get_canvas()
            cv.rectangle(self.temp_canvas, self.crop_points[0], (x, y),
                         color=(0, 0, 255), thickness=2)
            cv.imshow(self.canvas.canvas_name, self.temp_canvas)
        else:
            # restore the original canvas
            cv.imshow(self.canvas.canvas_name, self.canvas.get_canvas())

    def apply_crop(self):
        """
        Applies the cropping operation, cutting the canvas based on the selected crop points.
        """
        if len(self.crop_points) == 2:
            (x1, y1), (x2, y2) = self.crop_points

            # ensure the coordinates are ordered correctly
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])
            cropped_canvas = self.canvas.get_canvas()[y1:y2, x1:x2]

            # Show the cropped region in a new window
            cv.imshow("Cropped Region", cropped_canvas)
            # Reset crop points
            self.crop_points = []
