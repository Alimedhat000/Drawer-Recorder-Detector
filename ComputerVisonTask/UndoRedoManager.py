import cv2 as cv


class UndoRedoManager:
    """ A class to manage undo and redo actions for a canvas and shape manager."""

    def __init__(self, max_history=10):
        """
        Initializes the UndoRedoManager with an optional maximum history limit.

        Parameters:
            max_history (int): The maximum number of actions to store. Default is 10.
        """
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = max_history

    def add_action(self, action):
        """
        Adds an action to the undo stack. If the stack exceeds the max history,
        the oldest action is removed, and the redo stack is cleared.

        Parameters:
            action (DrawAction): The action to be added to the undo stack.
        """
        self.undo_stack.append(action)
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self, canvas, shape_manager):
        """
        Undoes the most recent action, restoring the previous state of the canvas and shape manager.

        Parameters:
            canvas (Canvas): The canvas to restore.
            shape_manager (ShapeManager): The shape manager to restore.
        """
        if len(self.undo_stack) > 1:  # Need at least 2 states to undo
            # Pop current state
            current_state = self.undo_stack.pop()
            # Store it in redo stack
            self.redo_stack.append(current_state)

            # Get previous state
            prev_state = self.undo_stack[-1]

            # Restore previous state
            canvas.set_canvas(prev_state.canvas_state)
            shape_manager.set_shapes(prev_state.shapes_state.copy())

    def redo(self, canvas, shape_manager):
        """
        Redoes the most recent undone action, restoring the next state of the canvas and shape manager.

        Parameters:
            canvas (Canvas): The canvas to restore.
            shape_manager (ShapeManager): The shape manager to restore.
        """
        if self.redo_stack:
           # Get next state from redo stack
            next_state = self.redo_stack.pop()
            self.undo_stack.append(next_state)

            # Apply the redo state
            canvas.set_canvas(next_state.canvas_state)
            shape_manager.set_shapes(next_state.shapes_state.copy())


class DrawAction:
    """
    A class representing an action that can be undone or redone.
    """

    def __init__(self, shapemanager=None, canvas=None):
        """
        Initializes a DrawAction with the given shape manager and canvas state.

        Parameters:
            shapemanager (ShapeManager): The current state of the shape manager.
            canvas (Canvas): The current state of the canvas.
        """
        self.shapes_state = shapemanager
        self.canvas_state = canvas
