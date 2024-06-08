from datetime import datetime, timedelta, time

import numpy as np
import matplotlib.patches as patches

class Classroom:
    table_assignment = {}
    pupils = []
    time: datetime = datetime(year=2024, month=1, day=1, hour=0, minute=0)
    time_unit = timedelta(hours=1)
    daymap = {1: "Montag", 2: "Dienstag", 3: "Mittwoch", 4: "Donnerstag", 
              5: "Freitag", 6: "Samstag", 7: "Sonntag"}

    def __init__(
        self, 
        room_map=None,
        grid_size=(30, 30), 
        seed=1, 
        diffusion_coefficient=0.5, 
        airing_efficiency=0.2,
        airing_duration=10
    ):
        self.rng = np.random.default_rng(seed)
        if room_map is None:
            self.grid_size = grid_size

        else:
            self.table_assignment = room_map.values
            self.grid_size = room_map.values.shape
            self.table_boxes = find_clusters(self.table_assignment)

        self.table_names = {}

        # Controls the rate of spreading
        self.diffusion_coefficient = diffusion_coefficient  
        self.decay_rate_constant = 0.05

        self.airing_efficiency = airing_efficiency
        self.airing_duration = airing_duration
        # Initialize the concentration grid
        self.concentration = np.zeros(self.grid_size)

    def update_concentration(self, dt):
        new_concentration = self.concentration.copy()
        for i in range(1, self.grid_size[0]-1):
            for j in range(1, self.grid_size[1]-1):
                # Apply the diffusion equation (discrete Laplacian)
                new_concentration[i, j] = (
                    self.concentration[i, j] + (
                        self.diffusion_coefficient * (
                            self.concentration[i+1, j] + 
                            self.concentration[i-1, j] +
                            self.concentration[i, j+1] + 
                            self.concentration[i, j-1] - 
                            4 * self.concentration[i, j]
                        ) - self.concentration[i, j] * self.decay_rate_constant
                    ) * dt / self.time_unit
                )
        self.concentration = new_concentration


    def air_the_room(self, duration):
        self.concentration[:,:] = self.concentration.mean() * np.exp(-duration * self.airing_efficiency)

    @property
    def is_weekday(self):
        return not self.time.isoweekday() in (6, 7)

    def step(self, dt: timedelta):
        self.time += dt

        # combines methods for one timestep
        self.update_concentration(dt=dt)

        if self.time.time() == time(hour=12):
            self.air_the_room(self.airing_duration)
            self.draw_movers()

    def draw_boxes(self, ax):
        self.table_patches = {}
        for table, box in self.table_boxes.items():
            rect = self.draw_box(ax, box)
            self.table_patches.update({table: rect})

    def draw_movers(self):
        self.moving = np.random.choice(
            np.unique(list(self.table_names.keys())), 
            size=5
        )

    def draw_box(self, ax, box):
        x, y, width, height = box
        rect = patches.Rectangle(
            (y-0.5, x-0.5), width, height, linewidth=1, 
            edgecolor='black', facecolor='none'
        )
        ax.add_patch(rect)
        return rect


def find_clusters(arr):
    clusters = {}
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
                    clusters.update({int(num): (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)})

    return clusters