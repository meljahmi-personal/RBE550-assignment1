# zigzag_pattern.py
# Draw three equilateral triangles arranged in a zigzag (Victor Sierra pattern)
# and enclose them with a dashed circle. Output is saved as an EPS.
#

import turtle
import math

def dashed_circle(t, radius, dash_angle=6, gap_angle=4):
    """Draw a dashed circle using circular arc segments.

    dash_angle, gap_angle: angles in degrees along the circle.
    """
    n = int(360 / (dash_angle + gap_angle)) or 1
    for _ in range(n):
        t.pendown()
        t.circle(radius, dash_angle)  # draw a short arc (the dash)
        t.penup()
        t.circle(radius, gap_angle)   # skip a short arc (the gap)

def enclosing_circle_from_points(points, pad=10):
    """Given a list of (x, y) points, return (cx, cy, r) for a circle that
    encloses them. Center is mid-point of the AABB; radius is max distance
    from center to any point, plus 'pad' pixels for breathing room."""
    xs = (x for x, _ in points)
    ys = (y for _, y in points)
    minx = min(xs); maxx = max(x for x, _ in points)  # re-scan xs since generators are one-shot
    miny = min(ys); maxy = max(y for _, y in points)  # re-scan ys likewise
    cx = (minx + maxx) / 2.0
    cy = (miny + maxy) / 2.0
    r = max(math.hypot(x - cx, y - cy) for x, y in points) + pad
    return cx, cy, r

# --- Turtle setup ---
screen = turtle.Screen()
screen.setup(800, 600)
screen.bgcolor("white")
screen.title("Victor Sierra Pattern - Zigzag")

t = turtle.Turtle()
t.hideturtle()
t.speed(0)
t.pensize(3)
t.color("blue")

# --- Draw the three triangles (equilateral, side = size) ---
size = 120
h = size * math.sqrt(3) / 2.0

# Triangle 1 (up)
t.penup()
t.goto(-150, -80)
t.pendown()
for _ in range(3):
    t.forward(size)
    t.left(120)

# Triangle 2 (down)
t.penup()
t.goto(-30, 60)
t.pendown()
for _ in range(3):
    t.forward(size)
    t.right(120)

# Triangle 3 (up)
t.penup()
t.goto(90, -80)
t.pendown()
for _ in range(3):
    t.forward(size)
    t.left(120)

# --- Compute enclosing dashed circle from triangle vertices only ---
s = size
h = s * math.sqrt(3) / 2.0
triangles = [
    [(-150, -80), (-150 + s, -80), (-150 + s/2, -80 + h)],  # up
    [(-30,  60),  (-30 + s,  60),  (-30 + s/2,  60 - h)],  # down
    [(90,  -80),  (90 + s,  -80),  (90 + s/2,  -80 + h)]   # up
]
pts = [p for tri in triangles for p in tri]

cx, cy, r = enclosing_circle_from_points(pts, pad=10)

t.penup()
t.goto(cx, cy - r)
t.setheading(0)
t.pensize(2)
t.color("blue")
dashed_circle(t, r, dash_angle=8, gap_angle=6)


# --- Save and exit ---
canvas = screen.getcanvas()
canvas.postscript(file="victor_sierra_zigzag.eps", colormode="color")
print("Saved: victor_sierra_zigzag.eps")

screen.exitonclick()

