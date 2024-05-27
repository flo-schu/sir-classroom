from datetime import datetime, timedelta, time

import numpy as np

from boxes import find_clusters

class Classroom:
    table_assignment = {}
    pupils = []
    time: datetime = datetime(year=2024, month=1, day=1, hour=0, minute=0)
    time_unit = timedelta(hours=1)

    def __init__(
        self, 
        room_map=None,
        grid_size=(30, 30), 
        seed=1, 
        diffusion_coefficient=0.7, 
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


    def step(self, dt: timedelta):
        self.time += dt

        # combines methods for one timestep
        self.update_concentration(dt=dt)

        if self.time.time() == time(hour=12):
            self.air_the_room(self.airing_duration)
