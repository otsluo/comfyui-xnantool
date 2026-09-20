#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
技能下载节点
功能：从 GitHub 下载技能目录到 skills 目录
"""

import os
import json
import urllib.request
import ssl
import zipfile
import io
import shutil

# 技能文件目录
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")


class SkillDownloaderNode:
    """技能下载节点 - 从 GitHub 下载技能目录"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "github_url": ("STRING", {
                    "default": "https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing",
                    "label": "GitHub URL",
                    "description": "GitHub 技能目录的 URL"
                }),
                "download": ("BOOLEAN", {
                    "default": False,
                    "label": "确认下载"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("下载结果",)
    FUNCTION = "download_skill"
    CATEGORY = "❤️❤️❤️XnanTool/预设"

    def download_skill(self, github_url, download):
        """从 GitHub 下载技能目录或整个仓库"""
        if not download:
            return ("请点击'确认下载'开关开始下载",)

        if not github_url or not github_url.strip():
            return ("错误：请输入 GitHub URL",)

        try:
            # 创建 SSL 上下文
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # 解析 GitHub URL
            url_info = self._parse_github_url(github_url.strip(), context)
            if not url_info:
                return ("错误：无法解析 GitHub URL，请检查格式\n\n支持格式：\n1. https://github.com/用户名/仓库名（整个仓库）\n2. https://github.com/用户名/仓库名/tree/分支/路径（指定目录）",)

            owner, repo, branch, path = url_info

            # 确定技能名称和目标目录
            if path:
                skill_name = os.path.basename(path)
            else:
                skill_name = repo

            # 获取目录内容列表
            contents = self._get_directory_contents(owner, repo, branch, path, context)
            if not contents:
                return ("错误：无法获取目录内容或目录为空",)

            # 创建目标目录
            target_dir = os.path.join(SKILLS_DIR, skill_name)
            if os.path.exists(target_dir):
                # 如果目录已存在，先备份
                backup_dir = target_dir + "_backup"
                if os.path.exists(backup_dir):
                    shutil.rmtree(backup_dir)
                os.rename(target_dir, backup_dir)

            os.makedirs(target_dir, exist_ok=True)

            # 下载所有文件
            downloaded_files = []
            self._download_directory(owner, repo, branch, path, target_dir, contents, context, downloaded_files, "")

            # 清理备份
            backup_dir = target_dir + "_backup"
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)

            result = f"✅ 技能下载成功！\n\n"
            result += f"技能名称: {skill_name}\n"
            result += f"保存路径: {target_dir}\n"
            result += f"下载文件数: {len(downloaded_files)}\n\n"
            result += "下载的文件:\n"
            for f in downloaded_files:
                result += f"  - {f}\n"

            return (result,)

        except Exception as e:
            return (f"❌ 下载失败: {str(e)}",)

    def _parse_github_url(self, url, context):
        """
        解析 GitHub URL

        支持格式:
        - https://github.com/owner/repo （整个仓库，自动检测默认分支）
        - https://github.com/owner/repo/tree/branch/path/to/dir
        - https://github.com/owner/repo/blob/branch/path/to/dir

        Returns:
            tuple: (owner, repo, branch, path) 或 None
        """
        try:
            # 移除末尾斜杠
            url = url.rstrip('/')

            # 解析 URL
            if 'github.com' not in url:
                return None

            parts = url.split('github.com/')[-1].split('/')
            if len(parts) < 2:
                return None

            owner = parts[0]
            repo = parts[1]

            # 格式1：整个仓库 URL，自动获取默认分支
            if len(parts) == 2:
                branch = self._get_default_branch(owner, repo, context)
                if not branch:
                    branch = "main"  # 回退到 main
                return (owner, repo, branch, "")

            # 格式2：tree 或 blob 路径
            if len(parts) >= 5 and parts[2] in ('tree', 'blob'):
                branch = parts[3]
                path = '/'.join(parts[4:])
                return (owner, repo, branch, path)

            return None
        except Exception:
            return None

    def _get_default_branch(self, owner, repo, context):
        """获取仓库的默认分支"""
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            req = urllib.request.Request(api_url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'ComfyUI-XnanTool-SkillDownloader')

            with urllib.request.urlopen(req, context=context, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get("default_branch", "main")
        except Exception as e:
            print(f"[技能下载] 获取默认分支失败: {e}")
            return None

    def _get_directory_contents(self, owner, repo, branch, path, context):
        """获取目录内容列表"""
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"

            req = urllib.request.Request(api_url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'ComfyUI-XnanTool-SkillDownloader')

            with urllib.request.urlopen(req, context=context, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data if isinstance(data, list) else None
        except Exception as e:
            print(f"[技能下载] 获取目录内容失败: {e}")
            return None

    def _download_file(self, url, target_path, context):
        """下载单个文件"""
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'ComfyUI-XnanTool-SkillDownloader')

            with urllib.request.urlopen(req, context=context, timeout=60) as response:
                content = response.read()

            # 确保目录存在
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            with open(target_path, 'wb') as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"[技能下载] 下载文件失败 {url}: {e}")
            return False

    def _download_directory(self, owner, repo, branch, path, target_dir, contents, context, downloaded_files, relative_path):
        """递归下载目录"""
        for item in contents:
            item_name = item.get('name', '')
            item_type = item.get('type', '')
            item_path = item.get('path', '')
            download_url = item.get('download_url', '')

            if relative_path:
                current_relative = f"{relative_path}/{item_name}"
            else:
                current_relative = item_name

            target_path = os.path.join(target_dir, item_name)

            if item_type == 'file' and download_url:
                # 下载文件
                if self._download_file(download_url, target_path, context):
                    downloaded_files.append(current_relative)

            elif item_type == 'dir':
                # 递归下载子目录
                os.makedirs(target_path, exist_ok=True)
                sub_contents = self._get_directory_contents(owner, repo, branch, item_path, context)
                if sub_contents:
                    self._download_directory(owner, repo, branch, item_path, target_path, sub_contents, context, downloaded_files, current_relative)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "SkillDownloaderNode": SkillDownloaderNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SkillDownloaderNode": "技能下载"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
