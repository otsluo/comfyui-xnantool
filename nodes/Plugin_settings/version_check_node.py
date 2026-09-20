#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
版本检查与更新节点
功能：查看更新日志，支持一键更新
"""

import logging

logger = logging.getLogger(__name__)

class VersionCheckNode:
    """版本检查节点 - 查看更新日志"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "check_update": ("BOOLEAN", {"default": False, "label": "查看更新日志"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("更新日志",)
    FUNCTION = "check_version"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"
    OUTPUT_NODE = True

    def check_version(self, check_update):
        """查看更新日志"""
        try:
            from .auto_update import get_updater
            
            updater = get_updater()
            current_version = updater.get_current_version()
            
            if not check_update:
                return (
                    f"当前版本: {current_version}\n\n点击'查看更新日志'开关以查看最新更新",
                )
            
            # 获取最新commit信息作为更新日志
            update_info = updater.get_latest_update_log()
            
            if update_info["error"]:
                return (
                    f"当前版本: {current_version}\n\n❌ {update_info['error']}",
                )
            
            # 显示更新日志
            commit_message = update_info.get("message", "暂无更新信息")
            commit_sha = update_info.get("sha", "")
            
            log_info = (
                f"📦 当前版本号: {current_version}\n"
                f"🆕 最新提交版本: commit-{commit_sha}\n\n"
                f"📝 更新内容:\n{commit_message}"
            )
            
            return (log_info,)
                
        except Exception as e:
            error_msg = f"❌ 获取更新日志失败: {str(e)}"
            logger.error(error_msg)
            return (error_msg,)


class VersionUpdateNode:
    """版本更新节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "confirm_update": ("BOOLEAN", {"default": False, "label": "确认更新"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("更新结果",)
    FUNCTION = "update_plugin"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"
    OUTPUT_NODE = True

    def update_plugin(self, confirm_update):
        """执行插件更新"""
        try:
            from .auto_update import get_updater
            
            updater = get_updater()
            
            if not confirm_update:
                return ("⚠️ 请打开'确认更新'开关以执行更新",)
            
            # 执行更新
            result = updater.update_plugin()
            
            if result["success"]:
                return (result["message"],)
            else:
                error_msg = f"❌ 更新失败\n\n{result['error']}"
                return (error_msg,)
                
        except Exception as e:
            error_msg = f"❌ 更新过程中发生错误: {str(e)}"
            logger.error(error_msg)
            return (error_msg,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "VersionCheckNode": VersionCheckNode,
    "VersionUpdateNode": VersionUpdateNode,
}

# 定义显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "VersionCheckNode": "版本检查",
    "VersionUpdateNode": "执行更新",
}

# 导出映射（必须）
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
