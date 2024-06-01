from datetime import time
import numpy as np
from classroom import Classroom

class Person:
    def __init__(self, name:str, table:int=None, virus_concentration:float=0.0):
        self.name = name
        self.table = table

        # parameters
        self.sick_threshold = 1000
        self.stayhome_threshold = np.inf
        self.emission_rate_constant = 0.2
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

    def stay_at_home(self):
        if self.virus_concentration > self.stayhome_threshold:
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

    def emit_virus(self, classroom: Classroom, dt):
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

        self.emit_virus(classroom, dt)
        self.infection_dynamic(classroom, dt)
        self.call_in_sick()