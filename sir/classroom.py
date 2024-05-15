import numpy as np
import matplotlib.pyplot as plt

# Define the grid size
grid_size = 100
time_steps = 1000
diffusion_coefficient = 0.2  # Controls the rate of spreading

# Initialize the concentration grid
concentration = np.zeros((grid_size, grid_size))

# Place an initial concentration of particles in the center
initial_concentration = 1000
center = grid_size // 2
concentration[center, center] = initial_concentration

# Function to update concentration based on diffusion
def update_concentration(concentration, diffusion_coefficient):
    new_concentration = concentration.copy()
    for i in range(1, grid_size-1):
        for j in range(1, grid_size-1):
            # Apply the diffusion equation (discrete Laplacian)
            new_concentration[i, j] = concentration[i, j] + diffusion_coefficient * (
                concentration[i+1, j] + concentration[i-1, j] +
                concentration[i, j+1] + concentration[i, j-1] - 4 * concentration[i, j]
            )
    return new_concentration

# Set up the plot
plt.ion()
fig, ax = plt.subplots()
cax = ax.matshow(concentration, cmap='hot')
fig.colorbar(cax)
ax.set_title("Aerosol Concentration")

# Simulation loop
for t in range(time_steps):
    concentration = update_concentration(concentration, diffusion_coefficient)
    if t < 500:
        concentration[center, center] = initial_concentration

    if t > 100:
        concentration[int(center/2), center] = initial_concentration
        concentration[int(center/2), int(center/2)] = initial_concentration*5

    # Update the plot
    if t % 10 == 0:
        cax.set_data(concentration)
        ax.set_title(f"Time Step: {t+1}")
        plt.pause(0.05)

plt.ioff()
plt.show()
plt.savefig("out/spatial.gif")