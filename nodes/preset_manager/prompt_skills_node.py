#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
提示词技能库节点
功能：扫描 skills 目录下的子目录，读取 SKILL.md 和引用文件

技能目录结构：
skills/
  xxx/
    SKILL.md          # 技能主文件
    references/       # 引用文件目录（可选）
      file1.txt
      file2.txt
"""

import os

# 技能文件目录
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")


def parse_front_matter(content):
    """
    解析 YAML front matter

    Returns:
        tuple: (front_matter_dict, body_content)
    """
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    front_matter_text = parts[1].strip()
    body = parts[2].strip()

    result = {}
    for line in front_matter_text.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('name:'):
            result["name"] = stripped[5:].strip()
        elif stripped.startswith('description:'):
            result["description"] = stripped[12:].strip()
        elif stripped.startswith('compatibility:'):
            result["compatibility"] = stripped[14:].strip()

    return result, body


def load_skills():
    """
    扫描 skills 目录下的子目录，加载技能

    支持两种格式：
    1. 包含 SKILL.md 的目录（标准技能格式）
    2. 不包含 SKILL.md 的目录（普通文件集合）

    Returns:
        list: 技能列表
    """
    skills = []

    if not os.path.exists(SKILLS_DIR):
        os.makedirs(SKILLS_DIR, exist_ok=True)
        return skills

    for item in sorted(os.listdir(SKILLS_DIR)):
        item_path = os.path.join(SKILLS_DIR, item)

        # 只处理子目录
        if not os.path.isdir(item_path):
            continue

        skill_md = os.path.join(item_path, "SKILL.md")

        # 格式1：包含 SKILL.md 的标准技能
        if os.path.exists(skill_md):
            try:
                with open(skill_md, 'r', encoding='utf-8') as f:
                    content = f.read()

                front_matter, body = parse_front_matter(content)

                # 读取引用文件
                ref_files = {}
                refs_dir = os.path.join(item_path, "references")
                if os.path.exists(refs_dir) and os.path.isdir(refs_dir):
                    for ref_file in sorted(os.listdir(refs_dir)):
                        ref_path = os.path.join(refs_dir, ref_file)
                        if os.path.isfile(ref_path):
                            try:
                                with open(ref_path, 'r', encoding='utf-8') as f:
                                    ref_files[ref_file] = f.read()
                            except Exception as e:
                                print(f"[提示词技能库] 读取引用文件失败 {ref_path}: {e}")

                skill = {
                    "name": front_matter.get("name", "") or item,
                    "description": front_matter.get("description", ""),
                    "body": body,
                    "ref_files": ref_files,
                    "dir": item_path
                }
                skills.append(skill)

            except Exception as e:
                print(f"[提示词技能库] 解析技能失败 {skill_md}: {e}")

        # 格式2：不包含 SKILL.md 的普通目录
        else:
            try:
                # 读取目录中的所有文件
                all_files = {}
                for filename in sorted(os.listdir(item_path)):
                    file_path = os.path.join(item_path, filename)
                    if os.path.isfile(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                all_files[filename] = f.read()
                        except Exception as e:
                            print(f"[提示词技能库] 读取文件失败 {file_path}: {e}")

                if all_files:
                    # 组合所有文件内容
                    body_parts = []
                    for filename, content in all_files.items():
                        body_parts.append(f"--- {filename} ---\n{content}")
                    body = "\n\n".join(body_parts)

                    skill = {
                        "name": item,
                        "description": f"从 {item} 目录加载的文件集合",
                        "body": body,
                        "ref_files": {},
                        "dir": item_path
                    }
                    skills.append(skill)

            except Exception as e:
                print(f"[提示词技能库] 加载目录失败 {item_path}: {e}")

    return skills


class PromptSkillNode:
    """提示词技能库节点 - 从 skills 子目录读取技能文件"""

    @classmethod
    def INPUT_TYPES(cls):
        skills = load_skills()
        skill_names = ["无"] + [s["name"] for s in skills]

        return {
            "required": {
                "skill": (skill_names, {
                    "default": "无",
                    "label": "选择技能"
                }),
                "include_references": ("BOOLEAN", {
                    "default": True,
                    "label": "包含引用文件"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("技能内容",)
    FUNCTION = "load_skill"
    CATEGORY = "❤️❤️❤️XnanTool/预设"

    def load_skill(self, skill, include_references):
        """加载并输出技能内容"""
        if skill == "无":
            return ("",)

        skills = load_skills()
        selected = None
        for s in skills:
            if s["name"] == skill:
                selected = s
                break

        if not selected:
            return ("",)

        # 组合输出内容
        result = selected["body"]

        if include_references and selected["ref_files"]:
            result += "\n\n"
            for ref_name, ref_content in selected["ref_files"].items():
                result += f"--- {ref_name} ---\n{ref_content}\n\n"

        return (result,)


# 注册节点
NODE_CLASS_MAPPINGS = {
    "PromptSkillNode": PromptSkillNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptSkillNode": "skills"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
