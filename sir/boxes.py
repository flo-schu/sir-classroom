import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def find_clusters(arr):
    clusters = []
    visited = np.zeros_like(arr, dtype=bool)
    nrows, ncols = arr.shape

    def get_cluster(i, j, num):
        cluster = []
        stack = [(i, j)]
        while stack:
            x, y = stack.pop()
            if visited[x, y] or arr[x, y] != num:
                continue
            visited[x, y] = True
            cluster.append((x, y))
            # Check the 4-connected neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < nrows and 0 <= ny < ncols and not visited[nx, ny] and arr[nx, ny] == num:
                    stack.append((nx, ny))
        return cluster

    for i in range(nrows):
        for j in range(ncols):
            if not visited[i, j] and not np.isnan(arr[i, j]):
                num = arr[i, j]
                cluster = get_cluster(i, j, num)
                if cluster:
                    min_x = min(x for x, y in cluster)
                    max_x = max(x for x, y in cluster)
                    min_y = min(y for x, y in cluster)
                    max_y = max(y for x, y in cluster)
                    clusters.append((min_x, min_y, max_x - min_x + 1, max_y - min_y + 1))

    return clusters

def draw_boxes(ax, clusters):
    for (x, y, width, height) in clusters:
        rect = patches.Rectangle((y-0.5, x-0.5), width, height, linewidth=1, edgecolor='b', facecolor='none')
        ax.add_patch(rect)

