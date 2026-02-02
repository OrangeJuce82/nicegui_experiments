import numpy as np
from nicegui import ui
from pathlib import Path


class ThreejsPointCloud(
    ui.element,
    component="threejs_pointcloud.js",
):
    def __init__(self, positions: np.ndarray, colors: np.ndarray, point_size: float = 0.15, fps: int = 60):
        """Initialize the Three.js point cloud component.

        Args:
            positions: numpy array of shape (n, 3) with x, y, z coordinates
            colors: numpy array of shape (n, 3) with r, g, b values (0-1)
            point_size: size of each point
            fps: target frames per second for animation (default: 60)
        """
        super().__init__()
        self.add_resource(Path(__file__).parent)

        # Convert numpy arrays to lists for JSON serialization
        self._props['positions'] = positions.tolist()
        self._props['colors'] = colors.tolist()
        self._props['pointSize'] = float(point_size)
        self._props['fps'] = int(fps)

    def update_positions(self, positions: np.ndarray):
        """Update point positions directly on the Three.js geometry."""
        self._props['positions'] = positions.tolist()
        self.run_method('updatePositions', positions.tolist())

    def update_colors(self, colors: np.ndarray):
        """Update point colors."""
        self._props['colors'] = colors.tolist()
        self.run_method('updateColors', colors.tolist())
