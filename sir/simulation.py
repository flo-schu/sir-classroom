import numpy as np
from matplotlib import pyplot as plt

from boxes import draw_boxes

def run(iteration, room, pupils, t_end, dt):

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

    while room.time < t_end:
        iteration(
            room=room,
            pupils=pupils,
            dt=dt
        )

        cax.set_data(room.concentration)
        ax.set_title(f"Time Step: {room.time}")
        plt.pause(0.001)

    
    fig.colorbar(cax)
    ax.set_title("Virus Concentration")

    plt.ioff()
    plt.show()
    # add plot for visualization and use make a gif at the  end

def iteration(room, pupils, dt):
    room.step(dt=dt)

    for pupil in pupils:
        pupil.step(classroom=room, dt=dt)
