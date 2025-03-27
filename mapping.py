import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from geometry import Point, Circle, Line, Segment, intersection, normalize_angle
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
from rigidobject import RigidObject, RigidType
import find_ball
from utils import ProcessError


def average(object_a: RigidObject, object_b: RigidObject):
    return Point(*np.mean([object_a.xy, object_b.xy], axis=0))


def transform(position: Point, base_pos: Point, debug_info: bool = False):
    if debug_info: print("Position before rot.", position)
    if debug_info: print("Robot position: ", base_pos)
    transform_matrix = np.array([[base_pos.cos, -base_pos.sin, base_pos.x],
                                [base_pos.sin, base_pos.cos, base_pos.y],
                                [0, 0, 1]])
    result = np.dot(transform_matrix, position.homog_xy)[:2]
    if debug_info: print("After rotation")
    return Point(*result)


def has_all(objects: list):
    poles = 0
    ball = 0

    for obj in objects:
        if obj.o_type == RigidType.POLE and 40 <= obj.im_p.x <= 600: 
            poles += 1
        elif obj.o_type == RigidType.BALL and 40 <= obj.im_p.x <= 600:
            ball += 1

    if poles == 2 and ball == 1:
        return True
    else:
        return False


class Map:
    def __init__(self, turtle, threshold=0.2):
        self.objects = []
        self.MAX_OBJECTS = {RigidType.POLE: 2, RigidType.BALL: 1}
        self.MIN_MATCHES = 2
        self.threshold = threshold

        self.turtle = turtle

    @property
    def poles(self):
        return self.merge_objects()[0][RigidType.POLE]

    @property
    def ball(self):
        return self.merge_objects()[0][RigidType.BALL]

    @property
    def obstacles(self):
        return self.merge_objects()[0][RigidType.OBST]

    @property
    def dead_zones(self):
        obj_dict, _ = self.merge_objects()
        dead_zones = []
        for pole in obj_dict[RigidType.POLE]:
            dead_zones.append(Circle(pole.position, 0.3))
        for obst in obj_dict[RigidType.OBST]:
            dead_zones.append(Circle(obst.position, 0.3))
        for ball in obj_dict[RigidType.BALL]:
            dead_zones.append(Circle(ball.position, 0.4))
        return dead_zones
    
    @property
    def has_all(self):
        obj_dict, counter = self.merge_objects()
        correct = {x:0 for x in obj_dict}
        for key in obj_dict:
            for i, _ in enumerate(obj_dict[key]):
                if counter[key][i] >= self.MIN_MATCHES:
                    correct[key] += 1
        if correct[RigidType.POLE] >= self.MAX_OBJECTS[RigidType.POLE] and correct[RigidType.BALL] >= self.MAX_OBJECTS[RigidType.BALL]:
            return True
        else:
            return False
    
    def reset(self):
        self.objects = []

    def add_object(self, object_a: RigidObject, robot_pos: Point, debug_info: bool = False):
        if debug_info: print("BEFORE ROTATION:", object_a.position)
        object_a.set_position(transform(object_a.position, robot_pos, debug_info))
        if debug_info: print("AFTER ROTATION:", object_a.position)
        self.objects.append(object_a)

    def is_max_reached(self, o_type: RigidType, count: dict) -> bool:
        is_max_poles = (o_type == RigidType.POLE and count[o_type] >= self.MAX_OBJECTS[o_type])
        is_max_ball = (o_type == RigidType.BALL and count[o_type] >= self.MAX_OBJECTS[o_type])
        return is_max_poles or is_max_ball

    def show(self, show_all: bool=False, show_merged: bool=True, robot_pos: Point=None,
             kick_pos: Point=None, path: list=None, dead_zones: list=None, debug_info: bool = False)-> None:
        _, ax = plt.subplots(figsize=(6, 6), dpi=100)  # Set 6x6 inches
        ax.set_aspect(1)  # X, Y axis ratio 1:1
        if show_merged:
            obj, _ = self.merge_objects()
            type_counter = {x:0 for x in obj}
            for object_type, points in obj.items():
                for point in points:
                    position = point.xy
                    if self.is_max_reached(object_type, type_counter):
                            ax.scatter(*position, color=point.color, s=50, edgecolors='red', linewidths=2)
                    else:
                        ax.scatter(*position, color=point.color, s=50)
                        if object_type == RigidType.BALL:
                            ax.scatter(*position, facecolors='none', edgecolors='orange', s=50, alpha=0.5)
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
            pos_x = points_x[:-1] + x_diff/2
            pos_y = points_y[:-1] + y_diff/2
            norm = np.sqrt(x_diff**2+y_diff**2)
            ax.quiver(pos_x, pos_y, x_diff/norm, y_diff/norm, angles="xy", zorder=5, pivot="mid")
        if dead_zones is not None:
            for zone in dead_zones:
                ax.add_patch(patches.Circle(zone.c.xy, zone.r, facecolor='r', edgecolor='r', linewidth=2, alpha=0.1))

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

            sorted_objects = [obj for _, obj in sorted(zip(merged_counter, merged), key=lambda x: x[0], reverse=True)]
            objects[o_type] = sorted_objects
            merge_count[o_type] = merged_counter
        print(merge_count)
        return objects, merge_count

    def determine_kick_pos(self, dist: float=1):
        poles: list[RigidObject] = self.poles
        if len(poles) < 2: raise ProcessError("Cannot determine kick position, not enough poles!")
        p1: np.array = poles[0].xy
        p2: np.array = poles[1].xy
        ball = self.ball
        if not ball: raise ProcessError("Cannot determine kick position, no ball!")
        ball_pos: np.array = ball[0].xy
        pole_center = np.array((p1 + p2) / 2)
        vector_line = ball_pos - pole_center
        v_length = np.linalg.norm(vector_line)
        pos = np.array(ball_pos + dist * vector_line / v_length)
        angle_rad = np.arctan2(-vector_line[1], -vector_line[0])
        return Point(*pos, angle_rad)

    def routing(self, s_pos: Point, f_pos: Point):
        route = [s_pos, f_pos]
        dz = self.dead_zones
        if any(zone.is_inner(f_pos) for zone in dz): return []
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
                            not (seg.is_element_of(intersects[0]) or seg.is_element_of(intersects[1]))):
                        continue
                    chord_seg = Segment(*intersects)
                    diameter_line = Line(chord_seg.midpoint, zone.c)
                    new_stop_candidates = intersection(Circle(zone.c, 2 * zone.r - zone.c.distance(chord_seg.midpoint)), diameter_line)
                    new_stop = max(new_stop_candidates, key=lambda p: p.distance(self.ball[0]))
                    route.insert(i + 1, new_stop)
                    change = True
                    change_counter += 1
                    break
            # mapA.show(kick_pos=kick_pos_, path=route, dead_zones=mapA.dead_zones)
        return route

    def scan_environment(self):
        # wait for rgb image
        self.turtle.wait_for_rgb_image()
        rgb_img = self.turtle.get_rgb_image()
        all_objects = find_ball.find_objects(rgb_img)
        # wait for point cloud find position of each object
        find_ball.show_objects(rgb_img, all_objects, "Objects", True)
        self.turtle.wait_for_point_cloud()
        pc = self.turtle.get_point_cloud()
        for o in all_objects:
            o.assign_xy(pc)
        return all_objects


if __name__ == "__main__":
    mapA = Map()

    def ao(x, y, t):
        obj = RigidObject(0, 0, 0, 0, RigidType(t))
        obj.set_position(Point(x, y))
        mapA.add_object(obj, Point(0, 0))

    #ao(0.2, -0.5, 1)
    #ao(0.4, 0, 2)
    #ao(0.7, -0.4, 2)
    #ao(-0.35, -0.15, 3)
    #kick_pos_ = mapA.determine_kick_pos(dist=0.7)
    #path_ = mapA.routing(Point(0, 0), kick_pos_)
    #mapA.show(kick_pos=kick_pos_, path=path_, dead_zones=mapA.dead_zones)

    ao(0.2, -0.5, 1)
    ao(0.25, -0.5, 1)
    ao(0.2, -0.51, 1)

    ao(0.4, 0, 2)
    ao(0.42, 0, 2)
    ao(0.4, 0.05, 2)

    ao(0.7, -0.4, 2)
    ao(0.7, -0.42, 2)
    ao(0.71, -0.4, 2)

    kick_pos_ = mapA.determine_kick_pos(dist=0.7)

    print(mapA.has_all)
    mapA.show(show_all=True)
    
