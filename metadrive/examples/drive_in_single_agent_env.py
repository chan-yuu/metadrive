#!/usr/bin/env python
"""
Please feel free to run this script to enjoy a journey by keyboard!
Remember to press H to see help message!

Note: This script require rendering, please following the installation instruction to setup a proper
environment that allows popping up an window.
"""
import argparse
import logging
import random

import numpy as np

from metadrive import MetaDriveEnv
from metadrive.component.sensors.rgb_camera import RGBCamera
from metadrive.component.sensors.mini_map import MiniMap
from metadrive.component.sensors.dashboard import DashBoard
from metadrive.constants import HELP_MESSAGE

if __name__ == "__main__":
    config = dict(
        # controller="steering_wheel",
        use_render=True,
        manual_control=True,
        traffic_density=0.1,
        num_scenarios=10000,
        random_agent_model=False,
        random_lane_width=True,
        random_lane_num=True,
        on_continuous_line_done=False,
        out_of_route_done=True,
        vehicle_config=dict(show_lidar=False, show_navi_mark=False, show_line_to_navi_mark=False),
        # debug=True,
        # debug_static_world=True,
        map=4,  # seven block
        start_seed=10,
        # 配置传感器 - 小地图、仪表盘、RGB相机
        # MiniMap参数: (width, height, z_pos) - 俯视相机的宽度、高度和高度位置
        sensors=dict(
            mini_map=(MiniMap, 400, 240, 100),  # 俯视地图相机
            rgb_camera=(RGBCamera, 400, 240),      # 前视RGB相机
        ),
        # 配置界面面板 - 显示三个面板(最多3个)
        # 顺序:从右到左显示为 mini_map, dashboard, rgb_camera
        interface_panel=["mini_map", "rgb_camera", "dashboard"],
        # 启用图像观测
        image_observation=True,
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--observation", type=str, default="lidar", choices=["lidar", "rgb_camera"])
    args = parser.parse_args()
    
    # 注意:在0.4.3版本中,默认已经配置了传感器和界面面板
    # 如果需要调整,可以修改上面config中的sensors和interface_panel参数
    env = MetaDriveEnv(config)
    try:
        o, _ = env.reset(seed=21)
        print(HELP_MESSAGE)
        env.agent.expert_takeover = True
        # 因为启用了 image_observation=True, 观测值总是字典类型
        assert isinstance(o, dict)
        print("The observation is a dict with numpy arrays as values: ", {k: v.shape for k, v in o.items()})
        for i in range(1, 1000000000):
            o, r, tm, tc, info = env.step([0, 0])
            env.render(
                text={
                    "Auto-Drive (Switch mode: T)": "on" if env.current_track_agent.expert_takeover else "off",
                    "Current Observation": args.observation,
                    "Keyboard Control": "W,A,S,D",
                }
            )
            print("Navigation information: ", info["navigation_command"])
            if (tm or tc) and info["arrive_dest"]:
                env.reset(env.current_seed + 1)
                env.current_track_agent.expert_takeover = True
    finally:
        env.close()
