# linear_pattern.py
# Draw three equilateral triangles arranged side-by-side in a line (Victor Sierra pattern, linear layout).
# A dashed circle is drawn around all three triangles to act as the search boundary.
# The output is saved as an EPS file.

import turtle
import math

def dashed_circle(t, radius, dash_angle=6, gap_angle=4):
    """Draw a dashed circle by alternating arc segments and gaps.

    dash_angle, gap_angle: angles (degrees) of the arc segments.
    """
    n = int(360 / (dash_angle + gap_angle)) or 1
    for _ in range(n):
        t.pendown()
        t.circle(radius, dash_angle)   # draw a short arc (the dash)
        t.penup()
        t.circle(radius, gap_angle)    # skip ahead (the gap)

# --- Screen setup ---
screen = turtle.Screen()
screen.setup(800, 600)
screen.bgcolor("white")
screen.title("Linear Triangle Pattern")

t = turtle.Turtle()
t.hideturtle()
t.speed(0)
t.pensize(3)
t.color("green")

# --- Draw three triangles in a row ---
size = 100
positions = [(-200, -50), (0, -50), (200, -50)]  # starting points for the bases

for x, y in positions:
    t.penup()
    t.goto(x, y)
    t.pendown()
    for _ in range(3):
        t.forward(size)
        t.left(120)

# --- Collect vertices for all triangles (for the enclosing circle) ---
h = size * math.sqrt(3) / 2.0
triangles = [[(x, y), (x + size, y), (x + size/2, y + h)] for x, y in positions]
pts = [p for tri in triangles for p in tri]

# bounding box
minx = min(x for x, _ in pts)
maxx = max(x for x, _ in pts)
miny = min(y for _, y in pts)
maxy = max(y for _, y in pts)

# center of bounding box
cx = (minx + maxx) / 2.0
cy = (miny + maxy) / 2.0

# radius is the farthest vertex distance + padding
r = max(math.hypot(x - cx, y - cy) for x, y in pts) + 10

# --- Draw dashed enclosing circle ---
t.penup()
t.goto(cx, cy - r)
t.setheading(0)
t.pensize(2)
t.color("green")
dashed_circle(t, r, dash_angle=8, gap_angle=6)

# --- Save as EPS and exit ---
canvas = screen.getcanvas()
canvas.postscript(file="victor_sierra_linear.eps", colormode="color")
print("Saved: victor_sierra_linear.eps")

screen.exitonclick()

