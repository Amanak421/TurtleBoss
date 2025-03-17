# TODO depreciate soon (used only in movement and depreciated kick_pos)
import matplotlib.pyplot as plt
import numpy as np

class Visual:
    def __init__(self):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        # Formatting
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)

        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_title("Robot Position and Orientation")
        self.ax.legend()
        self.ax.set_aspect('equal')  # Keep aspect ratio square
        plt.grid()

        self.goal = None
        self.ball = None
        self.obstacles = []

        #robot
        self.robot_dot, = self.ax.plot([0], [0], 'bo', markersize=10)
        self.robot_line, = self.ax.plot([0, 1], [0, 0], 'b-', linewidth=2)
    
    def updateRobot(self, x, y, angle, line_length = 1):
        x_end = x + line_length * np.cos(angle)
        y_end = y + line_length * np.sin(angle)
        self.robot_dot.set_data([x], [y])
        self.robot_line.set_data([x, x_end], [y, y_end])
        plt.draw()

    def setGoal(self, x, y):
        self.goal = self.ax.plot(x, y, 'bo', markersize=10)
        plt.draw()

    def setBall(self, x, y):
        self.ball = self.ax.plot(x, y, 'yo', markersize=10)
        plt.draw()

    def addObstacle(self, x, y):
        self.obstacles.append(self.ax.plot([x], [y], 'ro', markersize=10))
        plt.draw()

    def hideGoal(self):
        self.goal.set_visibility(False)
        plt.draw()

    def hideBall(self):
        self.ball.set_visibility(False)
        plt.draw()

    def removeAllObsatcles(self):
        for obs in self.obstacles:
            obs.set_visibility(False)
        plt.draw()


if __name__ == "__main__":
    vis = Visual()
    input()
    vis.updateRobot(1, 1, 0)
    input()
    vis.updateRobot(-1, -1, np.pi/2)
    input()
    vis.setGoal([3, 5], [1, 1])
    input()