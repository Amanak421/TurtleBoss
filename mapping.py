import numpy as np
import matplotlib.pyplot as plt
from rigidobject import RigidObject, RigidType, ColorType


def distance(object_a: RigidObject, object_b: RigidObject):
    return np.sqrt(np.sum(np.power(object_a.position - object_b.position, 2)))


def average(object_a: RigidObject, object_b: RigidObject):
    return np.mean([object_a.position, object_b.position], axis=0)


def transform(position, angle, base_pos):
    print("Position before rot.", position)
    print("Rotation angle: ", angle, "position", base_pos)
    transform_matrix = np.array([[np.cos(angle), -np.sin(angle), base_pos[0]],
                                [np.sin(angle), np.cos(angle), base_pos[1]],
                                [0, 0, 1]])
    position = np.array([*position, 1])
    result = np.dot(transform_matrix, position)[:2]
    print("After rotation")
    return result


class Map:
    def __init__(self, threshold=0.2):
        self.POLE_COLOR = "blue"
        self.OBST_COLOR = "red"
        self.BALL_COLOR = "yellow"

        self.objects = []

        self.threshold = threshold

    @property
    def poles(self):
        return self.merge_objects()[RigidType.POLE]

    @property
    def ball(self):
        return self.merge_objects()[RigidType.BALL]

    @property
    def obstacles(self):
        return self.merge_objects()[RigidType.OBST]

    def add_object(self, object_a: RigidObject, robot_pos: tuple, robot_angle: float):
        print("BEFORE ROTATION:", object_a.position)
        object_a.set_position(*transform(object_a.position, robot_angle, robot_pos))
        print("AFTER ROTATION:", object_a.position)
        self.objects.append(object_a)

    def get_object_color(self, object_a):
        color = "black"
        if object_a.o_type == RigidType.BALL:
            color = self.BALL_COLOR
        elif object_a.o_type == RigidType.POLE:
            color = self.POLE_COLOR
        elif object_a.o_type == RigidType.OBST:
            color = self.OBST_COLOR
        return color

    def show(self, show_all=False, show_merged=True, robot_pos=None, kick_pos=None, midpoint=None):
        fig, ax = plt.subplots(figsize=(6, 6), dpi=100)  # Set 6x6 inches
        ax.set_aspect(1)  # X, Y axis ratio 1:1
        if show_merged:
            obj = self.merge_objects()
            print(obj)
            for o_type in  obj:
                print("FOR O TYPE", o_type)
                count = 0
                for point in obj[o_type]:
                    pos = point.position
                    if (o_type == RigidType.POLE and count > 1) or (o_type == RigidType.BALL and count > 0):
                        ax.scatter(*pos, color=self.get_object_color(point), s=50, edgecolors='red', linewidths=2)
                    else:
                        ax.scatter(*pos, color=self.get_object_color(point), s=50)
                    count += 1
        if show_all:
            for point in self.objects:
                pos = point.position
                ax.scatter(*pos, color=self.get_object_color(point), s=25, alpha=0.2)
        if robot_pos is not None:
            x_end = robot_pos[0] + 0.2 * np.cos(robot_pos[2])
            y_end = robot_pos[1] + 0.2 * np.sin(robot_pos[2])
            plt.plot([robot_pos[0], x_end], [robot_pos[1], y_end])
            ax.scatter(robot_pos[0], robot_pos[1], color="black", s=60)
        if kick_pos is not None:
            x_end = kick_pos[0] + 0.2 * np.cos(kick_pos[2])
            y_end = kick_pos[1] + 0.2 * np.sin(kick_pos[2])
            plt.plot([kick_pos[0], x_end], [kick_pos[1], y_end])
            ax.scatter(kick_pos[0], kick_pos[1], color="black", s=60)
            ax.scatter(kick_pos[0], kick_pos[1], color="cyan", s=60)
        if midpoint is not None:
            ax.scatter(midpoint[0], midpoint[1], color="black", s=60)

        x_lim = plt.xlim()
        y_lim = plt.ylim()
        x_range = max(abs(x_lim[0]), abs(x_lim[1]))
        y_range = max(abs(y_lim[0]), abs(y_lim[1]))
        max_range = max(x_range, y_range) * 1.1
        plt.xlim(-max_range, max_range)
        plt.ylim(-max_range, max_range)
        plt.axhline(0, color='black', linewidth=1, linestyle='--')
        plt.axvline(0, color='black', linewidth=1, linestyle='--')
        plt.show()

    def merge_objects(self):
        objects = {}
        for o_type in RigidType:
            unmerged = list(filter(lambda x: x.o_type == o_type, self.objects))
            merged = []
            merged_counter = []

            for pole in unmerged:
                # add pole when empty
                if not merged:
                    merged.append(pole)
                    merged_counter.append(1)
                    continue

                dists = [distance(pole, x) for x in merged]
                is_merged = False
                for k, x in enumerate(dists):
                    # merge into existing object
                    if x < self.threshold:
                        merged[k].set_position(*average(merged[k], pole))
                        merged_counter[k] += 1
                        is_merged = True

                if is_merged:
                    continue
                else:
                    merged.append(pole)
                    merged_counter.append(1)    

            sorted_objects = [obj for _, obj in sorted(zip(merged_counter, merged), key=lambda x: x[0], reverse=True)]
            objects[o_type] = sorted_objects

        return objects

if __name__ == "__main__":
    mapA = Map()
    b = RigidObject(0.5, -0.5, 0, 0, RigidType.BALL, ColorType.YELLOW)
    b.set_position(0.5, -0.5)
    mapA.add_object(b, (0, 0), 0)
    mapA.show()
