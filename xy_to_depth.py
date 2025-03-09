import numpy as np
import scipy.io


def load_pc(filename):
    data = scipy.io.loadmat(filename)
    pc = data["point_cloud"]
    return pc


if __name__ == "__main__":
    pc_ = load_pc(f"test_data/test_y{1}.mat")
    pass
