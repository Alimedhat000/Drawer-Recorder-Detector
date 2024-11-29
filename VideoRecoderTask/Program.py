import cv2 as cv
import math
from ShapeManager import ShapeManager
from UndoRedoManager import *
from Shapes import *
from Cropper import Cropper
from Recorder import Recorder
from Canvas import *
from Drawer import *


class Program:
    """
    Class that manages the webcam feed, enabling users to draw shapes, crop the video, and record the output.

    Key Bindings:
        'q' : Quit the program
        'c' : Switch to circle drawing mode
        'r' : Switch to rectangle drawing mode
        'p' : Switch to polygon drawing mode
        's' : Finalize polygon drawing (for polygon mode)
        'x' : Enable cropping mode
        'e' : Switch to erase mode
        'a' : Rotate canvas counterclockwise by 90 degrees
        'd' : Rotate canvas clockwise by 90 degrees
        'z' : Undo the last action
        'y' : Redo the last undone action
        '1' : Start video recording
        '2' : Pause video recording
        '3' : Resume video recording
        '4' : Stop video recording    
    """

    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height
        self.cap = cv.VideoCapture(0)

        if width and height:
            self.cap.set(cv.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)
        else:
            # get the width of the webcam if the width is not specified
            self.width = int(self.cap.get(
                cv.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(
                cv.CAP_PROP_FRAME_HEIGHT))
        ret, first_frame = self.cap.read()
        self.canvas = Canvas(self.width, self.height, canvas=first_frame)
        self.cropper = Cropper()
        self.shape_manager = ShapeManager()
        self.undo_redo_manager = UndoRedoManager()
        self.draw_color = (255, 255, 255)
        self.video_recorder = Recorder(output_dir="./Records")
        self.drawer_tool = DrawingTool(
            self.canvas, self.shape_manager, self.undo_redo_manager)
        self.undo_redo_manager.add_action(
            DrawAction(self.shape_manager.get_shapes(), self.canvas.get_canvas()))
        self.active_mode = None

    def run(self):
        cv.namedWindow(self.canvas.canvas_name)
        cv.setMouseCallback(self.canvas.canvas_name, self._mouse_callback)

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Unable to read from camera.")
                break
            frame = self.cropper.apply_crop(frame)
            self.canvas.set_canvas(frame)
            self.shape_manager.draw_all(self.canvas)
            self.drawer_tool.rotate_canvas()
            self.canvas.draw_canvas()

            if self.video_recorder.is_recording and not self.video_recorder.is_paused:
                self.video_recorder.write_frame(self.canvas.get_canvas())

            key = cv.waitKey(1)

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
                self.cropper.select_crop_region(self.cap)
            elif key == ord('e'):
                self.active_mode = "erase"
            elif key == ord('a'):
                self.drawer_tool.rotation_angle -= 90
            elif key == ord('d'):
                self.drawer_tool.rotation_angle += 90
            elif key == ord('z'):
                self.undo_redo_manager.undo(self.canvas, self.shape_manager)
            elif key == ord('y'):
                self.undo_redo_manager.redo(self.canvas, self.shape_manager)
            elif key == ord('1'):  # Start recording
                self.video_recorder.start_recording(self.width, self.height)
            elif key == ord('2'):  # Pause recording
                self.video_recorder.pause_recording()
            elif key == ord('3'):  # Resume recording
                self.video_recorder.resume_recording()
            elif key == ord('4'):  # Stop recording
                self.video_recorder.stop_recording()
        self.cleanup()

    def _mouse_callback(self, event, x, y, flags, param):
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

    def handle_keys(self, key):
        if key == ord('s'):  # Start recording
            self.video_recorder.start_recording(self.width, self.height)
        elif key == ord('p'):  # Pause recording
            self.video_recorder.pause_recording()
        elif key == ord('r'):  # Resume recording
            self.video_recorder.resume_recording()
        elif key == ord('q'):  # Stop recording
            self.video_recorder.stop_recording()
        elif key == ord('x'):  # Enable cropping
            self.cropper.select_crop_region(self.cap)
        elif key == ord('d'):  # Draw shape
            self.shape_manager.add_shape('rectangle', (50, 50), (200, 150))

    def cleanup(self):
        self.cap.release()
        cv.destroyAllWindows()
