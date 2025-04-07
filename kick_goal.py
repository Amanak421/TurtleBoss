"""All implemented features for completion challenge no. 2."""


import sys

from robolab_turtlebot import Rate, Turtlebot, sleep
from mapping import Map
from robot import Robot


if len(sys.argv) > 1:
    DEBUG = True
else:
    DEBUG = False


if __name__ == "__main__":
    turtle_ = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle_.play_sound(1)
    sleep(0.3)
    rate = Rate(50)
    robot = Robot(turtle_, rate)
    robot.reset()
    robot_map = Map()

    # base distance for calculating kick position
    KICK_DISTANCE = 1

    print("Wait for button press on robot...")
    while not robot.button:
        pass

    # find ball and poles and add them to the map
    robot.scan_environment(robot_map, debug_info=DEBUG)

    ball = robot_map.ball
    kick_pos = robot_map.determine_kick_pos(dist=KICK_DISTANCE)
    path = robot_map.routing(robot.position, kick_pos)

    if DEBUG:
        robot_map.show(show_all=False, show_merged=True, path=path,
                       danger_zones=robot_map.danger_zones,
                       robot_pos=robot.position,
                       kick_pos=kick_pos, debug_info=True)

    # go in front of ball
    for p in path[1:]:
        robot.go_to(p)

    while True:
        # reset all systems and scan the environment for second time
        robot_map.reset()
        robot.reset()
        first_try = robot.scan_environment(robot_map, debug_info=DEBUG)
        # calculate position for kick and to it
        if first_try:
            KICK_DISTANCE = 0.6
        kick_pos = robot_map.determine_kick_pos(dist=0.6)
        robot.go_to(kick_pos)
        if KICK_DISTANCE == 0.6:
            break

    print("INIT KICK MODE")

    # center ball to the center of the screen
    robot.center_ball()

    # kick the ball to the goal
    robot.kick(0.5, speed=1.5)
