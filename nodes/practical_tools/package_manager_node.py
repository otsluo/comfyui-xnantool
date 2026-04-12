import subprocess
import sys
import json
import logging
from pip._internal.operations import freeze


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PackageManagerNode:
    """依赖包管理节点 - 查看、安装、卸载、更新Python包"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "action": (["查看已安装", "查看包详情", "安装包", "卸载包", "更新包"], {
                    "label": "操作类型",
                    "description": "选择要执行的操作"
                }),
                "package_name": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "label": "包名称",
                    "description": "要操作的包名称（查看已安装时可留空）"
                }),
                "mirror_url": ("STRING", {
                    "default": "https://mirrors.aliyun.com/pypi/simple",
                    "multiline": False,
                    "label": "镜像源URL",
                    "description": "留空使用默认源，填写则使用指定镜像源"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("结果",)
    FUNCTION = "manage_package"
    CATEGORY = "XnanTool/实用工具"
    DESCRIPTION = "管理Python依赖包：查看已安装、查看包详情、安装、卸载、更新（支持换源安装）"
    
    def manage_package(self, action, package_name, mirror_url="https://mirrors.aliyun.com/pypi/simple"):
        logger.info(f"执行操作: {action}, 包名称: {package_name}")
        try:
            if action == "查看已安装":
                return self.list_installed_packages()
            elif action == "查看包详情":
                return self.show_package_info(package_name)
            elif action == "安装包":
                return self.install_package(package_name, mirror_url)
            elif action == "卸载包":
                return self.uninstall_package(package_name)
            elif action == "更新包":
                return self.update_package(package_name, mirror_url)
        except Exception as e:
            error_msg = f"操作失败: {str(e)}"
            logger.error(error_msg)
            return (error_msg,)
    
    def list_installed_packages(self):
        """查看已安装的包"""
        try:
            packages_iter = freeze.freeze()
            packages = list(packages_iter) if packages_iter else []
            package_count = len(packages) if packages else 0
            logger.info(f"成功获取已安装包列表，共 {package_count} 个包")
            packages_str = "\n".join(packages) if packages else "无已安装包"
            return (f"成功获取已安装包列表，共 {package_count} 个包\n\n{packages_str}",)
        except Exception as e:
            error_msg = f"获取失败: {str(e)}"
            logger.error(error_msg)
            return (error_msg,)
    
    def show_package_info(self, package_name):
        """查看包的详细信息（类似pip show）"""
        if not package_name:
            error_msg = "错误：请输入包名称"
            logger.error(error_msg)
            return (error_msg,)
        
        logger.info(f"开始查看包详情: {package_name}")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                output = result.stdout if result.stdout else "包信息为空"
                logger.info(f"成功获取 {package_name} 的详细信息")
                return (output,)
            else:
                error_msg = f"获取失败 {package_name}\n{result.stderr if result.stderr else '未知错误'}"
                logger.error(error_msg)
                return (error_msg,)
        except subprocess.TimeoutExpired:
            error_msg = "获取超时"
            logger.error(error_msg)
            return (error_msg,)
        except Exception as e:
            error_msg = f"获取失败: {str(e)}"
            logger.error(error_msg)
            return (error_msg,)
    
    def install_package(self, package_name, mirror_url="https://mirrors.aliyun.com/pypi/simple"):
        """安装包"""
        if not package_name:
            error_msg = "错误：请输入包名称"
            logger.error(error_msg)
            return (error_msg,)
        
        logger.info(f"开始安装包: {package_name}")
        
        try:
            cmd = [sys.executable, "-m", "pip", "install", package_name]
            
            if mirror_url:
                cmd.extend(["-i", mirror_url])
                logger.info(f"使用镜像源: {mirror_url}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                output = f"成功安装 {package_name}\n{result.stdout}"
                logger.info(f"成功安装 {package_name}")
                return (output,)
            else:
                error_msg = f"安装失败 {package_name}\n{result.stderr}"
                logger.error(error_msg)
                return (error_msg,)
        except subprocess.TimeoutExpired:
            error_msg = "安装超时，请检查网络连接"
            logger.error(error_msg)
            return (error_msg,)
        except Exception as e:
            error_msg = f"安装失败: {str(e)}"
            logger.error(error_msg)
            return (error_msg,)
    
    def uninstall_package(self, package_name):
        """卸载包"""
        if not package_name:
            error_msg = "错误：请输入包名称"
            logger.error(error_msg)
            return (error_msg,)
        
        logger.info(f"开始卸载包: {package_name}")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "-y", package_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                output = f"成功卸载 {package_name}\n{result.stdout}"
                logger.info(f"成功卸载 {package_name}")
                return (output,)
            else:
                error_msg = f"卸载失败 {package_name}\n{result.stderr}"
                logger.error(error_msg)
                return (error_msg,)
        except subprocess.TimeoutExpired:
            error_msg = "卸载超时"
            logger.error(error_msg)
            return (error_msg,)
        except Exception as e:
            error_msg = f"卸载失败: {str(e)}"
            logger.error(error_msg)
            return (error_msg,)
    
    def update_package(self, package_name, mirror_url="https://mirrors.aliyun.com/pypi/simple"):
        """更新包"""
        if not package_name:
            error_msg = "错误：请输入包名称"
            logger.error(error_msg)
            return (error_msg,)
        
        logger.info(f"开始更新包: {package_name}")
        
        try:
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
            
            if mirror_url:
                cmd.extend(["-i", mirror_url])
                logger.info(f"使用镜像源: {mirror_url}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                output = f"成功更新 {package_name}\n{result.stdout}"
                logger.info(f"成功更新 {package_name}")
                return (output,)
            else:
                error_msg = f"更新失败 {package_name}\n{result.stderr}"
                logger.error(error_msg)
                return (error_msg,)
        except subprocess.TimeoutExpired:
            error_msg = "更新超时，请检查网络连接"
            logger.error(error_msg)
            return (error_msg,)
        except Exception as e:
            error_msg = f"更新失败: {str(e)}"
            logger.error(error_msg)
            return (error_msg,)
    
    @classmethod
    def IS_CHANGED(cls, action, package_name, mirror_url="https://mirrors.aliyun.com/pypi/simple", **kwargs):
        return float("NaN")
    
    @classmethod
    def VALIDATE_INPUTS(cls, action, package_name, mirror_url="https://mirrors.aliyun.com/pypi/simple", **kwargs):
        if action in ["查看包详情", "安装包", "卸载包", "更新包"] and not package_name.strip():
            return "请输入包名称"
        return True


NODE_CLASS_MAPPINGS = {
    "PackageManagerNode": PackageManagerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PackageManagerNode": "依赖包管理",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
