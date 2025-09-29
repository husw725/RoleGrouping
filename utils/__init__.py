from .file_utils import *
from .ui_utils import *
from .face_utils import *
from .video_utils import *



import os
import pickle

class CacheManager:
    """
    通用缓存管理器，用于Streamlit页面持久化数据。
    支持键值对缓存，自动持久化到本地文件。
    """

    def __init__(self, cache_file="cache.pkl"):
        self.cache_file = cache_file
        self.data = {}
        self.load()

    def load(self):
        """加载缓存文件，如果不存在则初始化空字典"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "rb") as f:
                    self.data = pickle.load(f)
            except Exception as e:
                print(f"加载缓存失败: {e}")
                self.data = {}
        else:
            self.data = {}

    def save(self):
        """保存缓存到文件"""
        try:
            with open(self.cache_file, "wb") as f:
                pickle.dump(self.data, f)
        except Exception as e:
            print(f"保存缓存失败: {e}")

    def get(self, key, default=None):
        """获取缓存值"""
        return self.data.get(key, default)

    def set(self, key, value):
        """设置缓存值"""
        self.data[key] = value
        self.save()  # 每次更新就保存