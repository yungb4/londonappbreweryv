import os
import json

from pathlib import Path

default_config_path = "configs/config.json"
try:
    os.mkdir("configs")
except OSError:
    pass


class TargetExists(Exception):
    pass


class Configurator:  # 没有对多线程进行适配，需要自行加锁
    def __init__(self, file_path=default_config_path, example=None, auto_save=True):
        if example is None:
            example = {}

        def fix_file():
            os.rename(default_config_path, default_config_path + ".bk")
            file = open(Path(self.file_path), "w")
            json.dump(example, file, indent=4)
            file.close()
            self.config = example
            print("配置文件已失效，已备份到 '%s.bk' 并已创建新的文件" % self.file_path)

        self.path = file_path
        self.__current_path = "/"
        self.file_path = file_path
        self.auto_save = auto_save
        if os.path.exists(file_path):
            try:
                file = open(Path(file_path), "r")
                self.config = json.load(file)
                file.close()
                try:
                    for key, value in example.items():
                        if type(self.config[key]) != type(value):
                            fix_file()
                except KeyError:
                    fix_file()
            except json.decoder.JSONDecodeError:
                os.rename(default_config_path, default_config_path + ".bk")
                self.config = example
                json.dump(example, open(Path(file_path), "w"))
                print("配置文件不是json文件，已备份到 '%s.bk' 并已创建新的空白文件" % file_path)
        else:
            file = open(Path(file_path), "w")
            file.write("{}")
            file.close()
            self.config = example
        self.current_config = self.config

    @property
    def current_path(self):
        return self.__current_path

    @current_path.setter
    def current_path(self, value):
        self.change_path(value)

    def save(self):
        file = open(Path(self.path), "w")
        json.dump(self.config, file, indent=4)
        file.close()

    def change_path(self, path):
        if path[0] != "/":
            raise ValueError("The path of target must start with '/'!")
        path = path[1:].split("/")
        # 检查合法性
        finder = self.config
        for i in range(len(path)):
            try:
                finder = finder[path[i]]
                if type(finder) != dict:
                    raise ValueError("Target path does not a dict!")
            except KeyError:
                raise ValueError("The target does not exist!")
        # 设置目录
        self.current_config = finder

    def read_or_create(self, path: str, default_value):
        if path[0] == "/":
            finder = self.config
            path = path[1:]
        else:
            finder = self.current_config
        path = path.split("/")
        for i in range(len(path) - 1):
            try:
                finder = finder[path[i]]
            except KeyError:
                finder[path[i]] = {}
                finder = finder[path[1]]
        try:
            return finder[path[-1]]
        except KeyError:
            finder[path[-1]] = default_value
            if self.auto_save:
                self.save()
            return default_value

    def read(self, path, raise_error=True):
        if path[0] == "/":
            finder = self.config
            path = path[1:]
        else:
            finder = self.current_config
        path = path.split("/")
        for i in range(len(path) - 1):
            try:
                finder = finder[path[i]]
            except KeyError as e:
                if raise_error:
                    raise e
                return None
        try:
            return finder[path[-1]]
        except KeyError as e:
            if raise_error:
                raise e
            return None

    def set(self, path, value) -> bool:
        if path[0] == "/":
            finder = self.config
            path = path[1:]
        else:
            finder = self.current_config
        path = path.split("/")
        for i in range(len(path) - 1):
            try:
                finder = finder[path[i]]
            except KeyError:
                finder[path[i]] = {}
                finder = finder[path[i]]
        finder[path[-1]] = value
        if self.auto_save:
            self.save()
        return True

    def delete(self, path, raise_error=False) -> bool:
        if path[0] == "/":
            finder = self.config
            path = path[1:]
        else:
            finder = self.current_config
        path = path.split("/")
        for i in range(len(path) - 1):
            try:
                finder = finder[path[i]]
            except KeyError as e:
                if raise_error:
                    raise e
                return False
        try:
            del finder[path[-1]]
            if self.auto_save:
                self.save()
            return True
        except KeyError as e:
            if raise_error:
                raise e
            return False
