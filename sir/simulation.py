import numpy as np
import datetime as dt
from matplotlib import pyplot as plt

class Classroom:
    table_assignment = {}
    pupils = []

    def __init__(self, seed=1, grid_size=30, diffusion_coefficient=0.2, 
                 airing_efficiency=0.2,
                 airing_duration=10):
        self.rng = np.random.default_rng(seed)
        self.grid_size = grid_size
        # Controls the rate of spreading
        self.diffusion_coefficient = diffusion_coefficient  
        self.airing_efficiency = airing_efficiency
        self.airing_duration = airing_duration
        # Initialize the concentration grid
        self.concentration = np.zeros((grid_size, grid_size))

    def update_concentration(self):
        new_concentration = self.concentration.copy()
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                # Apply the diffusion equation (discrete Laplacian)
                new_concentration[i, j] = (
                    self.concentration[i, j] + 
                    self.diffusion_coefficient * (
                        self.concentration[i+1, j] + 
                        self.concentration[i-1, j] +
                        self.concentration[i, j+1] + 
                        self.concentration[i, j-1] - 
                        4 * self.concentration[i, j]
                    )
                )
        self.concentration = new_concentration

    def air_the_room(self, duration):
        self.concentration[:,:] = self.concentration.mean() * np.exp(-duration * self.airing_efficiency)

    def assign_tables_to_pupils(self, assignment=None):
        # updates table assignment randomly or by a mapping
        ...

    def step(self, time):
        # combines methods for one timestep
        self.update_concentration()

        if time.time() == dt.time(hour=12):
            self.air_the_room(self.airing_duration)

class Pupil:
    def __init__(self, name, emission_rate=0.2):
        self.name = name

        # parameters
        self.sick_threshold = None
        self.emission_rate = emission_rate

        # state variables (zustandsvariablen)
        self.is_in_classroom = False
        self.position = None
        self.virus_concentration = 1000
        self.antibody_concentration = 0.00001

    def go_to_school(self, classroom: Classroom):
        self.position = classroom.table_assignment.get(self.name, None)
        rng = classroom.rng

        if self.position is None:
            xposition = rng.choice(np.arange(1, classroom.grid_size-1), replace=False)
            yposition = rng.choice(np.arange(1, classroom.grid_size-1), replace=False)
            self.position = (xposition, yposition)
        
        self.is_in_classroom = True

    def go_home(self):
        self.position = None
        self.is_in_classroom = False

    def infection_dynamic(self, classroom):
        pass

    def emit_virus(self, classroom: Classroom):
        if self.is_in_classroom:
            classroom.concentration[*self.position] += (
                self.virus_concentration * self.emission_rate)

    def step(self, classroom, time):
        # incorporate different behavior depending on time
        # Weekday, time of day, ...
        if time.time() == dt.time(hour=8):
            self.go_to_school(classroom)

        if time.time() == dt.time(hour=14):
            self.go_home()

        self.emit_virus(classroom)


# initialize simulations
t0 = dt.datetime(year=2024, month=5, day=15, hour=8)
time = [t0 + dt.timedelta(minutes=10*x) for x in range(24 * 7 * 4 * 6)]
room = Classroom()

pupils = []
for name in ["Agnes", "Tiffi", "Ben", "Peter", "Jim", "Samantha"]:
    pupil = Pupil(name)
    pupils.append(pupil)

# make sure all concentration is going to zero 
room.air_the_room(duration=np.inf)

# run the simulation over all timesteps
# add progress-bar
plt.ion()
fig, ax = plt.subplots()
room.concentration[0,0] = 100
cax = ax.matshow(room.concentration, cmap='cool')
room.concentration[0,0] = 0

fig.colorbar(cax)
ax.set_title("Virus Concentration")


for t in time:
    room.step(time=t)

    for pupil in pupils:
        pupil.step(classroom=room, time=t)

    if t.time().minute == 0:
        cax.set_data(room.concentration)
        ax.set_title(f"Time Step: {t}")
        plt.pause(0.001)

plt.ioff()
plt.show()
    # add plot for visualization and use make a gif at the  end