# radial_pattern.py
# Draw three equilateral triangles rotated around the origin (Victor Sierra pattern, radial layout).
# A dashed circle is added around the entire figure to act as the search boundary.
# Output is saved as an EPS image.

import turtle
import math

def dashed_circle(t, radius, dash_angle=6, gap_angle=4):
    """Draw a dashed circle by alternating short arc segments and gaps.

    dash_angle, gap_angle are angles (in degrees) for each dash and gap.
    """
    n = int(360 / (dash_angle + gap_angle)) or 1
    for _ in range(n):
        t.pendown()
        t.circle(radius, dash_angle)  # draw short arc
        t.penup()
        t.circle(radius, gap_angle)   # skip gap

# --- Screen setup ---
screen = turtle.Screen()
screen.setup(800, 600)
screen.bgcolor("white")
screen.title("Radial Triangle Pattern")

t = turtle.Turtle()
t.hideturtle()
t.speed(0)

# --- Draw the three triangles in a radial arrangement ---
size = 100
for angle in [0, 120, 240]:
    t.penup()
    t.goto(0, 0)
    t.setheading(angle)
    t.pendown()
    for _ in range(3):
        t.forward(size)
        t.left(120)

# --- Compute vertices so we know how large the enclosing circle should be ---
h = size * math.sqrt(3) / 2.0
base_vertices = [(0, 0), (size, 0), (size / 2, h)]

def rot(p, ang_deg):
    """Rotate point p = (x, y) by ang_deg degrees around the origin."""
    a = math.radians(ang_deg)
    x, y = p
    return (x * math.cos(a) - y * math.sin(a),
            x * math.sin(a) + y * math.cos(a))

pts = []
for ang in [0, 120, 240]:
    pts.extend([rot(v, ang) for v in base_vertices])

# bounding box and circle center
minx = min(x for x, _ in pts)
maxx = max(x for x, _ in pts)
miny = min(y for _, y in pts)
maxy = max(y for _, y in pts)

cx = (minx + maxx) / 2.0
cy = (miny + maxy) / 2.0
r = max(math.hypot(x - cx, y - cy) for x, y in pts) + 10  # radius with padding

# --- Draw dashed enclosing circle ---
t.penup()
t.goto(cx, cy - r)
t.setheading(0)
t.pensize(2)
t.color("red")
dashed_circle(t, r, dash_angle=8, gap_angle=6)

# --- Save as EPS and exit ---
canvas = screen.getcanvas()
canvas.postscript(file="victor_sierra_radial.eps", colormode="color")
print("Saved: victor_sierra_radial.eps")

screen.exitonclick()

