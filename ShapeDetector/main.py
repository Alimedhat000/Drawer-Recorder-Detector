import cv2 as cv
from ShapeDetector import ShapeDetector

if __name__ == "__main__":
    #! To process a static image put path
    detector = ShapeDetector(file_path="shapes.png")
    detector.detect_shapes()

    #! To proccess instance of canvas
    # detector = ShapeDetector(canvas=Canvas.canvas)
    # detector.detect_shapes()

    #! To process video (live camera or file)
    # Use 0 for live camera, or a file path for videos
    # detector = ShapeDetector(video_source=0)
    # detector.detect_shapes_in_video()
    # cv.waitKey(0)
    # cv.destroyAllWindows()
