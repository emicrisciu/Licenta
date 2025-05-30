import football_field
import math

# Define all field boundaries as line segments
field_boundaries = {
    "left_goal_line": [(0, 0), (0, football_field.field_width)],
    "right_goal_line": [(football_field.field_length, 0), (football_field.field_length, football_field.field_width)],
    "bottom_line": [(0, 0), (football_field.field_length, 0)],
    "top_line": [(0, football_field.field_width), (football_field.field_length, football_field.field_width)]
}

# Function to check if two line segments intersect
def do_segments_intersect(p1, p2, p3, p4):
    """Check if line segment p1-p2 intersects with line segment p3-p4"""
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    
    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

# Function to calculate intersection point
def get_intersection_point(p1, p2, p3, p4):
    """Calculate the intersection point of two line segments"""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    
    # Line 1 represented as a1x + b1y = c1
    a1 = y2 - y1
    b1 = x1 - x2
    c1 = a1*x1 + b1*y1
    
    # Line 2 represented as a2x + b2y = c2
    a2 = y4 - y3
    b2 = x3 - x4
    c2 = a2*x3 + b2*y3
    
    determinant = a1*b2 - a2*b1
    
    if determinant == 0:
        return None  # Lines are parallel
    else:
        x = (b2*c1 - b1*c2)/determinant
        y = (a1*c2 - a2*c1)/determinant
        return (x, y)

# Enhanced line crossing detection
def detect_line_crossing(current_pos, previous_pos, z_coord, dt):
	message = ""
	# Check for intersection with each boundary
	for boundary_name, boundary_points in field_boundaries.items():
		p3, p4 = boundary_points
        
		if do_segments_intersect(previous_pos, current_pos, p3, p4):
			# Calculate exact crossing point
			crossing_point = get_intersection_point(previous_pos, current_pos, p3, p4)
            
			# Determine direction (in/out)
			current_zone = football_field.detect_zone(current_pos[0], current_pos[1], z_coord)
			previous_zone = football_field.detect_zone(previous_pos[0], previous_pos[1], z_coord)
			
			if previous_zone == "field" and current_zone != "field":
				direction = "out"
				if current_zone in ["above_goal_left", "above_goal_right"]:
					message = "Mingea a trecut peste poarta!"
				elif current_zone in ["goal_left", "goal_right"]:
					message = "Gol detectat!"
				else:
					message = "Mingea a iesit din teren in "
					if current_zone in ["out_up", "out_down"]:
						message += "aut de margine!"
					else:
						message += "aut de poarta / corner!"
			elif previous_zone != "field" and current_zone == "field":
				direction = "in"
				message = "Mingea a intrat in teren din zona "
				if previous_zone in ["above_goal_left", "above_goal_right", "goal_left", "goal_right"]:
					message += "portii!"
				elif previous_zone in ["out_up", "out_down"]:
					message += "autului de margine!"
				else:
					message += "autului de poarta / cornerului!"
			else:
				direction = "unclear"
            
			# Calculate crossing velocity
			dx = current_pos[0] - previous_pos[0]
			dy = current_pos[1] - previous_pos[1]
			velocity = math.sqrt(dx**2 + dy**2) / dt
            
			return {
				"boundary": boundary_name,
				"crossing_point": crossing_point,
				"direction": direction,
				"velocity": velocity/1000,
				"message": message
			}
    
	return None
    
def detect_goal(z_coord, crossing_point, crossing_direction):
    return z_coord <= 500 and crossing_direction == "out" and (goal_y_start <= crossing_point[1] <= goal_y_start + goal_width)
    
def distance_from_point_to_line(point, line):
	"""
	Calculate the minimum distance from a point to a line in 2D space.

	Parameters:
	point (tuple): A tuple (x, y) representing the point coordinates
	line (tuple): A tuple ((x1, y1), (x2, y2)) representing two points on the line

	Returns:
	float: The minimum distance from the point to the line
	"""
	x0, y0 = point
	(x1, y1), (x2, y2) = line

	# Check if the line points are the same (not a valid line)
	if (x1, y1) == (x2, y2):
		# Calculate distance to the point on the line
		return ((x0 - x1)**2 + (y0 - y1)**2)**0.5

	# Calculate the distance using the formula:
	# d = |Ax0 + By0 + C| / sqrt(A^2 + B^2)
	# where Ax + By + C = 0 is the line equation

	A = y2 - y1
	B = x1 - x2
	C = x2*y1 - x1*y2

	numerator = abs(A*x0 + B*y0 + C)
	denominator = (A**2 + B**2)**0.5

	return numerator / denominator