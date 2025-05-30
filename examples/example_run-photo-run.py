"""
Testing script from early stages of the project.

Expected behavior: go around half a circle and make 3 RGBd images
"""


import sys

from scipy.io import savemat
from robolab_turtlebot import Turtlebot, sleep, Rate

# Name bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

bumped: int = 0
global_x_pos = 0
global_y_pos = 0
global_angle = 0


def bumper_cb(msg: str) -> None:
    """Bumber callback."""
    bumper = bumper_names[msg.bumper]
    state = state_names[msg.state]
    print('{} bumper {}'.format(bumper, state))
    # Update global variable
    global bumped
    bumped = msg.state


def check_bump() -> None:
    """
    Stop whole program.

    INVALID! DOES NOT WORK!
    """
    if bumped:
        print("Bumped!")
        sys.exit(66)


def reset_telemetry() -> None:
    """Reset global data."""
    global global_x_pos, global_y_pos, global_angle
    global_x_pos = turtle.get_odometry()[0]
    global_y_pos = turtle.get_odometry()[1]
    global_angle = turtle.get_odometry()[2]
    turtle.reset_odometry()
    sleep(0.1)


def save_telemetry(fn: str = "default.mat") -> None:
    """Save .mat file with RGBd data."""
    # Get K, images, and point cloud
    data = dict()
    data['K_rgb'] = turtle.get_rgb_K()
    data['K_depth'] = turtle.get_depth_K()
    data['image_rgb'] = turtle.get_rgb_image()
    data['image_depth'] = turtle.get_depth_image()
    data['point_cloud'] = turtle.get_point_cloud()
    data['odometry'] = turtle.get_odometry()
    # Save data to .mat file
    filename = fn
    savemat(filename, data)
    print("Data saved in {filename}")


def go(length: int = 1) -> None:
    """Go straight."""
    rate = Rate(10)
    reset_telemetry()
    distance = turtle.get_odometry()[0]
    length *= 0.96

    while distance < length:
        turtle.cmd_velocity(linear=0.3)
        check_bump()
        rate.sleep()
        distance = turtle.get_odometry()[0]
    turtle.cmd_velocity()


def turn(target_angle: float) -> None:
    """Turn by angle in degrees."""
    target_angle = target_angle * 3.141592653 / 180
    rate = Rate(10)
    reset_telemetry()
    angle = turtle.get_odometry()[2]

    def cond(a: float) -> bool:
        return (a <= target_angle) if target_angle > 0 else (a > target_angle)

    while cond(angle):
        turtle.cmd_velocity(angular=0.5)
        check_bump()
        print(turtle.get_odometry())
        rate.sleep()
        angle = turtle.get_odometry()[2]
    turtle.cmd_velocity()


def run() -> None:
    """Make 3 images from 3 positions."""
    turtle.reset_odometry()
    for i in range(3):
        save_telemetry(f"tel{i}.mat")
        print(f"{i} [o]'\tR60 {turtle.get_odometry()}")
        turn(-60)
        print(f"{i} R60\t->> {turtle.get_odometry()}")
        go()
        print(f"{i} ->>\tL120 {turtle.get_odometry()}")
        turn(120)
        print(f"{i} L120\t[o]' {turtle.get_odometry()}")


if __name__ == "__main__":
    # Initialize Turlebot
    turtle = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle.play_sound(1)
    sleep(0.3)
    turtle.register_bumper_event_cb(bumper_cb)
    run()
