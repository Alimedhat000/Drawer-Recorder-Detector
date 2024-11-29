import cv2 as cv


class Cropper:
    """
    A class for interactively selecting a rectangular region of interest (ROI) from a video feed or image 
    using mouse events and applying the crop to the frame.
    """

    def __init__(self):
        """
        Initializes the Cropper instance with default values.

        Sets up initial values for crop_points, drawing state, and mouse tracking.
        """
        self.crop_points = None  # ((x1, y1), (x2, y2))
        self.drawing = False
        self.start_point = None
        self.current_point = None  # To track the mouse's current position

    def mouse_callback(self, event, x, y, flags, param):
        """
        Callback function to handle mouse events.

        Updates the crop region based on mouse input (left-click to start, drag to define, and left-click release to finalize).

        Args:
            event (int): The type of mouse event.
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
            flags (int): Any flags related to the event.
            param (any): Additional Args passed to the callback function.
        """
        if event == cv.EVENT_LBUTTONDOWN:
            # Start drawing
            self.start_point = (x, y)
            self.drawing = True
            self.current_point = (x, y)

        elif event == cv.EVENT_MOUSEMOVE:
            # Update current point while dragging
            if self.drawing:
                self.current_point = (x, y)

        elif event == cv.EVENT_LBUTTONUP:
            # Finish drawing
            if self.drawing:
                end_point = (x, y)
                x1 = min(self.start_point[0], end_point[0])
                y1 = min(self.start_point[1], end_point[1])
                x2 = max(self.start_point[0], end_point[0])
                y2 = max(self.start_point[1], end_point[1])

                self.crop_points = (x1, y1, x2 - x1, y2 - y1)
                self.drawing = False
                self.start_point = None
                self.current_point = None

    def select_crop_region(self, cap):
        """
        Opens a window to allow the user to select a rectangular crop region in the video frame.

        The user can click and drag to define the region and press Enter to confirm or 'q' to exit without cropping.

        Args:
            cap (cv.VideoCapture): A cv.VideoCapture object used to capture the video frame.

        Returns:
            tuple or None: The crop region as a tuple (x, y, width, height) if selected, or None if the user exits.
        """
        print("Select crop region by clicking and dragging.")
        print("Left-click and drag to define the region.")
        print("Press Enter to confirm selection.")
        print("Press 'q' to exit without selecting.")

        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            return None

        # Create a copy of the frame for drawing
        display_frame = frame.copy()

        # Create window and set mouse callback
        cv.namedWindow("Select Crop Region")
        cv.setMouseCallback("Select Crop Region", self.mouse_callback)

        while True:
            # Create a copy of the display frame for drawing
            show_frame = display_frame.copy()

            # If currently drawing, show the current selection rectangle
            if self.drawing and self.start_point and self.current_point:
                cv.rectangle(
                    show_frame,
                    self.start_point,
                    self.current_point,
                    (0, 255, 0), 2
                )

            # If crop points are set, show the selected region
            if self.crop_points:
                x, y, w, h = self.crop_points
                cv.rectangle(show_frame, (x, y),
                             (x + w, y + h), (0, 0, 255), 2)

            # Display the frame
            cv.imshow("Select Crop Region", show_frame)

            # Wait for key press
            key = cv.waitKey(1) & 0xFF

            # Confirm selection with Enter key
            if key == 13 and self.crop_points:
                break

            # Exit if 'q' is pressed
            elif key == ord('q'):
                self.crop_points = None
                break

        # Close the selection window
        cv.destroyWindow("Select Crop Region")
        return self.crop_points

    def apply_crop(self, frame):
        """
        Applies the crop region to the provided frame and returns the cropped image.

        Args:
            frame (np.ndarray): The input frame from which the crop region will be extracted.

        Returns:
            np.ndarray: The cropped image based on the selected crop region.
        """
        if self.crop_points:
            x, y, w, h = map(int, self.crop_points)
            return frame[y:y + h, x:x + w]
        return frame
