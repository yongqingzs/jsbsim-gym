import gym
import jsbsim_gym.jsbsim_points # This line makes sure the environment is registered
from jsbsim_gym.jsbsim_points import JSBSimEnvPoints
import imageio as iio
from os import path
from jsbsim_gym.features import JSBSimFeatureExtractor
from stable_baselines3 import SAC

policy_kwargs = dict(
    features_extractor_class=JSBSimFeatureExtractor
)

root_path = path.abspath(path.dirname(__file__)) + "/.."
# env = gym.make("JSBSimCC-v0", root=root_path)
env = JSBSimEnvPoints(root=root_path)

model = SAC.load(root_path + "/models/jsbsim_sac_pre", env)  #jsbsim_sac_pre为预训练模型

mp4_writer = iio.get_writer(root_path + "/output/video.mp4", format="ffmpeg", fps=30)
gif_writer = iio.get_writer(root_path + "/output/video.gif", format="gif", fps=5)

obs = env.reset()
done = False
step = 0
while not done:
    render_data = env.render(mode='rgb_array')
    mp4_writer.append_data(render_data)
    if step % 6 == 0:
        gif_writer.append_data(render_data[::2,::2,:])

    action, _ = model.predict(obs, deterministic=True)
    obs, _, done, _ = env.step(action)
    step += 1
mp4_writer.close()
gif_writer.close()
env.close()