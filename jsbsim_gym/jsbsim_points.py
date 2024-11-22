from typing import Union
import numpy as np
import gym
import pymap3d
from .jsbsim_gym import JSBSimEnv, PositionReward, RADIUS

WAY_POINTS = np.array([
    [0, 0, 3000],
    [5000, 0, 3000],
    [4000, 4000, 3000],
    [6000, 6000, 3000],
    [8000, 8000, 3000],
])

class JSBSimEnvPoints(JSBSimEnv):
    """
    非训练环境，用于跟踪一系列航迹点
    """
    def __init__(self, root='.'):
        super().__init__(root)
        self.cur_idx = 0
        self.next_idx = self.cur_idx + 1
        self.way_points = WAY_POINTS
        self.goal_idx = len(self.way_points) - 1
    
    def reset(self, seed=None):
        # Rerun initial conditions in JSBSim
        self.simulation.run_ic()
        self.simulation.set_property_value("position/lat-gc-rad", self.way_points[self.cur_idx][0] / RADIUS)
        self.simulation.set_property_value("position/long-gc-rad", self.way_points[self.cur_idx][1] / RADIUS)
        self.simulation.set_property_value("position/h-sl-meters", self.way_points[self.cur_idx][2])
        self.simulation.set_property_value('propulsion/set-running', -1)
        
        # Generate a new goal
        self.set_goal()

        # Get state from JSBSim and save to self.state
        self._get_state()

        return np.hstack([self.state, self.goal])
    
    def set_goal(self):
        self._get_state()
        cur_loc = self.state[:3]
        next_point = self.way_points[self.next_idx]
        n = next_point[0]
        e = next_point[1]
        d = next_point[2]
        if (n > 50000 or e > 50000 or d > 5000):
            raise ValueError("Distance between current position and goal is too large")
        self.goal[0] = n
        self.goal[1] = e
        self.goal[2] = next_point[2]

    def step(self, action):
        roll_cmd, pitch_cmd, yaw_cmd, throttle = action

        # Pass control inputs to JSBSim
        self.simulation.set_property_value("fcs/aileron-cmd-norm", roll_cmd)
        self.simulation.set_property_value("fcs/elevator-cmd-norm", pitch_cmd)
        self.simulation.set_property_value("fcs/rudder-cmd-norm", yaw_cmd)
        self.simulation.set_property_value("fcs/throttle-cmd-norm", throttle)

        # We take multiple steps of the simulation per step of the environment
        for _ in range(self.down_sample):
            # Freeze fuel consumption
            self.simulation.set_property_value("propulsion/tank/contents-lbs", 1000)
            self.simulation.set_property_value("propulsion/tank[1]/contents-lbs", 1000)

            # Set gear up
            self.simulation.set_property_value("gear/gear-cmd-norm", 0.0)
            self.simulation.set_property_value("gear/gear-pos-norm", 0.0)

            self.simulation.run()

        # Get the JSBSim state and save to self.state
        self._get_state()

        reward = 0
        done = False

        # Check for collision with ground
        if self.state[2] < 10:
            reward = -10
            done = True

        # Check if reached goal
        if np.sqrt(np.sum((self.state[:2] - self.goal[:2])**2)) < self.dg and abs(self.state[2] - self.goal[2]) < self.dg:
            reward = 10
            # done = True
            self.cur_idx += 1
            self.next_idx += 1
            if self.cur_idx < self.goal_idx:
                self.set_goal()

        if self.cur_idx == self.goal_idx:
            done = True
        
        return np.hstack([self.state, self.goal]), reward, done, {}
    
# Create entry point to wrapped environment
def wrap_jsbsim(**kwargs):
    return PositionReward(JSBSimEnvPoints(**kwargs), 1e-2)

# Register the wrapped environment
gym.register(
    id="JSBSimEnvPoints-v0",
    entry_point=wrap_jsbsim,
    max_episode_steps=1200
)