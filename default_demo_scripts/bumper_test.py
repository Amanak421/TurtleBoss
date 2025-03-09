from __future__ import print_function

from robolab_turtlebot import Turtlebot, Rate

# Names bumpers and events
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']


def bumper_cb(msg):
    """Bumber callback."""
    # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
    bumper = bumper_names[msg.bumper]

    # msg.state stores the event 0:RELEASED, 1:PRESSED
    state = state_names[msg.state]

    # Print the event
    print('{} bumper {}'.format(bumper, state))


def main():
    # Initialize turtlebot class
    turtle = Turtlebot()

    # Register bumper callback
    turtle.register_bumper_event_cb(bumper_cb)

    # Do something, the program would end otherwise
    rate = Rate(1)
    while not turtle.is_shutting_down():
        rate.sleep()


if __name__ == '__main__':
    main()
