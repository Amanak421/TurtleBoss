from robolab_turtlebot import Turtlebot, sleep, Rate
from mapping import Map
from robot import Robot
import sys


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

    print("Wait for button press on robot...")
    while not robot.button:
        pass

    # find ball and poles and add them to the map
    robot.scan_environment(robot_map)

    ball = robot_map.ball
    kick_pos = robot_map.determine_kick_pos(dist=1)
    path = robot_map.routing(robot.position, kick_pos)
    
    if DEBUG:
        robot_map.show(show_all=False, show_merged=True, path=path, dead_zones=robot_map.dead_zones, robot_pos=robot.position, kick_pos=kick_pos, debug_info=True)

    # go in front of ball
    for p in path[1:]:
        robot.go_to(p, linear_velocity=0.4, angular_velocity=0.45)

    # reset all systems and scan the environment for second time
    robot_map.reset()
    robot.reset()
    robot.scan_environment(robot_map)
    # calculate position for kick and to it
    kick_pos = robot_map.determine_kick_pos(dist=0.6)
    robot.go_to(kick_pos, linear_velocity=0.4, angular_velocity=0.45)

    print("INIT KICK MODE")

    # center ball to the center of the screen
    robot.center_ball()

    # kick the ball to the goal
    robot.kick(0.5, speed=1)
    robot.stop()
    sleep(0.2)

    # play sound
    turtle_.play_sound(5)
    print("PROGRAM ENDED")