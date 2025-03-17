import numpy as np
import matplotlib.pyplot as plt


def pathfinder(start: np.array, finish: np.array):



def show_graph():
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect(1)
    # ax.scatter(1, 2, color="black", s=60)
    xlim = plt.xlim()
    ylim = plt.ylim()
    x_range = max(abs(xlim[0]), abs(xlim[1]))
    y_range = max(abs(ylim[0]), abs(ylim[1]))
    max_range = max(x_range, y_range) * 1.1
    plt.xlim(-max_range, max_range)
    plt.ylim(-max_range, max_range)
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axvline(0, color='black', linewidth=1, linestyle='--')
    plt.show()


if __name__ == "__main__":
    show_graph()
