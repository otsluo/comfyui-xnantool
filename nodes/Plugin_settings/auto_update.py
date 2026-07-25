#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
插件自动更新模块
功能：检查GitHub最新版本，支持自动下载更新
"""

import os
import json
import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

class AutoUpdater:
    """自动更新器"""
    
    def __init__(self, plugin_dir, github_repo="otsluo/comfyui-xnantool"):
        """
        初始化自动更新器
        
        Args:
            plugin_dir: 插件目录路径
            github_repo: GitHub仓库地址（格式：用户名/仓库名）
        """
        self.plugin_dir = Path(plugin_dir)
        self.github_repo = github_repo
        self.version_file = self.plugin_dir / "__version_info__.json"
        self.update_log_file = self.plugin_dir / "__update_log__.txt"
    
    def get_current_version(self):
        """获取当前版本号"""
        try:
            # 尝试从插件根目录的__init__.py导入版本号
            import sys
            import os
            
            # 获取插件根目录路径
            plugin_root = self.plugin_dir
            
            # 方法1：尝试直接导入
            if "comfyui-xnantool" in sys.modules:
                module = sys.modules["comfyui-xnantool"]
                version = getattr(module, "__version__", None)
                if version:
                    return version
            
            # 方法2：读取__init__.py文件提取版本号
            init_file = plugin_root / "__init__.py"
            if init_file.exists():
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 查找 __version__ = "x.x.x"
                    import re
                    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)
            
            return "unknown"
        except Exception as e:
            logger.warning(f"获取版本号失败: {str(e)}")
            return "unknown"
    
    def get_latest_version_from_github(self):
        """
        从GitHub获取最新commit信息
        
        Returns:
            dict: 包含版本信息和更新日志的字典，失败返回None
        """
        try:
            import urllib.request
            import ssl
            
            # 创建SSL上下文（忽略证书验证，仅用于获取公开信息）
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # 获取最新commit
            return self._get_latest_commit(context)
                
        except Exception as e:
            logger.warning(f"获取GitHub版本信息失败: {str(e)}")
            return None
    
    def _get_latest_commit(self, ssl_context):
        """
        获取最新commit信息
        
        Args:
            ssl_context: SSL上下文
            
        Returns:
            dict: commit信息
        """
        try:
            import urllib.request
            
            api_url = f"https://api.github.com/repos/{self.github_repo}/commits?per_page=1"
            
            req = urllib.request.Request(api_url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'ComfyUI-XnanTool-Updater')
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if data and len(data) > 0:
                    commit = data[0]
                    commit_sha = commit.get("sha", "")[:7]  # 取前7位
                    commit_date = commit.get("commit", {}).get("author", {}).get("date", "")
                    commit_message = commit.get("commit", {}).get("message", "")
                    
                    return {
                        "version": f"commit-{commit_sha}",
                        "name": f"最新提交: {commit_sha}",
                        "published_at": commit_date,
                        "body": commit_message,
                        "zip_url": f"https://github.com/{self.github_repo}/archive/main.zip",
                        "source": "commit",
                        "sha": commit.get("sha", "")
                    }
        except Exception as e:
            logger.warning(f"获取commit信息失败: {str(e)}")
            return None
    
    def check_for_updates(self):
        """
        检查是否有可用更新
        
        Returns:
            dict: {
                "has_update": bool, 是否有更新
                "current_version": str, 当前版本
                "latest_version": str, 最新版本
                "update_info": dict, 更新信息
                "error": str, 错误信息（如果有）
            }
        """
        result = {
            "has_update": False,
            "current_version": self.get_current_version(),
            "latest_version": "",
            "update_info": None,
            "error": None
        }
        
        try:
            latest_info = self.get_latest_version_from_github()
            
            if latest_info is None:
                result["error"] = "无法获取最新版本信息"
                return result
            
            result["latest_version"] = latest_info["version"]
            result["update_info"] = latest_info
            
            # 比较版本号
            if self._compare_versions(result["current_version"], latest_info["version"]) < 0:
                result["has_update"] = True
            
        except Exception as e:
            result["error"] = f"检查更新失败: {str(e)}"
            logger.error(result["error"])
        
        return result
    
    def update_plugin(self):
        """
        更新插件（使用git pull）
        
        Returns:
            dict: {
                "success": bool, 是否成功
                "message": str, 更新信息
                "error": str, 错误信息（如果有）
            }
        """
        result = {
            "success": False,
            "message": "",
            "error": None
        }
        
        try:
            # 检查是否是git仓库
            git_dir = self.plugin_dir / ".git"
            if not git_dir.exists():
                result["error"] = "插件不是通过git克隆安装的，无法自动更新\n请手动下载最新版本或使用git clone安装"
                return result
            
            # 执行git pull
            logger.info("开始更新插件...")
            
            # 先获取当前分支
            branch = self._get_current_branch()
            if branch is None:
                result["error"] = "无法获取当前git分支"
                return result
            
            # 执行git fetch
            fetch_result = self._run_git_command(["git", "fetch", "origin"])
            if not fetch_result["success"]:
                result["error"] = f"获取远程更新失败: {fetch_result['error']}"
                return result
            
            # 执行git pull
            pull_result = self._run_git_command(["git", "pull", "origin", branch])
            
            if pull_result["success"]:
                result["success"] = True
                result["message"] = f"插件更新成功！\n\n请重启ComfyUI以应用更新\n\n更新内容：\n{pull_result['output']}"
                logger.info("插件更新成功")
            else:
                # 如果有冲突，尝试stash
                if "conflict" in pull_result.get("error", "").lower():
                    logger.info("检测到冲突，尝试stash后重新pull...")
                    
                    stash_result = self._run_git_command(["git", "stash"])
                    if stash_result["success"]:
                        pull_result2 = self._run_git_command(["git", "pull", "origin", branch])
                        if pull_result2["success"]:
                            result["success"] = True
                            result["message"] = f"插件更新成功！（已自动处理冲突）\n\n请重启ComfyUI以应用更新"
                            logger.info("插件更新成功（已处理冲突）")
                        else:
                            result["error"] = f"更新失败: {pull_result2['error']}"
                    else:
                        result["error"] = f"更新失败且无法stash: {pull_result['error']}"
                else:
                    result["error"] = f"更新失败: {pull_result['error']}"
            
        except Exception as e:
            result["error"] = f"更新过程中发生错误: {str(e)}"
            logger.error(result["error"])
        
        return result
    
    def _compare_versions(self, version1, version2):
        """
        比较两个版本号
        
        Args:
            version1: 版本号1
            version2: 版本号2
            
        Returns:
            int: -1表示version1 < version2, 0表示相等, 1表示version1 > version2
        """
        try:
            # 处理commit版本
            if version2.startswith("commit-"):
                # 如果当前版本不是commit版本，认为不需要更新
                if not version1.startswith("commit-"):
                    return 0
                # 都是commit版本，认为需要更新（无法比较）
                return -1
            
            # 移除版本号前缀
            v1 = version1.lstrip("v")
            v2 = version2.lstrip("v")
            
            # 分割版本号
            parts1 = [int(x) for x in v1.split(".")]
            parts2 = [int(x) for x in v2.split(".")]
            
            # 补齐长度
            max_len = max(len(parts1), len(parts2))
            parts1.extend([0] * (max_len - len(parts1)))
            parts2.extend([0] * (max_len - len(parts2)))
            
            # 逐段比较
            for p1, p2 in zip(parts1, parts2):
                if p1 < p2:
                    return -1
                elif p1 > p2:
                    return 1
            
            return 0
        except:
            # 如果解析失败，使用字符串比较
            if version1 < version2:
                return -1
            elif version1 > version2:
                return 1
            return 0
    
    def _get_current_branch(self):
        """获取当前git分支"""
        result = self._run_git_command(["git", "branch", "--show-current"])
        if result["success"] and result["output"]:
            return result["output"].strip()
        return None
    
    def _run_git_command(self, command):
        """
        执行git命令
        
        Args:
            command: git命令列表
            
        Returns:
            dict: {
                "success": bool, 是否成功
                "output": str, 输出内容
                "error": str, 错误信息
            }
        """
        try:
            result = subprocess.run(
                command,
                cwd=str(self.plugin_dir),
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "output": result.stdout,
                    "error": result.stderr
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "命令执行超时"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }


# 全局更新器实例
_updater = None

def get_updater():
    """获取全局更新器实例"""
    global _updater
    if _updater is None:
        plugin_dir = Path(__file__).parent.parent
        _updater = AutoUpdater(
            plugin_dir=plugin_dir,
            github_repo="otsluo/comfyui-xnantool"
        )
    return _updater
