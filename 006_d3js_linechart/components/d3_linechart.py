from pathlib import Path

from nicegui import ui


class D3LineChart(
    ui.element,
    component="d3_linechart.js",
):
    def __init__(self, data: list = None, width: int = None, height: int = None):
        super().__init__()
        self._props["data"] = data or []
        self._props["width"] = width
        self._props["height"] = height

    @property
    def data(self):
        return self._props["data"]

    @data.setter
    def data(self, value):
        self._props["data"] = value
        self.update()

    def set_data(self, data: list):
        """Set new data for the chart."""
        self.data = data

    @property
    def width(self):
        return self._props["width"]

    @width.setter
    def width(self, value):
        self._props["width"] = value
        self.update()

    @property
    def height(self):
        return self._props["height"]

    @height.setter
    def height(self, value):
        self._props["height"] = value
        self.update()
