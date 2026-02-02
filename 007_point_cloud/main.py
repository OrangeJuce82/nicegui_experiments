import numpy as np
from nicegui import ui

# Configuration - adjust grid_size to change number of points
# grid_size = 20 -> 400 points
# grid_size = 50 -> 2500 points
# grid_size = 100 -> 10000 points
GRID_SIZE = 30
FPS = 50

# Animation state
time = 0.0

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

# Create a 3D scene with show_stats=True
with ui.scene(show_stats=True, fps=FPS).classes('w-full h-96') as scene:
    # Create point cloud
    point_cloud = scene.point_cloud(positions.tolist(), colors.tolist(), point_size=0.15)

# Timer to animate points (throttled to 30 FPS to avoid websocket bottleneck)
def animate_points():
    global time
    time += 0.05
    
    # Only update Z coordinates (in-place modification)
    positions[:, 2] = np.sin(X_flat * 1.0 + time) * np.cos(Y_flat * 1.0 + time) + 1
    
    # Update point cloud with new positions
    point_cloud.set_points(positions.tolist(), colors.tolist())

ui.timer(1.0 / FPS, animate_points)

ui.run()
