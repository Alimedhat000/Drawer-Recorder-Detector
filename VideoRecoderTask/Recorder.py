import cv2 as cv
import os
from datetime import datetime


class Recorder:
    """
    A class that provides functionality for recording video from a camera.
    """

    def __init__(self, output_dir="./Records"):
        """
        Initializes the Recorder object.

        Args:
            output_dir (str): Directory where recorded videos will be saved. Defaults to './Records'.
        """
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        self.video_writer = None
        self.is_recording = False
        self.is_paused = False
        self.current_filename = None

    def start_recording(self, width, height, fps=60):
        """
        Starts recording video to a file with the given resolution and frame rate.

        Args:
            width (int): The width of the video frame.
            height (int): The height of the video frame.
            fps (int, optional): Frames per second for the recording. Defaults to 60.
        """
        if not self.is_recording:
            # Generate a unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_filename = os.path.join(
                self.output_dir, f"recording_{timestamp}.avi")

            # Define the codec and create VideoWriter object
            fourcc = cv.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv.VideoWriter(
                self.current_filename, fourcc, fps, (width, height))

            self.is_recording = True
            self.is_paused = False
            print(f"Started recording to {self.current_filename}")

    def stop_recording(self):
        """
        Stops the video recording and saves the video file.

        If recording is in progress, it releases the VideoWriter object, stops the recording,
        and prints the location where the video was saved.
        """
        if self.is_recording and self.video_writer:
            self.video_writer.release()
            self.is_recording = False
            self.is_paused = False
            print(f"Stopped recording. Video saved to {self.current_filename}")

    def pause_recording(self):
        """
        Pauses the video recording.

        If recording is in progress and not already paused, it pauses the recording and
        prints a message indicating that the recording has been paused.
        """
        if self.is_recording and not self.is_paused:
            self.is_paused = True
            print("Recording paused")

    def resume_recording(self):
        """
        Resumes the paused video recording.

        If recording is in progress and paused, it resumes the recording and prints a message
        indicating that the recording has resumed.
        """
        if self.is_recording and self.is_paused:
            self.is_paused = False
            print("Recording resumed")

    def write_frame(self, frame):
        """
        Writes a single frame to the video file.

        Args:
            frame (numpy.ndarray): The frame to be written to the video file.

        If recording is in progress and not paused, the frame is written to the video file.
        """
        if self.is_recording and not self.is_paused and self.video_writer:
            self.video_writer.write(frame)
