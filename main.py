import os
import threading
import importlib
import time
import traceback
from pathlib import Path

from PIL import Image

import enviroment
from system import configurator

'''
Theme and App
AppController
Docker
更好的错误处理机制

book update函数支持全局刷新
'''


# 原来的主线程

def main_thread():
    time.sleep(0.5)
    print("Running In Develop Mode")

    load_lock = threading.Barrier(2)

    def opening():
        env.Screen.display(Image.open("resources/images/simplebytes.jpg"))
        opening_image_paths = ["resources/images/raspberry.jpg", ]
        opening_images = []
        for path in opening_image_paths:
            opening_images.append(Image.open(Path(path)))
        for i in opening_images:
            env.Screen.display_auto(i)
            env.Screen.wait_busy()
        if load_lock.n_waiting == 0:
            env.Screen.display_auto(Image.open("resources/images/loading.jpg"))
        load_lock.wait()

    env.Pool.add(opening)
    """
    touch_recoder_dev = enviroment.touchscreen.TouchRecoder()
    touch_recoder_old = enviroment.touchscreen.TouchRecoder()
    """

    # plugins
    for plugin_dir in os.listdir("plugins"):
        if not os.path.isdir(f"plugins/{plugin_dir}"):
            continue
        try:
            env.plugins[plugin_dir] = importlib.import_module(f"plugins.{plugin_dir}.main").Plugin(env)
            env.Logger.info(f"插件加载：{plugin_dir}")
        except:
            print(traceback.format_exc())
            env.Logger.error(traceback.format_exc())

    # themes
    for theme_dir in os.listdir("themes"):
        if not os.path.isdir(f"themes/{theme_dir}"):
            continue
        try:
            env.themes[theme_dir] = importlib.import_module(f"themes.{theme_dir}.main").Theme(env)
            env.Logger.info(f"主题加载: {theme_dir}")
        except:
            print(traceback.format_exc())
            env.Logger.error(traceback.format_exc())

    # apps
    for app_dir in os.listdir("applications"):
        if not os.path.isdir(f"applications/{app_dir}"):
            continue
        try:
            env.apps[app_dir] = importlib.import_module(f"applications.{app_dir}.main").Application(env)
            env.Logger.info(f"应用加载: {app_dir}")
        except:
            print(traceback.format_exc())
            env.Logger.error(traceback.format_exc())

    env.apps["应用抽屉"].update_app_list()

    load_lock.wait()

    env.start()


"""
    while 1:  # 据说 while 1 的效率比 while True 高
        env.Touch.icnt_scan(touch_recoder_dev, touch_recoder_old)
        env.TouchHandler.handle(touch_recoder_dev, touch_recoder_old)
"""


if __name__ == "__main__":
    simulator = enviroment.Simulator()
    env = enviroment.Env(simulator)
    env.Pool.add(main_thread)
    simulator.start(env)
