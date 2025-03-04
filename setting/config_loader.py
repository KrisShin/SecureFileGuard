from pathlib import Path
from typing import Any, Dict

import yaml

from setting.global_variant import CONFIG_PATH


class ConfigLoadError(Exception):
    """自定义配置加载异常"""

    pass


class ConfigNode(object):
    """配置节点包装类，支持点号访问"""

    def __init__(self, config_dict: Dict[str, Any]):
        for key, value in config_dict.items():
            if isinstance(value, dict):
                setattr(self, key, ConfigNode(value))
            else:
                setattr(self, key, value)

    def __repr__(self):
        return str(self.__dict__)


class ConfigLoader(object):
    @staticmethod
    def load_config(file_path: str) -> ConfigNode:
        """
        加载并验证配置文件
        :param file_path: 配置文件路径
        :return: 配置节点对象
        """
        try:
            config_path = Path(file_path)
            if not config_path.exists():
                raise FileNotFoundError(f"配置文件 {file_path} 不存在")

            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            # 转换为ConfigNode对象
            config = ConfigNode(config_data)

            # 执行基础验证
            ConfigLoader._validate_config(config)
            return config

        except yaml.YAMLError as e:
            raise ConfigLoadError(f"YAML解析错误: {str(e)}") from e
        except Exception as e:
            raise ConfigLoadError(f"配置加载失败: {str(e)}") from e

    @staticmethod
    def _validate_config(config: ConfigNode):
        """配置基础验证"""
        # 验证加密算法配置
        if config.security.default_algorithm not in config.security.algorithms:
            raise ValueError(f"默认算法 {config.security.default_algorithm} " f"不在支持的算法列表 {config.security.algorithms} 中")

        # 验证路径配置
        required_paths = ['db_file', 'upload', 'download']
        for path_key in required_paths:
            if not hasattr(config.path, path_key):
                raise ValueError(f"缺少必要的路径配置项: {path_key}")


config = ConfigLoader.load_config(CONFIG_PATH)  # 全局配置对象

if __name__ == "__main__":
    # 使用示例
    try:

        print(f"应用名称: {config.app.name}")
        print(f"支持算法: {config.security.algorithms}")
        print(f"数据库路径: {config.path.db_file}")

    except ConfigLoadError as e:
        print(f"配置加载错误: {e}")
    except Exception as e:
        print(f"运行时错误: {e}")
