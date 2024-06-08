from datetime import time
import numpy as np
from scipy.stats import truncnorm, lognorm
from matplotlib import pyplot as plt
from classroom import Classroom

class Person:
    def __init__(self, name:str, table:int=None, virus_concentration:float=0.0):
        self.name = name
        self.table = table

        # parameters
        self.sick_threshold = 1000
        self.symptoms_threshold = np.inf
        self.emission_rate_constant = 0.2
        self.viral_growth_rate_constant = 0.1
        self.antibody_decay_rate_constant = 0.005
        self.viral_uptake_rate_constant = 0.1
        self.viral_uptake_threshold = 0.5
        self.immune_defense_rate_constant = 0.01
        
        # create distribution and draw from it
        self.mean_antibody_growth_rate_constant = 0.0002
        self.sigma_antibody_growth_rate_constant = 0.3
        self.dist_antibody_growth_rate_constant = self.lognorm_dist(
            mean=self.mean_antibody_growth_rate_constant,
            scale=self.sigma_antibody_growth_rate_constant
        )
        self.antibody_growth_rate_constant = float(self.dist_antibody_growth_rate_constant.rvs(1))

        # state variables (zustandsvariablen)
        self.is_in_classroom = False
        self.position = None
        self.old_position = None
        self.moved_at_time = None

        if np.isnan(virus_concentration):
            self.virus_concentration = 0.0
        else:
            self.virus_concentration = virus_concentration
        self.antibody_concentration = 0.00001

    def __repr__(self):
        return f"{self.name.capitalize()}(tisch={self.table})"

    def get_table_location(self, classrom: Classroom, x_offset=0, y_offset=0):
        y, x = np.where(classrom.table_assignment == self.table)
        return (x.mean() + x_offset, y.mean() + y_offset)

    def go_to_school(self, classroom: Classroom):
        self.position = np.where(classroom.table_assignment == self.table)
        rng = classroom.rng

        if self.position is None:
            xposition = rng.choice(np.arange(1, classroom.grid_size-1), replace=False)
            yposition = rng.choice(np.arange(1, classroom.grid_size-1), replace=False)
            self.position = (xposition, yposition)
        
        self.is_in_classroom = True
        classroom.table_patches[self.table].set_facecolor("white")

    def go_home(self, classroom):
        self.position = None
        self.is_in_classroom = False
        classroom.table_patches[self.table].set_facecolor("none")

    def will_move(self, classroom):
        return self.table in classroom.moving

    def call_in_sick(self, classroom):
        if self.is_sick:
            self.go_home(classroom)

    def stay_at_home(self, classroom):
        if self.shows_symptoms:
            self.go_home(classroom)

    def infection_dynamic(self, classroom, dt):
        if self.is_in_classroom:
            Cv_env = classroom.concentration[*self.position].mean()
        else:
            Cv_env = 0.0
        
        Cv_dt = (
            self.virus_concentration * self.viral_growth_rate_constant +
            np.max([Cv_env - self.viral_uptake_threshold, 0]) * self.viral_uptake_rate_constant -
            self.virus_concentration * self.antibody_concentration * self.immune_defense_rate_constant
        )

        Ca_dt = (
            self.virus_concentration * self.antibody_growth_rate_constant -
            self.antibody_concentration * self.antibody_decay_rate_constant
        )
        
        self.virus_concentration += Cv_dt * dt / classroom.time_unit
        self.antibody_concentration += Ca_dt * dt / classroom.time_unit

        if self.virus_concentration > self.sick_threshold:
            self.is_sick = True
        else:
            self.is_sick = False

        if self.virus_concentration > self.symptoms_threshold:
            self.shows_symptoms = True
        else:
            self.shows_symptoms = False


    def emit_virus(self, classroom: Classroom, dt):
        if self.is_in_classroom:
            classroom.concentration[*self.position] += (
                self.virus_concentration * self.emission_rate_constant *
                dt / classroom.time_unit
            )

    def find_free_spot(self, classroom):
        tables = list(set(classroom.table_patches.keys()).difference([self.table]))
        table_to_visit = np.random.choice(tables, 1)[0]
        x, y, h, w = classroom.table_boxes[table_to_visit]

        x_range = np.arange(x - w, x + w * 2)
        y_range = np.arange(y - h, y + h * 2)

        surrounding = np.isnan(classroom.table_assignment[np.ix_(x_range, y_range)])
        surrounding = ~np.diff(surrounding, append=True, axis=0) * surrounding
        surrounding = ~np.diff(surrounding, append=True, axis=1) * surrounding
        surrounding[-1, :] = False
        surrounding[:, -1] = False

        x_possible, y_possible = np.where(surrounding)
        x_new_pos = np.random.choice(x_possible + x - w)
        y_new_pos = np.random.choice(y_possible + y - h)

        new_position = (
            np.repeat(np.arange(x_new_pos, x_new_pos+w), 2),
            np.tile(np.arange(y_new_pos, y_new_pos+h), 2)
        )

        return new_position


    def move(self, classroom: Classroom):
        if self.is_in_classroom and self.will_move(classroom):
            self.old_position = self.position
            self.position = self.find_free_spot(classroom)

            tp = classroom.table_patches[self.table]
            tp.set_xy(reversed([x.min() - 0.5 for x in self.position]))
            tp.set_edgecolor("red") 

            txt = classroom.table_names[self.table]
            txt.set_y(self.position[0].mean() +1.5)
            txt.set_x(self.position[1].mean())

    def move_back(self, classroom: Classroom):
        if self.is_in_classroom and self.will_move(classroom):
            self.position = self.old_position

            tp = classroom.table_patches[self.table]
            tp.set_xy(reversed([x.min()-0.5 for x in self.position]))
            tp.set_edgecolor("black")

            txt = classroom.table_names[self.table]
            txt.set_x(self.position[1].mean())
            txt.set_y(self.position[0].mean() + 2)

    def step(self, classroom, dt):
        # incorporate different behavior depending on time
        # Weekday, time of day, ...
        if classroom.time.time() == time(hour=8) and classroom.is_weekday and not self.is_sick:
            self.go_to_school(classroom)

        if classroom.time.time() == time(hour=14):
            self.go_home(classroom)

        self.emit_virus(classroom, dt)
        self.infection_dynamic(classroom, dt)
        self.call_in_sick(classroom)

    def truncnorm_dist(self, mean, sigma):
        # create a truncated distribution, clipped at zero
        return truncnorm(
            a=(0-mean) / sigma, 
            b=np.inf,
            loc=mean,
            scale=sigma,
        )

    def lognorm_dist(self, mean, scale):
        return lognorm(scale=mean, s=scale)

    def plot_antibody_growthrate_constant_distribution(self):
        x = np.linspace(
            0,
            self.dist_antibody_growth_rate_constant.ppf(0.9999),
            1000
        )
        pdf = self.dist_antibody_growth_rate_constant.pdf(x)

        plt.plot(x, pdf)
        plt.xlabel("Antibody growth rate")