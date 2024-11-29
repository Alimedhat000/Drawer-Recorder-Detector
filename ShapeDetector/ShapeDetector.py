import cv2 as cv
from Canvas import *
from ShapeManager import *
from Shapes import *


class ShapeDetector:
    """
    Detects shapes (circles, rectangles, polygons) in images or video streams.
    """

    # Constants for thresholds and parameters
    MIN_AREA_THRESHOLD = 500  # Minimum area to consider a valid shape
    TRIANGLE_APPROX_EPSILON_RATIO = 0.02  # Epsilon ratio for contour approximation
    THRESHOLD_BINARY = 120  # Threshold for binary thresholding
    CIRCLE_MIN_RADIUS = 10  # Minimum radius for HoughCircles
    CIRCLE_MAX_RADIUS = 100  # Maximum radius for HoughCircles
    # First parameter for HoughCircles (Higher threshold for the edge detector
    # lower threshold is automatically set to half of this value.)
    CIRCLE_PARAM1 = 100

    # Second parameter for HoughCircles (The accumulator threshold for circle detection.
    # A smaller value means more false positives,
    # while a larger value means fewer detections but higher confidence.)
    CIRCLE_PARAM2 = 30
    BLUR_KERNEL_SIZE_CIRCLE = (9, 9)  # GaussianBlur kernel size for circles
    # GaussianBlur kernel size for contour shapes
    BLUR_KERNEL_SIZE_CONTOUR = (5, 5)
    ASPECT_RATIO_THRESHOLD = 0.1  # Threshold to distinguish square from rectangle

    def __init__(self, file_path=None, canvas=None, video_source=None):
        """
        Initializes the shape detector with an image file, video source, or existing canvas.

        Parameters:
            file_path (str, optional): The file path to an image for shape detection.
            canvas (np.ndarray, optional): A canvas (image) for shape detection.
            video_source (str, optional): The video source (filepath or cam) for real-time shape detection.
        """
        if file_path:
            self.file_path = file_path
            self.original = cv.imread(file_path)

            # Ensure the file was read correctly
            if self.original is None:
                raise FileNotFoundError(
                    f"File not found or could not be loaded: {file_path}")

            self.height, self.width = self.original.shape[:2]
            self.canvas = Canvas(
                self.width, self.height, canvas=self.original)
            self.shape_manager = ShapeManager()
        elif video_source:
            self.cap = cv.VideoCapture(video_source)
            if not self.cap.isOpened():
                raise ValueError("Error: Cannot open video source.")
            self.width = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))
            self.canvas = Canvas(self.width, self.height)
            self.shape_manager = ShapeManager()
        elif canvas:
            self.height, self.width = canvas.shape[:2]
            self.canvas = Canvas(self.width, self.height, canvas=canvas)
            self.shape_manager = ShapeManager()

    def detect_shapes(self):
        """
        Detects shapes in the provided image and adds them to the shape manager.
        """
        # Convert to grayscale for shape detection
        gray_image = cv.cvtColor(self.original, cv.COLOR_BGR2GRAY)

        # Blur images for detecting different shapes
        circle_blurred = cv.GaussianBlur(
            gray_image, self.BLUR_KERNEL_SIZE_CIRCLE, 2
        )
        basic_blurred = cv.GaussianBlur(
            gray_image, self.BLUR_KERNEL_SIZE_CONTOUR, 0
        )

        # Detect circles using HoughCircles
        circles = cv.HoughCircles(
            circle_blurred,
            cv.HOUGH_GRADIENT,
            dp=1,
            minDist=self.height / 8,  # min dist between centers
            param1=self.CIRCLE_PARAM1,
            param2=self.CIRCLE_PARAM2,
            minRadius=self.CIRCLE_MIN_RADIUS,
            maxRadius=self.CIRCLE_MAX_RADIUS,
        )
        detected_centers = set()
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for x, y, r in circles[0]:
                detected_centers.add((x, y))
                self.shape_manager.add_shape(Circle((x, y), r, (0, 0, 255)))

        # Detect contours for polygons and rectangles
        _, thresh_image = cv.threshold(
            basic_blurred,
            self.THRESHOLD_BINARY,
            255,
            cv.THRESH_BINARY,
        )

        # cv.imshow("Thresholded Image", thresh_image)
        contours, _ = cv.findContours(
            thresh_image,
            cv.RETR_LIST,  # retrieves all contours
            cv.CHAIN_APPROX_SIMPLE,
        )

        for contour in contours:
            area = cv.contourArea(contour)
            # Ignore small shapes and areas close to the image area
            if self.MIN_AREA_THRESHOLD < area < (self.width * self.height) - 10000:
                # arclength computes the area of the contour and true for closed contour
                epsilon = self.TRIANGLE_APPROX_EPSILON_RATIO * \
                    cv.arcLength(contour, True)
                # approximates the countor to a simple polygon
                # approx is the number of points
                approx = cv.approxPolyDP(contour, epsilon, True)

                x, y, w, h = cv.boundingRect(contour)
                if len(approx) == 3:  # Triangle
                    tri_points = approx[:, 0].tolist()
                    self.shape_manager.add_shape(
                        Polygon(tri_points, (255, 0, 0))
                    )
                elif len(approx) == 4:  # Square
                    self.shape_manager.add_shape(
                        Rectangle((x, y), (x + w, y + h), (0, 255, 255))
                    )

        self.draw_detected_shapes()
        self.draw_labels()
        self.show_detected_shapes()

    def detect_shapes_in_video(self):
        """
        Detects shapes in a video stream and displays the results in real-time.
        The video is processed frame-by-frame to detect shapes and display them.
        """
        if not hasattr(self, 'cap') or self.cap is None:
            raise ValueError("No video source provided for shape detection.")

        while True:
            ret, frame = self.cap.read()
            if not ret:  # Break if no frame is captured
                break

            # Use the current frame as the canvas
            self.original = frame.copy()
            self.canvas.set_canvas(frame)
            self.shape_manager = ShapeManager()  # Reset for each frame
            self.detect_shapes()

            # Exit on pressing 'q'
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        # Release video capture and close windows
        self.cap.release()
        cv.destroyAllWindows()

    def draw_labels(self):
        """
        Draws labels (e.g., 'Circle', 'Square', 'Triangle') on the detected shapes.
        """
        for shape in self.shape_manager.get_shapes():
            shape_data = shape.get_data()
            text_position = None

            if shape_data['type'] == 'rectangle':
                # Place text near the center of the rectangle
                top_left = shape_data['top_left']
                bottom_right = shape_data['bottom_right']
                text_position = (top_left[0] - 10, top_left[1] - 10)
                label = "Square"

            elif shape_data['type'] == 'circle':
                center = shape_data['center']
                radius = shape_data['radius']
                # Place text at the center of the circle
                text_position = (center[0] - radius - 10,
                                 center[1] - radius - 10)
                label = "Circle"

            elif shape_data['type'] == 'polygon':
                points = shape_data['points']
                # Calculate bounding box for the polygon
                x, y, w, h = cv.boundingRect(points)
                # Place the text at the top-left of the bounding box
                text_position = (x - 10, y - 10)
                if len(points == 3):
                    label = "Triangle"
                else:
                    label = "Polygon"

            # Draw the text on the canvas
            if text_position:
                cv.putText(
                    self.canvas.canvas,
                    label,
                    text_position,
                    cv.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=(0, 0, 0),  # Black text
                    thickness=1
                )

    def draw_detected_shapes(self):
        """Draw detected shapes on the canvas."""
        self.shape_manager.draw_all(self.canvas)

    def show_detected_shapes(self):
        """Display the canvas with detected shapes."""
        cv.imshow(self.canvas.canvas_name, self.canvas.canvas)
        cv.waitKey(0)
        cv.destroyAllWindows()
