from pathlib import Path

from nicegui import ui


class GameOfLife(
    ui.element,
    component="game_of_life.js",
):
    def __init__(self):
        # A 'Game Of Life' canvas
        super().__init__()
        self.add_resource(Path(__file__).parent.parent / "libs")
        self._props["speed"]: float = 1.0
        self._props["playing"]: bool = False
        self._props["drawing"]: str = "pencil"
        self._props["hex_color"]: str = "#5893a8"

        # Add event listener
        self.generation_num = 0
        ui.on("gol__generation_num", lambda e: setattr(self, "generation_num", e.args))

    def init_grid(self, mode: str = None, *args, **kwarg):
        self.drawing = "pencil"
        self.run_method("init_grid", mode)

    @property
    def speed(self):
        return self._props["speed"]

    @speed.setter
    def speed(self, value):
        self._props["speed"] = min(4.0, max(0.25, float(value)))
        self.update()

    def decrease_speed(self, *args, **kwarg):
        self.speed /= 2

    def increase_speed(self, *args, **kwarg):
        self.speed *= 2

    @property
    def playing(self):
        return self._props["playing"]

    @playing.setter
    def playing(self, value: bool):
        self._props["playing"] = value
        self.update()

    def toggle_play(self, *args, **kwarg):
        self.playing = not self.playing

    def generate_next_grid(self, *args, **kwarg):
        self.playing = False
        self.run_method("generate_next_grid_then_draw")

    @property
    def drawing(self):
        return self._props["drawing"]

    @drawing.setter
    def drawing(self, value: bool):
        self._props["drawing"] = value
        self.update()

    def use_pencil(self, *args, **kwarg):
        self.drawing = "pencil"

    def use_eraser(self, *args, **kwarg):
        self.drawing = "eraser"

    @property
    def hex_color(self):
        return self._props["hex_color"]

    @hex_color.setter
    def hex_color(self, value):
        self._props["hex_color"] = value
        self.update()

    def set_hex_color(self, hex_color: str = None):
        self.hex_color = hex_color or "#5893a8"  # the default color
