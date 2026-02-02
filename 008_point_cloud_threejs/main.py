import numpy as np
from nicegui import ui

from components import ThreejsPointCloud

# Configuration - adjust grid_size to change number of points
# grid_size = 20 -> 400 points
# grid_size = 50 -> 2500 points
# grid_size = 100 -> 10000 points
GRID_SIZE = 50
FPS = 60

# Create meshgrid once (X and Y are fixed)
X, Y = np.meshgrid(np.linspace(-3, 3, GRID_SIZE), np.linspace(-3, 3, GRID_SIZE))
X_flat = X.flatten()
Y_flat = Y.flatten()
num_points = len(X_flat)

# Pre-allocate arrays for positions and colors
positions = np.zeros((num_points, 3), dtype=np.float32)
positions[:, 0] = X_flat  # X coordinates (fixed)
positions[:, 1] = Y_flat  # Y coordinates (fixed)

colors = np.zeros((num_points, 3), dtype=np.float32)
colors[:, 0] = (X_flat + 3) / 6
colors[:, 1] = (Y_flat + 3) / 6
colors[:, 2] = 0.5

# Create the Three.js point cloud component with FPS configuration
# Animation is handled entirely in JavaScript
point_cloud = ThreejsPointCloud(
    positions=positions, 
    colors=colors, 
    point_size=0.15,
    fps=FPS
)
point_cloud.classes('w-full h-96')

ui.run()
