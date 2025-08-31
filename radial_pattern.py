# radial_pattern.py
import turtle

# Setup
screen = turtle.Screen()
screen.setup(800, 600)
screen.bgcolor("white")
screen.title("Radial Triangle Pattern")

t = turtle.Turtle()
t.hideturtle()
t.speed(0)
t.pensize(3)
t.color("red")

# Draw radial pattern
size = 100
for angle in [0, 120, 240]:
    t.penup()
    t.goto(0, 0)
    t.setheading(angle)
    t.pendown()
    for _ in range(3):
        t.forward(size)
        t.left(120)

# Add title
t.penup()
t.goto(0, -200)
t.color("black")
t.write("Radial Triangle Pattern", align="center", font=("Arial", 14, "bold"))

# Save EPS
canvas = screen.getcanvas()
canvas.postscript(file="victor_sierra_radial.eps", colormode="color")
print("Saved: victor_sierra_radial.eps")

screen.exitonclick()
