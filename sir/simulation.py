import numpy as np
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from matplotlib.widgets import Button, Slider

from classroom import Classroom

from boxes import draw_boxes

class PlayPause:
    long_pause = True

    def _pause(self, event):
        self.long_pause = True

    def _play(self, event):
        self.long_pause = False

class Playspeed:
    pause = 0.1

    def update(self, val):
        self.pause = val


def run(
    iteration: callable, 
    room: Classroom, 
    pupils: list, 
    t_end: datetime, 
    dt: timedelta
):

    # make sure all concentration is going to zero 
    room.air_the_room(duration=np.inf)

    # run the simulation over all timesteps
    # add progress-bar
    plt.ion()
    fig, (ax, ax_graph) = plt.subplots(2, 1, figsize=(10, 14))
    room.concentration[0,0] = 100
    cax = ax.matshow(room.concentration, cmap='cool')

    # add interactive buttons
    # callback = PlayPause()
    # axpause = fig.add_axes([0.7, 0.05, 0.1, 0.075])
    # axplay = fig.add_axes([0.81, 0.05, 0.1, 0.075])
    # bpause = Button(axpause, 'Pause')
    # bpause.on_clicked(callback._pause)
    # bplay = Button(axplay, 'Play')
    # bplay.on_clicked(callback._play)
        

    # add interactive slider
    callback = Playspeed()
    axplayspeed = fig.add_axes([0.2, 0.5, 0.6, 0.02])
    splayspeed = Slider(
        ax=axplayspeed, label="Pause [s]", 
        valmin=0.001, valmax=2, valinit=0.5, valstep=0.001
    )
    splayspeed.on_changed(callback.update)
    # plot to track the developemnt of infection over time.

    room.concentration[0,0] = 0
    draw_boxes(ax=ax, clusters=room.table_boxes)

    while room.time < t_end:
        iteration(
            room=room,
            pupils=pupils,
            dt=dt
        )

        cax.set_data(room.concentration)
        ax.set_title(f"Zeit: {room.daymap[room.time.isoweekday()]}, {room.time}")

        plt.pause(callback.pause)
    
    fig.colorbar(cax)
    ax.set_title("Virus Concentration")

    plt.ioff()
    plt.show()
    # add plot for visualization and use make a gif at the  end

def iteration(room, pupils, dt):
    room.step(dt=dt)

    for pupil in pupils:
        pupil.step(classroom=room, dt=dt)
