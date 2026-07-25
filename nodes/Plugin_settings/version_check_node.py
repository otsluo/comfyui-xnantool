#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
版本检查与更新节点
功能：检查插件更新，支持一键更新
"""

import logging

logger = logging.getLogger(__name__)

class VersionCheckNode:
    """版本检查节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "check_update": ("BOOLEAN", {"default": False, "label": "检查更新"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "BOOLEAN")
    RETURN_NAMES = ("版本信息", "更新日志", "有可用更新")
    FUNCTION = "check_version"
    CATEGORY = "❤️❤️❤️XnanTool/实用工具"
    OUTPUT_NODE = True

    def check_version(self, check_update):
        """检查版本更新"""
        try:
            from .auto_update import get_updater
            
            updater = get_updater()
            current_version = updater.get_current_version()
            
            if not check_update:
                return (
                    f"当前版本: {current_version}\n\n点击'检查更新'开关以检查最新版本",
                    "",
                    False
                )
            
            # 检查更新
            update_info = updater.check_for_updates()
            
            if update_info["error"]:
                return (
                    f"当前版本: {current_version}\n\n❌ {update_info['error']}",
                    "",
                    False
                )
            
            latest_version = update_info["latest_version"]
            has_update = update_info["has_update"]
            
            if has_update:
                update_body = update_info["update_info"].get("body", "暂无更新日志")
                published_at = update_info["update_info"].get("published_at", "")
                
                version_info = (
                    f"📦 当前版本: {current_version}\n"
                    f"🆕 最新版本: {latest_version}\n"
                    f"📅 更新日期: {published_at}\n\n"
                    f"✅ 发现新版本！\n"
                    f"请使用 '执行更新' 节点进行更新"
                )
                
                return (version_info, update_body, True)
            else:
                version_info = (
                    f"📦 当前版本: {current_version}\n"
                    f"🆕 最新版本: {latest_version}\n\n"
                    f"✅ 已是最新版本，无需更新"
                )
                
                return (version_info, "", False)
                
        except Exception as e:
            error_msg = f"❌ 检查更新失败: {str(e)}"
            logger.error(error_msg)
            return (error_msg, "", False)


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
