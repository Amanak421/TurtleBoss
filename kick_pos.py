from visual import Visual
import numpy as np

def determine_kick_pos(pole1, pole2, ball, ball_r = 0, dist = 1):
    P1 = np.array(pole1)
    P2 = np.array(pole2)
    B = np.array(ball)

    M = np.array((P1 + P2) / 2)

    v = B - M
    r = M - B
    v_length = np.linalg.norm(v)
    u = v / v_length
    pos = np.array( B + dist * u)

    angle_rad =np.arctan2(*r)


    return np.append(pos, angle_rad)

if __name__ == "__main__":
    pole1 = [-2, 2]
    pole2 = [0, 0]
    ball = [0, 2]
    kick_pos = determine_kick_pos(pole1, pole2, ball)

    vis = Visual()
    vis.updateRobot(1, 1, 0)
    vis.setGoal(*pole1)
    vis.setGoal(*pole2)
    vis.setBall(*ball)
    print(kick_pos)
    vis.updateRobot(*kick_pos)
    input()