import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc
import math

# Initialize plot elements
fig, ax = plt.subplots(figsize=(16, 9))
goal_zone_left = None
goal_zone_right = None
out_zone_up = None
out_zone_down = None
corner_zone_up_left = None
corner_zone_down_left = None
corner_zone_up_right = None
corner_zone_down_right = None
corner_zone_left = None
corner_zone_right = None
above_goal_zone_left = None
above_goal_zone_right = None
sc = ax.scatter([], [])

# Field dimensions
field_length = 1800  # Field length in mm
field_width = 1200   # Field width in mm
goal_depth = 150     # Goal depth in mm
goal_y_start = 350   # Goal start position on Y axis
goal_width = 500
goal_offset = (field_width - goal_width) / 2
penalty_area_size = 297
penalty_area_offset = 223
goal_area_size = 99
penalty_spot = 197
radius = 163
border = 200
# Approximate diagonal length of your tracking area in meters
room_diagonal = math.sqrt(field_length**2 + field_width**2)

# Dictionary mapping zone names to their patch objects
zone_patches = {}

def draw_field():
    # Configure 2D plot
    global ax, sc, goal_zone_left, goal_zone_right, out_zone_up, out_zone_down
    global corner_zone_up_left, corner_zone_down_left, corner_zone_up_right, corner_zone_down_right
    global corner_zone_left, corner_zone_right, above_goal_zone_left, above_goal_zone_right
    global field_length, field_width, goal_depth, goal_width, goal_y_start, goal_offset, penalty_area_size, goal_area_size
    

    # Create scatter plot for ball position
    sc = ax.scatter([], [], color='blue', s=50)

    # Set plot limits
    ax.set_xlim(-border, field_length + border)
    ax.set_ylim(-border, field_width + border)
    ax.set_title('Soccer Field with Real-time Ball Position')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')

    # Draw field boundaries
    ax.plot([0, 0], [0, field_width], color='black')  # Left goal line
    ax.plot([field_length, field_length], [0, field_width], color='black')  # Right goal line
    ax.plot([0, field_length], [0, 0], color='black')  # Bottom line
    ax.plot([0, field_length], [field_width, field_width], color='black')  # Top line
    ax.plot([field_length / 2, field_length / 2], [0, field_width], color='black')  # Middle line

    # Draw goal outlines
    # Left goal
    ax.plot([-goal_depth, 0], [goal_offset, goal_offset], color='grey', linewidth=1.2)
    ax.plot([-goal_depth, -goal_depth], [goal_offset, field_width - goal_offset], color='grey', linewidth=1.2)
    ax.plot([-goal_depth, 0], [field_width - goal_offset, field_width - goal_offset], color='grey', linewidth=1.2)
    # Right goal
    ax.plot([field_length, field_length + goal_depth], [goal_offset, goal_offset], color='grey', linewidth=1.2)
    ax.plot([field_length + goal_depth, field_length + goal_depth], [goal_offset, field_width - goal_offset], color='grey', linewidth=1.2)
    ax.plot([field_length, field_length + goal_depth], [field_width - goal_offset, field_width - goal_offset], color='grey', linewidth=1.2)

    # Center circle
    center_circle = Circle((field_length / 2, field_width / 2), radius, edgecolor='black', facecolor='none', linestyle='-')
    ax.add_patch(center_circle)

    # Center point
    ax.scatter([field_length / 2], [field_width / 2], color='black')

    # Penalty areas
    penalty_area_left = Rectangle((0, penalty_area_offset), penalty_area_size, field_width - 2 * penalty_area_offset, edgecolor='black', facecolor='none')
    penalty_area_right = Rectangle((field_length - penalty_area_size, penalty_area_offset), penalty_area_size, field_width - 2 * penalty_area_offset, edgecolor='black', facecolor='none')
    ax.add_patch(penalty_area_left)
    ax.add_patch(penalty_area_right)

    # Goal areas
    goal_area_left = Rectangle((0, goal_y_start), goal_area_size, goal_width, edgecolor='black', facecolor='none')
    goal_area_right = Rectangle((field_length - goal_area_size, goal_y_start), goal_area_size, goal_width, edgecolor='black', facecolor='none')
    ax.add_patch(goal_area_left)
    ax.add_patch(goal_area_right)

    # Penalty spots
    ax.scatter([penalty_spot], [field_width / 2], color='black')
    ax.scatter([field_length - penalty_spot], [field_width / 2], color='black')

    # Penalty arcs
    penalty_arc_left = Arc((penalty_spot, field_width / 2), 2 * radius, 320, angle=0, theta1=308, theta2=52, edgecolor='black')
    penalty_arc_right = Arc((field_length - penalty_spot, field_width / 2), 2 * radius, 320, angle=0, theta1=128, theta2=232, edgecolor='black')
    ax.add_patch(penalty_arc_left)
    ax.add_patch(penalty_arc_right)

    # Goal zones
    goal_zone_left = Rectangle((-goal_depth, goal_y_start), goal_depth, goal_width, color='green', alpha=0.2)
    goal_zone_right = Rectangle((field_length, goal_y_start), goal_depth, goal_width, color='green', alpha=0.2)
    ax.add_patch(goal_zone_left)
    zone_patches["goal_left"] = goal_zone_left
    ax.add_patch(goal_zone_right)
    zone_patches["goal_right"] = goal_zone_right

    # Out-of-bounds zones
    out_zone_up = Rectangle((-border, field_width), field_length + 2 * border, border, color='red', alpha=0.2)
    out_zone_down = Rectangle((-border, -border), field_length + 2 * border, border, color='red', alpha=0.2)
    ax.add_patch(out_zone_up)
    zone_patches["out_up"] = out_zone_up
    ax.add_patch(out_zone_down)
    zone_patches["out_down"] = out_zone_down

    # Corner zones
    corner_zone_up_left = Rectangle((-goal_depth, goal_offset + goal_width), goal_depth, goal_offset, color='orange', alpha=0.2)
    corner_zone_down_left = Rectangle((-goal_depth, 0), goal_depth, goal_offset, color='orange', alpha=0.2)
    corner_zone_left = Rectangle((-border, 0), border - goal_depth, field_width, color='orange', alpha=0.2)
    corner_zone_up_right = Rectangle((field_length, goal_offset + goal_width), goal_depth, goal_offset, color='orange', alpha=0.2)
    corner_zone_down_right = Rectangle((field_length, 0), goal_depth, goal_offset, color='orange', alpha=0.2)
    corner_zone_right = Rectangle((field_length + goal_depth, 0), border - goal_depth, field_width, color='orange', alpha=0.2)
    ax.add_patch(corner_zone_up_left)
    zone_patches["corner_up_left"] = corner_zone_up_left
    ax.add_patch(corner_zone_down_left)
    zone_patches["corner_down_left"] = corner_zone_down_left
    ax.add_patch(corner_zone_left)
    zone_patches["corner_left"] = corner_zone_left
    ax.add_patch(corner_zone_up_right)
    zone_patches["corner_up_right"] = corner_zone_up_right
    ax.add_patch(corner_zone_down_right)
    zone_patches["corner_down_right"] = corner_zone_down_right
    ax.add_patch(corner_zone_right)
    zone_patches["corner_right"] = corner_zone_right

    # Above-goal zones
    above_goal_zone_left = Rectangle((-goal_depth, goal_y_start), goal_depth, goal_width, color='orange', alpha=0.2)
    above_goal_zone_right = Rectangle((field_length, goal_y_start), goal_depth, goal_width, color='orange', alpha=0.2)
    ax.add_patch(above_goal_zone_left)
    zone_patches["above_goal_left"] = above_goal_zone_left
    ax.add_patch(above_goal_zone_right)
    zone_patches["above_goal_right"] = above_goal_zone_right

# Fixed zone detection functions to match field dimensions
# Function for zone detection that returns the zone type
def detect_zone(x, y, z):
    if (-goal_depth <= x <= 0) and (goal_y_start <= y <= goal_y_start + goal_width) and (z >= 250):
        return 'above_goal_left'
    elif (field_length <= x <= field_length + goal_depth) and (goal_y_start <= y <= goal_y_start + goal_width) and (z >= 250):
        return 'above_goal_right'
    if (-goal_depth <= x <= 0) and (goal_y_start <= y <= goal_y_start + goal_width):
        return 'goal_left'
    elif (field_length <= x <= field_length + goal_depth) and (goal_y_start <= y <= goal_y_start + goal_width):
        return 'goal_right'
    elif (-border <= x <= field_length + border) and (y > field_width):
        return 'out_up'
    elif (-border <= x <= field_length + border) and (y < 0):
        return 'out_down'
    elif (-goal_depth <= x <= 0) and (goal_y_start + goal_width <= y <= field_width):
        return 'corner_up_left'
    elif (-goal_depth <= x <= 0) and (0 <= y <= goal_y_start):
        return 'corner_down_left'
    elif (field_length <= x <= field_length + goal_depth) and (goal_y_start + goal_width <= y <= field_width):
        return 'corner_up_right'
    elif (field_length <= x <= field_length + goal_depth) and (0 <= y <= goal_y_start):
        return 'corner_down_right'
    elif (-border <= x <= -goal_depth) and (0 <= y <= field_width):
        return 'corner_left'
    elif (field_length + goal_depth <= x <= field_length + border) and (0 <= y <= field_width):
        return 'corner_right'
    else:
        return "field"