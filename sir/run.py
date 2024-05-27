from datetime import datetime, timedelta, time

import pandas as pd

from classroom import Classroom
from agents import Person
from simulation import run

# Definition der Simulation
# ==============================================================================

class Klasse10a(Classroom):
    def step(self, dt: timedelta):
        self.time += dt

        # combines methods for one timestep
        self.update_concentration(dt=dt)

        if self.time.time() == time(hour=12):
            self.air_the_room(self.airing_duration)

class Pupil(Person):
    def step(self, classroom, dt):
        # incorporate different behavior depending on time
        # Weekday, time of day, ...
        if classroom.time.time() == time(hour=8):
            self.go_to_school(classroom)

        if classroom.time.time() == time(hour=14):
            self.go_home()

        self.emit_virus(classroom, dt)
        self.infection_dynamic(classroom, dt)
        self.call_in_sick()

# define one iteration
def iteration(room, pupils, dt):
    room.step(dt=dt)

    for pupil in pupils:
        pupil.step(classroom=room, dt=dt)


# Initialisierung
# ==============================================================================

# initialize time
t = datetime(year=2024, month=5, day=15, hour=7)
dt = timedelta(minutes=5)
t_end = t + timedelta(weeks=2)

# initialize classroom
classroom_map = pd.read_excel("data/classroom.xlsx", sheet_name="U-shape", index_col=0)
pupil_list = pd.read_excel("data/namelist.xlsx", sheet_name="Klasse-1a")
room = Classroom(room_map=classroom_map)
room.time = t

# initialize pupils
pupils = []
for _, row in pupil_list.iterrows():
    pupil = Pupil(name=row.Name, table=row.Table, virus_concentration=row.Virenlast)
    pupils.append(pupil)


# Ausführung der Simulation
# ==============================================================================

run(
    iteration=iteration,
    room=room,
    pupils=pupils,
    t_end=t_end,
    dt=dt
)
