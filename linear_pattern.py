# linear_pattern.py
import turtle

# Setup
screen = turtle.Screen()
screen.setup(800, 600)
screen.bgcolor("white")
screen.title("Linear Triangle Pattern")

t = turtle.Turtle()
t.hideturtle()
t.speed(0)
t.pensize(3)
t.color("green")

# Draw linear pattern
size = 100
positions = [(-200, -50), (0, -50), (200, -50)]

for x, y in positions:
    t.penup()
    t.goto(x, y)
    t.pendown()
    for _ in range(3):
        t.forward(size)
        t.left(120)

# Add title
t.penup()
t.goto(0, -150)
t.color("black")
t.write("Linear Triangle Pattern", align="center", font=("Arial", 14, "bold"))

# Save EPS
canvas = screen.getcanvas()
canvas.postscript(file="victor_sierra_linear.eps", colormode="color")
print("Saved: victor_sierra_linear.eps")

screen.exitonclick()
