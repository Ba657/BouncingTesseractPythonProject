import win32gui
import win32con
import ctypes
import time
import math

# Get desktop dimensions
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
desktop_width = user32.GetSystemMetrics(0)
desktop_height = user32.GetSystemMetrics(1)

# Get desktop device context
hdc_screen = win32gui.GetDC(0)

# Hypercube parameters
outer_cube_size = 100
inner_cube_size = 50
center_x = desktop_width // 2  # Starting position (x, center of screen)
center_y = desktop_height // 2  # Starting position (y, center of screen)
velocity_x = 3  # Horizontal velocity
velocity_y = 3  # Vertical velocity
angle_x = 0     # Rotation angle around the X-axis
angle_z = 0     # Rotation angle around the Z-axis

# Collision and icon tracking
collision_count = 0  # Tracks wall collisions
current_icon_index = 0  # Tracks current icon
icons = [
    win32con.IDI_ERROR,
    win32con.IDI_INFORMATION,
    win32con.IDI_QUESTION,
    win32con.IDI_WARNING,
    win32con.IDI_APPLICATION
]  # List of standard icons

def project_3d(x, y, z):
    """Project 3D coordinates onto 2D plane."""
    distance = 500
    factor = distance / (distance + z)
    x_2d = center_x + int(x * factor)
    y_2d = center_y - int(y * factor)
    return x_2d, y_2d

def draw_icons_along_line(hdc, x1, y1, x2, y2, icon):
    """Place icons along a line from (x1, y1) to (x2, y2)."""
    icon_size = 32

    # Calculate distance and number of icons needed
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    num_icons = int(distance // icon_size)

    # Calculate direction vector
    dx = (x2 - x1) / distance
    dy = (y2 - y1) / distance

    # Place icons along the line
    for i in range(num_icons + 1):
        icon_x = int(x1 + i * icon_size * dx)
        icon_y = int(y1 + i * icon_size * dy)
        win32gui.DrawIcon(hdc, icon_x, icon_y, icon)

def draw_hypercube_with_icon_edges(hdc, outer_size, inner_size, angle_x, angle_z, icon):
    """Draw a hypercube (nested cubes) with dynamic tilting and edges covered in icons."""
    def rotate_and_project(vertices):
        """Helper function to rotate and project vertices."""
        rotated = []
        for x, y, z in vertices:
            # Apply tilting rotation (X-axis and Z-axis)
            y_rotated = y * math.cos(angle_x) - z * math.sin(angle_x)
            z_rotated = y * math.sin(angle_x) + z * math.cos(angle_x)
            x_rotated = x * math.cos(angle_z) - z_rotated * math.sin(angle_z)
            z_rotated = x * math.sin(angle_z) + z_rotated * math.cos(angle_z)
            rotated.append(project_3d(x_rotated, y_rotated, z_rotated))
        return rotated

    # Define cube vertices
    outer_vertices = [
        (-outer_size, -outer_size, -outer_size),
        (outer_size, -outer_size, -outer_size),
        (outer_size, outer_size, -outer_size),
        (-outer_size, outer_size, -outer_size),
        (-outer_size, -outer_size, outer_size),
        (outer_size, -outer_size, outer_size),
        (outer_size, outer_size, outer_size),
        (-outer_size, outer_size, outer_size)
    ]

    inner_vertices = [
        (-inner_size, -inner_size, -inner_size),
        (inner_size, -inner_size, -inner_size),
        (inner_size, inner_size, -inner_size),
        (-inner_size, inner_size, -inner_size),
        (-inner_size, -inner_size, inner_size),
        (inner_size, -inner_size, inner_size),
        (inner_size, inner_size, inner_size),
        (-inner_size, inner_size, inner_size)
    ]

    rotated_outer = rotate_and_project(outer_vertices)
    rotated_inner = rotate_and_project(inner_vertices)

    # Define edges
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    connections = [(i, i) for i in range(8)]

    # Draw edges
    for start, end in edges:
        draw_icons_along_line(hdc, rotated_outer[start][0], rotated_outer[start][1],
                              rotated_outer[end][0], rotated_outer[end][1], icon)
        draw_icons_along_line(hdc, rotated_inner[start][0], rotated_inner[start][1],
                              rotated_inner[end][0], rotated_inner[end][1], icon)

    # Draw connections between cubes
    for outer_idx, inner_idx in connections:
        draw_icons_along_line(hdc, rotated_outer[outer_idx][0], rotated_outer[outer_idx][1],
                              rotated_inner[inner_idx][0], rotated_inner[inner_idx][1], icon)

# Animation loop
while True:
    # Get current icon
    current_icon = win32gui.LoadIcon(None, icons[current_icon_index])

    # Draw the hypercube directly onto the screen's DC
    draw_hypercube_with_icon_edges(hdc_screen, outer_cube_size, inner_cube_size, angle_x, angle_z, current_icon)

    # Update position and check for screen boundaries (bounce logic)
    center_x += velocity_x
    center_y += velocity_y

    # Bounce off the edges of the screen
    if center_x - outer_cube_size <= 0 or center_x + outer_cube_size >= desktop_width:
        velocity_x *= -1
        collision_count += 1  # Count collisions

    if center_y - outer_cube_size <= 0 or center_y + outer_cube_size >= desktop_height:
        velocity_y *= -1
        collision_count += 1  # Count collisions

    # Change icon every 2 collisions
    if collision_count >= 2:
        collision_count = 0
        current_icon_index = (current_icon_index + 1) % len(icons)  # Cycle to the next icon

    # Update rotation angles for tilting and spinning
    angle_x += 0.01
    angle_z += 0.02

    # Delay for smooth animation
    time.sleep(0.01)
