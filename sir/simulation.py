from datetime import datetime, timedelta, time

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from boxes import find_clusters, draw_boxes

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
            self.table_assignment = classroom_map.values
            self.grid_size = classroom_map.values.shape
            self.table_boxes = find_clusters(self.table_assignment)

        # Controls the rate of spreading
        self.diffusion_coefficient = diffusion_coefficient  
        self.decay_rate_constant = 0.05

        self.airing_efficiency = airing_efficiency
        self.airing_duration = airing_duration
        # Initialize the concentration grid
        self.concentration = np.zeros(self.grid_size)

    def update_concentration(self):
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
        self.update_concentration()

        if self.time.time() == time(hour=12):
            self.air_the_room(self.airing_duration)


class Pupil:
    def __init__(self, name:str, table:int=None, virus_concentration:float=0.0, 
                 emission_rate=0.2):
        self.name = name
        self.table = table

        # parameters
        self.sick_threshold = 1000
        self.emission_rate_constant = emission_rate
        self.viral_growth_rate_constant = 0.1
        self.antibody_growth_rate_constant = 0.0002
        self.antibody_decay_rate_constant = 0.00002
        self.viral_uptake_rate_constant = 0.1
        self.immune_defense_rate_constant = 0.01

        # state variables (zustandsvariablen)
        self.is_in_classroom = False
        self.position = None
        if np.isnan(virus_concentration):
            self.virus_concentration = 0.0
        else:
            self.virus_concentration = virus_concentration
        self.antibody_concentration = 0.00001

    def __repr__(self):
        return f"{self.name.capitalize()}(tisch={self.table})"

    def go_to_school(self, classroom: Classroom):
        self.position = np.where(classroom.table_assignment == self.table)
        rng = classroom.rng

        if self.position is None:
            xposition = rng.choice(np.arange(1, classroom.grid_size-1), replace=False)
            yposition = rng.choice(np.arange(1, classroom.grid_size-1), replace=False)
            self.position = (xposition, yposition)
        
        self.is_in_classroom = True

    def go_home(self):
        self.position = None
        self.is_in_classroom = False

    def call_in_sick(self):
        if self.virus_concentration > self.sick_threshold:
            self.go_home()

    def infection_dynamic(self, classroom, dt):
        if self.is_in_classroom:
            Cv_env = classroom.concentration[*self.position].mean()
        else:
            Cv_env = 0.0
        
        Cv_dt = (
            self.virus_concentration * self.viral_growth_rate_constant +
            Cv_env * self.viral_uptake_rate_constant -
            self.virus_concentration * self.antibody_concentration * self.immune_defense_rate_constant
        )

        Ca_dt = (
            self.virus_concentration * self.antibody_growth_rate_constant -
            self.antibody_concentration * self.antibody_decay_rate_constant
        )
        
        self.virus_concentration += Cv_dt * dt / classroom.time_unit
        self.antibody_concentration += Ca_dt * dt / classroom.time_unit

    def emit_virus(self, classroom: Classroom):
        if self.is_in_classroom:
            classroom.concentration[*self.position] += (
                self.virus_concentration * self.emission_rate_constant *
                dt / classroom.time_unit
            )

    def step(self, classroom, dt):
        # incorporate different behavior depending on time
        # Weekday, time of day, ...
        if classroom.time.time() == time(hour=8):
            self.go_to_school(classroom)

        if classroom.time.time() == time(hour=14):
            self.go_home()

        self.emit_virus(classroom)
        self.infection_dynamic(classroom, dt)
        self.call_in_sick()

# initialize simulations
t = datetime(year=2024, month=5, day=15, hour=7)
dt = timedelta(minutes=5)
t_end = t + timedelta(weeks=2)

classroom_map = pd.read_excel("data/classroom.xlsx", sheet_name="U-shape", 
                              index_col=0)
pupil_list = pd.read_excel("data/namelist.xlsx", sheet_name="Klasse-1a")
room = Classroom(room_map=classroom_map)
room.time = t

pupils = []
for _, row in pupil_list.iterrows():
    pupil = Pupil(name=row.Name, table=row.Table, virus_concentration=row.Virenlast)
    pupils.append(pupil)

# make sure all concentration is going to zero 
room.air_the_room(duration=np.inf)

# run the simulation over all timesteps
# add progress-bar
plt.ion()
fig, (ax, ax_graph) = plt.subplots(2, 1, figsize=(10, 14))
room.concentration[0,0] = 100
cax = ax.matshow(room.concentration, cmap='cool')

# plot to track the developemnt of infection over time.

room.concentration[0,0] = 0
draw_boxes(ax=ax, clusters=room.table_boxes)

fig.colorbar(cax)
ax.set_title("Virus Concentration")


while room.time < t_end:
    room.step(dt=dt)

    for pupil in pupils:
        pupil.step(classroom=room, dt=dt)

    cax.set_data(room.concentration)
    ax.set_title(f"Time Step: {room.time}")
    plt.pause(0.001)

plt.ioff()
plt.show()
# add plot for visualization and use make a gif at the  end