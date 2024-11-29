
from DrawerProgram import Drawer

if __name__ == "__main__":
    try:
        width = int(input("Enter canvas width: "))
        height = int(input("Enter canvas height: "))

        if width <= 0 or height <= 0:
            raise ValueError("Canvas dimensions must be positive integers.")

        color_input = input(
            "Enter canvas background color in BGR format (e.g., 255,255,255): "
        )
        color_parts = color_input.split(',')

        if len(color_parts) != 3:
            raise ValueError(
                "Color must have exactly three components (B, G, R).")
        color = tuple(map(int, color_parts))
        if not all(0 <= c <= 255 for c in color):
            raise ValueError("Color components must be in the range 0-255.")

        app = Drawer(width, height, color)
        app.run()

    except ValueError as e:
        print(f"Invalid input: {e} \nRunning with Default values")
        app = Drawer()
        app.run()
    except Exception as e:
        print(f"An unexpected error occurred: {
              e} \nRunning with Default values")
        app = Drawer()
        app.run()
