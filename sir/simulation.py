import numpy as np

class Classroom:
    table_assignment = {}
    pupils = []

    def update_concentration(self):
        ...

    def air_the_room(self, duration):
        ...

    def place_table(self, location):
        ...

    def assign_tables_to_pupils(self, assignment=None):
        # updates table assignment randomly or by a mapping
        ...

    def step(self, time):
        # combines methods for one timestep
        self.update_concentration(self)
        ...


class Pupil:
    def __init__(self, name):
        self.name = name
        self.is_in_classroom = False

        # parameters
        self.sick_threshold = ...

        # state variables (zustandsvariablen)
        self.virus_concentration = 0
        self.antibody_concentration = 0.00001

    def go_to_school(self):
        ...

    def go_to_table(self, classroom: Classroom):
        self.table = classroom.table_assigment[self.name]
        self.is_in_classroom = True

    def infection_dynamic(self, classroom):
        ...

    def step(self, classroom, time):
        # incorporate different behavior depending on time
        # Weekday, time of day, ...
        ...


# initialize simulations
room = Classroom()
room.place_tables()

pupils = []
for name in ["Agnes", "Tiffi", "Ben", "Peter", "Jim", "Samantha"]:
    pupil = Pupil(name)
    pupil.go_to_table(classroom=room)
    pupils.append(pupil)

# make sure all concentration is going to zero 
room.air_the_room(duration=np.inf)

# run the simulation over all timesteps
# add progress-bar
for t in time:
    room.step()

    for pupil in pupils:
        pupil.step()

    # add plot for visualization and use make a gif at the  end