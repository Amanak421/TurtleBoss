"""Module to keep, process and plan navigational data during a move."""


import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from geometry import Circle, Line, Point, Segment, intersection
from rigidobject import RigidObject, RigidType
from constants import MAX_OBJECTS, MIN_MATCHES, DISCRETE_INCREMENT
from utils import ProcessError


def average(object_a: RigidObject, object_b: RigidObject) -> Point:
    """
    Get an averagely estimated RigidObject from among two RigidObjects.

    :param object_a: first reference RigidObject
    :param object_b: second reference RigidObject
    :return: RigidObject estimate
    """
    return Point(*np.mean([object_a.xy, object_b.xy], axis=0))


def transform(position: Point,
              base_pos: Point,
              debug_info: bool = False) -> Point:
    """
    Transform a vector to another system with different base.

    :param position: vector to transform
    :param base_pos: default system
    :param debug_info: boolean for debug
    :return: Point with newly transformed (rotated and moved) coordinates
    """
    if debug_info:
        print("Position before rot.", position)
        print("Robot position: ", base_pos)
    transform_matrix = np.array([[base_pos.cos, -base_pos.sin, base_pos.x],
                                [base_pos.sin, base_pos.cos, base_pos.y],
                                [0, 0, 1]])
    result = np.dot(transform_matrix, position.homog_xy)[:2]
    if debug_info:
        print("After rotation")
    return Point(*result)


def has_all(all_objects: list) -> bool:
    """
    Decide whether all known object all_objects contain 2 poles and 1 ball.

    :param all_objects: list with all known objects
    :return: boolean
    """
    poles = 0
    ball = 0

    for obj in all_objects:
        if obj.o_type == RigidType.POLE and 40 <= obj.im_p.x <= 600:
            poles += 1
        elif obj.o_type == RigidType.BALL and 40 <= obj.im_p.x <= 600:
            ball += 1

    if (poles == MAX_OBJECTS[RigidType.POLE] and
            ball == MAX_OBJECTS[RigidType.BALL]):
        return True
    else:
        return False


class Map:
    """Object for keeping known objects and processing them."""

    def __init__(self, threshold: float = 0.2) -> None:
        """Set up a Map instance."""
        self.objects = []
        self.threshold = threshold

    @property
    def poles(self, debug_info: bool = False) -> list:
        """
        Gets merged positions of poles in one list sorted by merge counter.

        :param debug_info: boolean for debug
        :return: merged all known objects of type POLE
        """
        return self.merge_objects(debug_info=debug_info)[0][RigidType.POLE]

    @property
    def ball(self, debug_info: bool = False) -> list:
        """
        Gets merged positions of balls in one list sorted by merge counter.

        :param debug_info: boolean for debug
        :return: merged all known objects of type BALL
        """
        return self.merge_objects(debug_info=debug_info)[0][RigidType.BALL]

    @property
    def obstacles(self, debug_info: bool = False) -> list:
        """
        Gets merged positions of obstacles in one list sorted by merge counter.

        :param debug_info: boolean for debug
        :return: merged all known objects of type OBST
        """
        return self.merge_objects(debug_info=debug_info)[0][RigidType.OBST]

    @property
    def danger_zones(self) -> list:
        """
        Zones that the center of robot should not cross to prevent collisions.

        :return: list of danger zones
        """
        obj_dict, _ = self.merge_objects()
        danger_zones = []
        for pole in obj_dict[RigidType.POLE]:
            danger_zones.append(Circle(pole.position, 0.3))
        for obst in obj_dict[RigidType.OBST]:
            danger_zones.append(Circle(obst.position, 0.3))
        for ball in obj_dict[RigidType.BALL]:
            danger_zones.append(Circle(ball.position, 0.3))
        return danger_zones

    @property
    def has_all(self) -> bool:
        """
        Decide whether all known object all_objects contain 2 poles and 1 ball.

        :return: boolean
        """
        obj_dict, counter = self.merge_objects()
        correct = dict.fromkeys(obj_dict, 0)
        for key in obj_dict:
            for i, _ in enumerate(obj_dict[key]):
                if counter[key][i] >= MIN_MATCHES:
                    correct[key] += 1
        if (correct[RigidType.POLE] >= MAX_OBJECTS[RigidType.POLE] and
                correct[RigidType.BALL] >= MAX_OBJECTS[RigidType.BALL]):
            return True
        else:
            return False

    def reset(self) -> None:
        """Set all known object to blank list."""
        self.objects = []

    def add_object(self, object_a: RigidObject,
                   robot_pos: Point, debug_info: bool = False) -> None:
        """
        Introduce a new object to all known objects.

        :param object_a: the new object
        :param robot_pos: robot position
        :param debug_info: boolean for debug
        """
        if debug_info:
            print("BEFORE ROTATION:", object_a.position)
        object_a.set_position(transform(object_a.position,
                                        robot_pos, debug_info))
        if debug_info:
            print("AFTER ROTATION:", object_a.position)
        self.objects.append(object_a)

    @staticmethod
    def is_max_reached(o_type: RigidType, count: dict) -> bool:
        """
        Decide whether count is equal or more than requested objects.

        :param o_type: reference object type
        :param count: count of known type of reference objects
        :return: boolean
        """
        is_max_poles = (o_type == RigidType.POLE and
                        count[o_type] >= MAX_OBJECTS[o_type])
        is_max_ball = (o_type == RigidType.BALL and
                       count[o_type] >= MAX_OBJECTS[o_type])
        return is_max_poles or is_max_ball

    def show(self, show_all: bool = False,
             show_merged: bool = True,
             robot_pos: Point = None,
             kick_pos: Point = None,
             path: list = None,
             danger_zones: list = None,
             debug_info: bool = False) -> None:
        """
        Visual representation of all known objects.

        :param show_all: show detected objects before merging
        :param show_merged: show detected objects after merging
        :param robot_pos: robot position
        :param kick_pos: kick position
        :param path: list of points of the planned route
        :param danger_zones: list of danger zones
        :param debug_info: boolean for debug
        """
        _, ax = plt.subplots(figsize=(6, 6), dpi=100)  # Set 6x6 inches
        ax.set_aspect(1)  # X, Y axis ratio 1:1
        if show_merged:
            obj, _ = self.merge_objects(debug_info)
            type_counter = dict.fromkeys(obj, 0)
            for object_type, points in obj.items():
                for point in points:
                    position = point.xy
                    if self.is_max_reached(object_type, type_counter):
                        ax.scatter(*position, color=point.color, s=50,
                                   edgecolors='red', linewidths=2)
                    else:
                        ax.scatter(*position, color=point.color, s=50)
                        if object_type == RigidType.BALL:
                            ax.scatter(*position, facecolors='none',
                                       edgecolors='orange', s=50, alpha=0.5)
                    type_counter[object_type] += 1

        if show_all:
            for point in self.objects:
                pos = point.xy
                ax.scatter(*pos, color=point.color, s=25, alpha=0.2)
        if robot_pos is not None:
            x_end = robot_pos.x + 0.2 * robot_pos.cos
            y_end = robot_pos.y + 0.2 * robot_pos.sin
            ax.plot([robot_pos.x, x_end], [robot_pos.y, y_end])
            ax.scatter(*robot_pos.xy, color="black", s=60)
        if kick_pos is not None:
            x_end = kick_pos.x + 0.2 * kick_pos.cos
            y_end = kick_pos.y + 0.2 * kick_pos.sin
            ax.plot([kick_pos.x, x_end], [kick_pos.y, y_end])
            ax.scatter(*kick_pos.xy, color="cyan", s=60)
        if path is not None:
            points_x = [x.x for x in path]
            points_y = [x.y for x in path]
            ax.plot(points_x, points_y, marker="o", color='#37BB37')
            # compute differences
            x_diff = np.diff(points_x)
            y_diff = np.diff(points_y)
            pos_x = points_x[:-1] + x_diff / 2
            pos_y = points_y[:-1] + y_diff / 2
            norm = np.sqrt(x_diff**2 + y_diff**2)
            ax.quiver(pos_x, pos_y, x_diff / norm, y_diff / norm,
                      angles="xy", zorder=5, pivot="mid")
        if danger_zones is not None:
            for zone in danger_zones:
                ax.add_patch(patches.Circle(zone.c.xy, zone.r,
                                            facecolor='r', edgecolor='r',
                                            linewidth=2, alpha=0.1))

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

    def merge_objects(self, debug_info: bool = False) -> tuple:
        """
        Reduce duplicates of objects to their respective most probable amount.

        :param debug_info: boolean for debug
        :return: most probable objects and their amounts of sources
        """
        objects = {}
        merge_count = {}
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

                dists = [pole.position.distance(x) for x in merged]
                is_merged = False
                for k, x in enumerate(dists):
                    # merge into existing object
                    if x < self.threshold:
                        merged[k].set_position(average(merged[k], pole))
                        merged_counter[k] += 1
                        is_merged = True

                if is_merged:
                    continue
                else:
                    merged.append(pole)
                    merged_counter.append(1)

            sorted_objects = [obj for _,
                              obj in sorted(zip(merged_counter, merged),
                                            key=lambda x: x[0], reverse=True)]
            objects[o_type] = sorted_objects
            merge_count[o_type] = merged_counter
        if debug_info:
            print(merge_count)
        return objects, merge_count

    def determine_kick_pos(self, dist: float = 1) -> Point:
        """
        Calculate Kick position.

        :param dist: requested distance from ball, default = 1 m
        :return: Kick position
        """
        poles: list[RigidObject] = self.poles
        if len(poles) < 2:
            raise ProcessError("Cannot determine kick position, "
                               "not enough poles!")
        p1: np.array = poles[0].xy
        p2: np.array = poles[1].xy
        ball = self.ball
        if not ball:
            raise ProcessError("Cannot determine kick position, no ball!")
        ball_pos: np.array = ball[0].xy
        pole_center = np.array((p1 + p2) / 2)
        vector_line = ball_pos - pole_center
        v_length = np.linalg.norm(vector_line)
        pos = np.array(ball_pos + dist * vector_line / v_length)
        angle_rad = np.arctan2(-vector_line[1], -vector_line[0])
        return Point(*pos, angle_rad)

    def routing(self, s_pos: Point, f_pos: Point) -> list:
        """
        Algorithm for avoiding objects (their respective danger zones).

        :param s_pos: starting position
        :param f_pos: finish position
        :return: list of positions along the route
        """
        route = [s_pos, f_pos]
        dz = self.danger_zones
        if any(zone.is_inner(f_pos) for zone in dz):
            return []
        change = True
        change_counter = 0
        while change and change_counter < 10:
            change = False
            for i in range(len(route) - 1):
                line = Line(route[i], route[i + 1])
                seg = Segment(route[i], route[i + 1])
                for zone in sorted(dz, key=lambda z: z.c.distance(route[i])):
                    intersects = intersection(zone, line)
                    if (not intersects or intersects[0] == intersects[1] or
                            not (seg.is_element_of(intersects[0]) or
                                 seg.is_element_of(intersects[1]))):
                        continue
                    chord_seg = Segment(*intersects)
                    diameter_line = Line(chord_seg.midpoint, zone.c)
                    new_stop_candidates = intersection(
                        Circle(zone.c, 2 * zone.r -
                               zone.c.distance(chord_seg.midpoint)),
                        diameter_line
                    )
                    if np.isclose(*(p.distance(self.ball[0]) for p in
                                    new_stop_candidates)):
                        new_stop = min(new_stop_candidates,
                                       key=lambda p: p.distance(route[i]))
                    else:
                        new_stop = max(new_stop_candidates,
                                       key=lambda p: p.distance(self.ball[0]))


                    while any(z.is_inner(new_stop) for z in dz):
                        new_stop_candidates = intersection(
                            Circle(zone.c, zone.c.distance(new_stop) +
                                   DISCRETE_INCREMENT),
                            Line(new_stop, zone.c)
                        )
                        if np.isclose(*(p.distance(self.ball[0]) for p in
                                        new_stop_candidates)):
                            new_stop = min(new_stop_candidates,
                                           key=lambda p: p.distance(route[i]))
                        else:
                            new_stop = max(new_stop_candidates,
                                           key=lambda p: p.distance(
                                               self.ball[0]))

                    route.insert(i + 1, new_stop)
                    change = True
                    change_counter += 1
                    break
        for point_index in range(1, len(route) - 1):
            vector = np.append(Line(route[point_index], route[point_index + 1])
                               .direction_vector.xy, 0)
            zero_angle_vector = np.array((1, 0, 0))
            route[point_index].angle = np.arctan2(
                np.cross(zero_angle_vector, vector)[2],
                np.dot(zero_angle_vector, vector)
            )
        return route


if __name__ == "__main__":
    mapA = Map()

    def ao(x: float, y: float, t: int) -> None:
        """Add object, testing function."""
        obj = RigidObject(0, 0, 0, 0, RigidType(t))
        obj.set_position(Point(x, y))
        mapA.add_object(obj, Point(0, 0))

    """
    ao(0.2, -0.5, 1)
    ao(0.4, 0, 2)
    ao(0.7, -0.4, 2)
    ao(-0.35, -0.15, 3)
    kick_pos_ = mapA.determine_kick_pos(dist=0.7)
    path_ = mapA.routing(Point(0, 0), kick_pos_)
    print(*path_, sep="\n")
    mapA.show(kick_pos=kick_pos_, path=path_, danger_zones=mapA.danger_zones)
    """

    ao(0, -0.32, 1)
    ao(0.4, 0, 2)
    ao(0.7, -0.4, 2)
    ao(-0.4, 0.1, 3)
    kick_pos_ = mapA.determine_kick_pos(dist=0.7)
    path_ = mapA.routing(Point(0, 0), kick_pos_)
    print(*path_, sep="\n")
    mapA.show(kick_pos=kick_pos_, path=path_, danger_zones=mapA.danger_zones)
