# zigzag_pattern.py
import turtle
import math

# Setup
screen = turtle.Screen()
screen.setup(800, 600)
screen.bgcolor("white")
screen.title("Victor Sierra Pattern - Zigzag")

t = turtle.Turtle()
t.hideturtle()
t.speed(0)
t.pensize(3)
t.color("blue")

# Draw zigzag pattern
size = 120
h = size * math.sqrt(3) / 2.0

# Triangle 1 (pointing up)
t.penup()
t.goto(-150, -80)
t.pendown()
for _ in range(3):
    t.forward(size)
    t.left(120)

# Triangle 2 (pointing down)
t.penup()
t.goto(-30, 60)
t.pendown()
for _ in range(3):
    t.forward(size)
    t.right(120)

# Triangle 3 (pointing up)
t.penup()
t.goto(90, -80)
t.pendown()
for _ in range(3):
    t.forward(size)
    t.left(120)

# Add title
t.penup()
t.goto(0, -150)
t.color("black")
t.write("Victor Sierra Zigzag Pattern", align="center", font=("Arial", 14, "bold"))

# Save EPS
canvas = screen.getcanvas()
canvas.postscript(file="victor_sierra_zigzag.eps", colormode="color")
print("Saved: victor_sierra_zigzag.eps")

screen.exitonclick()
