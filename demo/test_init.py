import sys
import jsbsim
from tools import Logger

DEMO_FLAG = 2


def demo1():
  fdm = jsbsim.FGFDMExec(None)  # Use JSBSim default aircraft data.
  fdm.set_debug_level(0)
  fdm.load_script('scripts/c1723.xml')
  fdm.set_output_filename(0, './output/c1723.csv')
  fdm.run_ic()

  for _ in range(100):
    fdm.run()


def demo2():
  sys.stdout = Logger('./output/output.log', sys.stdout)
  fdm = jsbsim.FGFDMExec('..', None)
  print("JSBSim version: ", fdm.get_version())
  fdm.load_model('f16')
  print("Model loaded: ", fdm.get_model_name())
  print("lat: ", fdm.get_property_value("position/lat-gc-rad"))
  print("long: ", fdm.get_property_value("position/long-gc-rad"))
  print("h: ", fdm.get_property_value("position/h-sl-meters"))
  print("================Change postion===============")
  fdm.set_property_value("position/lat-gc-rad", 1)  # 具体能设定的经纬度需要测试
  fdm.set_property_value("position/long-gc-rad", 1)
  fdm.set_property_value("position/h-sl-meters", 1000)
  print("lat: ", fdm.get_property_value("position/lat-gc-rad"))
  print("long: ", fdm.get_property_value("position/long-gc-rad"))
  print("h: ", fdm.get_property_value("position/h-sl-meters"))


def main():
  if DEMO_FLAG == 1:
    demo1()
  elif DEMO_FLAG == 2:
    demo2()
  else:
    print('Invalid DEMO_FLAG value. Exiting...')
    sys.exit(-1)  


if __name__ == '__main__':
  main()
