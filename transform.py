import numpy as np
from find_ball import RigidObject, RigidType
import matplotlib.pyplot as plt

class Map:
    def __init__(self, threshold=0.1):
        self.POLE_COLOR = "blue"
        self.OBST_COLOR = "red"
        self.BALL_COLOR = "yellow"

        self.objects = []

        self.threshold = threshold

    def distance(self, object_a: RigidObject, object_b: RigidObject):
        return np.sqrt(np.sum(np.power(object_a.position() - object_b.position(), 2)))

    def add_object(self, object_a: RigidObject, robot_pos: tuple, robot_angle: float):
        print("BEFORE ROTATION:", object_a.position())
        object_a.set_position(*self.transform(object_a.position(), robot_angle, robot_pos))
        print("AFTER ROTATION:", object_a.position())
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

    def show(self, show_all=False, show_merged=True, robot_pos=None):
        if show_merged:
            for point in self.merge_objects():
                pos = point.position()
                plt.scatter(*pos, color=self.get_object_color(point), s=50)
        if show_all:
            for point in self.objects:
                pos = point.position()
                plt.scatter(*pos, color=self.get_object_color(point), s=25, alpha=0.2)
        if robot_pos:
            plt.scatter(*pos, color="magenta", s=60)
        xlim = plt.xlim()
        ylim = plt.ylim()
        x_range = max(abs(xlim[0]), abs(xlim[1]))
        y_range = max(abs(ylim[0]), abs(ylim[1]))
        max_range = max(x_range, y_range) * 1.1
        plt.xlim(-max_range, max_range)
        plt.ylim(-max_range, max_range)
        plt.axhline(0, color='black', linewidth=1, linestyle='--')
        plt.axvline(0, color='black', linewidth=1, linestyle='--')
        plt.show()

    def average(self, object_a: RigidObject, object_b: RigidObject):
        return np.mean([object_a.position(), object_b.position()], axis=0)
    
    def transform(self, position, angle, base_pos):
        print("Position before rot.", position)
        print("Rotation angle: ", angle, "position", base_pos)
        transform_matrix = np.array([[np.cos(angle), -np.sin(angle), base_pos[0]],
                                    [np.sin(angle), np.cos(angle), base_pos[1]],
                                    [0, 0, 1]])
        position = np.array([*position, 1])
        result = np.dot(transform_matrix, position)[:2]
        print("After rotation")
        return result

    def merge_objects(self):
        objects = []
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

                dists = [self.distance(pole, x) for x in merged]
                is_merged = False
                for k, x in enumerate(dists):
                    # merge into existing object
                    if x < self.threshold:
                        merged[k].set_position(*self.average(merged[k], pole))
                        merged_counter[k] += 1
                        is_merged = True

                if is_merged:
                    continue
                else:
                    merged.append(pole)
                    merged_counter.append(1)
            objects.extend(merged)
        return objects

    def get_poles(self):
        return list(filter(lambda x: x.o_type == RigidType.POLE, self.merge_objects()))

    def get_ball(self):
        return list(filter(lambda x: x.o_type == RigidType.BALL, self.merge_objects()))

    def get_obst(self):
        return list(filter(lambda x: x.o_type == RigidType.OBST, self.merge_objects()))