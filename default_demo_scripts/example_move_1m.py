from robolab_turtlebot import Turtlebot, Rate, get_time

turtle = Turtlebot()
rate = Rate(10)

t = get_time()

while get_time() - t < 10:
    turtle.cmd_velocity(linear=0.1)
    rate.sleep()
