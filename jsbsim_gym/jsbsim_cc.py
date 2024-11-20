from typing import Union
import numpy as np
import gym
import pymap3d
from .jsbsim_gym import JSBSimEnv, PositionReward

class JSBSimEnvCC(JSBSimEnv):
    def __init__(self, root='.'):
        super().__init__(root)
    
    def reset(self, seed=None, init_pos: Union[list, np.array]=None, pos3d_flag=False):
        # Rerun initial conditions in JSBSim
        self.simulation.run_ic()
        self.simulation.set_property_value('propulsion/set-running', -1)
        
        # Generate a new goal
        distance = 0
        bearing = 0
        altitude = 0
        if init_pos is None:
            rng = np.random.default_rng(seed)
            distance = rng.random() * 9000 + 1000
            bearing = rng.random() * 2 * np.pi
            altitude = rng.random() * 3000
            self.goal[:2] = np.cos(bearing), np.sin(bearing)
            self.goal[:2] *= distance
            self.goal[2] = altitude

        if (isinstance(init_pos, (list, np.ndarray))):
            if (len(init_pos) < 3):
                raise ValueError("init_pos must have at least 3 elements")
            if (pos3d_flag is False):
                distance = init_pos[0]
                bearing = init_pos[1]
                altitude = init_pos[2]
                self.goal[:2] = np.cos(bearing), np.sin(bearing)
                self.goal[:2] *= distance
                self.goal[2] = altitude
            elif pos3d_flag:
                self._get_state()
                n, e, d = pymap3d.geodetic2ned(self.state[0], self.state[1], self.state[2], 
                                               init_pos[0], init_pos[1], init_pos[2])
                n = -n
                e = -e
                if (n > 5000 or e > 5000 or d > 5000):
                    raise ValueError("Distance between current position and goal is too large")
                self.goal[0] = n
                self.goal[1] = e
                self.goal[2] = init_pos[2]

        # Get state from JSBSim and save to self.state
        self._get_state()

        return np.hstack([self.state, self.goal])
    
# Create entry point to wrapped environment
def wrap_jsbsim(**kwargs):
    return PositionReward(JSBSimEnvCC(**kwargs), 1e-2)

# Register the wrapped environment
gym.register(
    id="JSBSimCC-v0",
    entry_point=wrap_jsbsim,
    max_episode_steps=1200
)