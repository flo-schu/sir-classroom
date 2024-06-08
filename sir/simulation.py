from typing import List
import numpy as np
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider

from classroom import Classroom
from agents import Person

class PlayPause:
    long_pause = True

    def _pause(self, event):
        self.long_pause = True

    def _play(self, event):
        self.long_pause = False

class Playspeed:
    pause = 1.5

    def update(self, val):
        self.pause = val


def run(
    iteration: callable, 
    room: Classroom, 
    pupils: list[Person], 
    t_end: datetime, 
    dt: timedelta
):

    # make sure all concentration is going to zero 
    room.air_the_room(duration=np.inf)

    # run the simulation over all timesteps
    # add progress-bar
    plt.ion()

    # set up figure
    fig = plt.figure(figsize=(10,14))
    G = fig.add_gridspec(5, 2)
    ax = fig.add_subplot(G[:3, :])
    ax_graph = fig.add_subplot(G[3, :])
    ax_bars = fig.add_subplot(G[4, :])

    # ax.set_xticklabels([])
    # ax.set_yticklabels([])
    # ax.set_xticks([])
    # ax.set_yticks([])
    ax.set_title(f"Zeit: {room.daymap[room.time.isoweekday()]}, {room.time}")

    room.concentration[0,0] = 100
    cax = ax.matshow(room.concentration, cmap='cool')

    # set up virus plot
    agent_viral_conc = calc_viral_load(agents=pupils)
    l_va = ax_graph.plot(room.time, agent_viral_conc, lw=1, color="black", 
                         label="Durchschnitt")[0]
    ax_graph.legend(loc="upper right")
    ax_graph.set_xlim(room.time, t_end)
    ax_graph.set_ylim(0, agent_viral_conc*1.1)
    ax_graph.set_xlabel("Time")
    ax_graph.set_ylabel("Virus concentration")
    fig.tight_layout()

    # set up bar plot
    n = 5
    pupil_selection = pupils[slice(n)]
    virus_concs_sel = [p.virus_concentration for p in pupil_selection]
    antib_concs_sel = [p.antibody_concentration * 100 for p in pupil_selection]
    virus_bars = ax_bars.bar(
        x=np.arange(n) - 0.2, 
        height=virus_concs_sel, 
        width=2/n
    )

    antib_bars = ax_bars.bar(
        x=np.arange(n) + 0.2, 
        height=antib_concs_sel, 
        width=2/n
    )
    max_bars = np.max(virus_concs_sel + antib_concs_sel)
    # add interactive slider
    callback = Playspeed()
    axplayspeed = fig.add_axes([0.2, 0.4, 0.6, 0.02])
    splayspeed = Slider(
        ax=axplayspeed, label="Pause [s]", 
        valmin=0.001, valmax=2, valinit=1.5, valstep=0.001
    )
    splayspeed.on_changed(callback.update)
    # plot to track the developemnt of infection over time.

    room.concentration[0,0] = 0
    room.draw_boxes(ax=ax)
    room.table_names = {
        p.table: ax.text(*p.get_table_location(room, y_offset=2), p.name, ha="center") 
        for p in pupils
    }


    virus_load_agents = []
    time_traj = []

    while room.time < t_end:
        iteration(
            room=room,
            pupils=pupils,
            dt=dt
        )

        agent_viral_conc = calc_viral_load(agents=pupils)

        virus_load_agents.append(agent_viral_conc)
        time_traj.append(room.time)
        l_va.set_xdata(time_traj)
        l_va.set_ydata(virus_load_agents)
        ax_graph.set_ylim(0, np.max(virus_load_agents)*1.1)

        # virus concentrations
        virus_concs_sel = [p.virus_concentration for p in pupil_selection]
        antib_concs_sel = [p.antibody_concentration * 100 for p in pupil_selection]
        [p.set_height(c) for p, c in zip(virus_bars.patches, virus_concs_sel)]
        [p.set_height(c) for p, c in zip(antib_bars.patches, antib_concs_sel)]
        max_bars = np.max(virus_concs_sel+antib_concs_sel+[max_bars])
        ax_bars.set_ylim(0, max_bars*1.1)

        cax.set_data(room.concentration)
        ax.set_title(f"Zeit: {room.daymap[room.time.isoweekday()]}, {room.time}")

        plt.pause(callback.pause)
    
    # fig.colorbar(cax)
    ax.set_title("Virus Concentration")

    plt.ioff()
    plt.show()
    # add plot for visualization and use make a gif at the  end

def iteration(room, pupils, dt):
    room.step(dt=dt)

    for pupil in pupils:    
        pupil.step(classroom=room, dt=dt)
    

def calc_viral_load(agents: List[Person]):
    return np.mean([a.virus_concentration for a in agents])