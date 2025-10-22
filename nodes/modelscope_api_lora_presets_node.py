import json
import os

# 定义支持的魔搭API Lora模型列表
SUPPORTED_LORA_MODELS = [
    ["xingchensong/sd_xl_lora_test", "SDXL测试Lora"],
    ["xingchensong/flux_lora_test", "FLUX测试Lora"],
]

# Lora预设配置相关函数
def load_lora_config():
    config_path = os.path.join(os.path.dirname(__file__), 'modelscope_api_lora_presets.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 确保lora_models字段存在
            if "lora_models" not in data:
                data["lora_models"] = SUPPORTED_LORA_MODELS
            return data
    except:
        # 默认配置
        return {
            "lora_models": SUPPORTED_LORA_MODELS
        }

def save_lora_config(config: dict) -> bool:
    config_path = os.path.join(os.path.dirname(__file__), 'modelscope_api_lora_presets.json')
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存魔搭API Lora配置失败: {e}")
        return False

class ModelscopeApiLoraSelector:
    """魔搭API-Lora模型选择器节点 - 仅提供Lora模型名称选择功能"""
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_lora_config()
        lora_models = config.get("lora_models", SUPPORTED_LORA_MODELS)
        
        # 提取所有Lora模型ID和显示名称
        lora_model_ids = [model[0] for model in lora_models]
        lora_model_labels = {model[0]: model[1] for model in lora_models}
        
        # 返回输入类型配置
        return {
            "required": {
                "lora_model_name": (lora_model_ids, {
                    "default": lora_model_ids[0] if lora_model_ids else "",
                    "labels": lora_model_labels,
                    "label": "Lora模型名称",
                    "description": "选择要使用的魔搭API Lora模型名称，可通过魔搭API-Lora列表管理节点添加新模型"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("lora_model_name",)
    FUNCTION = "get_lora_model_name"
    CATEGORY = "XnanTool/魔搭api"
    
    def get_lora_model_name(self, lora_model_name):
        """返回选中的魔搭API Lora模型名称"""
        return (lora_model_name,)

class ModelscopeApiLoraManager:
    """魔搭API-Lora列表管理节点 - 用于查看和管理可用Lora模型
    
    主要功能：
    1. 列出所有可用的魔搭API Lora模型列表
    2. 添加新的魔搭API Lora模型到预设列表中
    3. 删除已有的魔搭API Lora模型
    
    使用说明：
    - 选择"list"操作可查看当前所有可用Lora模型
    - 选择"add"操作可添加新的Lora模型（需要填写模型ID和显示名称）
    - 选择"delete"操作可删除Lora模型（通过下拉列表选择模型）
    - 所有操作结果会通过status_message输出
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        config = load_lora_config()
        lora_models = config.get("lora_models", SUPPORTED_LORA_MODELS)
        
        # 提取所有Lora模型ID和显示名称，用于delete操作的下拉选择
        lora_model_ids = [model[0] for model in lora_models]
        lora_model_labels = {model[0]: model[1] for model in lora_models}
        
        return {
            "required": {
                "action": (["list", "add", "delete"], {
                    "default": "list",
                    "label": "操作类型",
                    "description": "选择要执行的操作：list(查看模型列表)、add(添加新模型)或delete(删除模型)"
                })
            },
            "optional": {
                "lora_model_id": ("STRING", {
                    "default": "",
                    "placeholder": "例如: xingchensong/new-lora-model",
                    "label": "Lora模型ID",
                    "description": "魔搭平台上的完整Lora模型ID，仅在add操作时需要填写"
                }),
                "lora_model_display_name": ("STRING", {
                    "default": "",
                    "placeholder": "例如: 新Lora模型显示名称",
                    "label": "显示名称",
                    "description": "Lora模型的显示名称，用于在选择器中识别，仅在add操作时需要填写"
                }),
                "lora_model_to_delete": (lora_model_ids, {
                    "default": lora_model_ids[0] if lora_model_ids else "",
                    "labels": lora_model_labels,
                    "label": "要删除的Lora模型",
                    "description": "选择要删除的Lora模型，仅在delete操作时有效"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status_message",)
    FUNCTION = "manage_lora_models"
    CATEGORY = "XnanTool/魔搭api"
    
    def manage_lora_models(self, action, lora_model_id="", lora_model_display_name="", lora_model_to_delete=""):
        config = load_lora_config()
        lora_models = config.get("lora_models", SUPPORTED_LORA_MODELS)
        
        if action == "list":
            # 列出所有可用Lora模型
            message = "可用魔搭API Lora模型列表:\n"
            message += "==============\n"
            message += "使用说明:\n"
            message += "1. 选择模型ID可直接用于魔搭API-Lora模型选择器节点\n"
            message += "2. 通过add操作可添加新的Lora模型\n"
            message += "3. 通过delete操作可删除现有Lora模型（直接下拉选择）\n"
            message += "4. 添加或删除后需重启ComfyUI才能在选择器中看到变化\n"
            message += "5. name：SDXL测试Lora(可随意) 、ID: xingchensong/sd_xl_lora_test\n"
            message += "==============\n"
            message += "Lora模型列表:\n"
            
            for i, model_tuple in enumerate(lora_models):
                try:
                    # 安全地获取模型信息
                    if isinstance(model_tuple, list) and len(model_tuple) >= 2:
                        model_id_val = model_tuple[0]
                        display_name_val = model_tuple[1]
                        message += f"{i+1}. {display_name_val} (ID: {model_id_val})\n"
                    else:
                        message += f"{i+1}. 无效的模型定义: {model_tuple}\n"
                except Exception as e:
                    message += f"{i+1}. 处理模型时出错: {str(e)}\n"
            
            return (message,)
        
        elif action == "add":
            # 添加新Lora模型
            if not lora_model_id or not lora_model_display_name:
                return ("添加失败: Lora模型ID和显示名称不能为空\n提示：请确保同时填写模型ID和显示名称",)
            
            # 检查是否已存在
            try:
                for model_tuple in lora_models:
                    if isinstance(model_tuple, list) and len(model_tuple) > 0:
                        existing_id = model_tuple[0]  # 只获取第一个元素作为模型ID
                        if existing_id == lora_model_id:
                            return ("添加失败: 该Lora模型ID已存在\n提示：请尝试使用不同的模型ID",)
            except Exception as e:
                return (f"检查Lora模型是否存在时出错: {str(e)}",)
            
            # 添加新Lora模型
            lora_models.append([lora_model_id, lora_model_display_name])
            config["lora_models"] = lora_models
            success = save_lora_config(config)
            
            if success:
                return (f"成功添加魔搭API Lora模型: {lora_model_display_name} ({lora_model_id})\n提示：请重启ComfyUI以在魔搭API-Lora模型选择器中看到新添加的模型",)
            else:
                return ("添加魔搭API Lora模型失败，请检查日志\n可能原因：文件权限问题或磁盘空间不足",)
        
        elif action == "delete":
            # 删除Lora模型 - 现在使用下拉选择的lora_model_to_delete参数
            if not lora_model_to_delete:
                return ("删除失败: 请从下拉列表中选择要删除的Lora模型",)
            
            # 检查是否存在
            model_index = -1
            try:
                for i, model_tuple in enumerate(lora_models):
                    if isinstance(model_tuple, list) and len(model_tuple) > 0:
                        existing_id = model_tuple[0]
                        if existing_id == lora_model_to_delete:
                            model_index = i
                            break
            except Exception as e:
                return (f"检查Lora模型是否存在时出错: {str(e)}",)
            
            if model_index == -1:
                return ("删除失败: 未找到指定的Lora模型\n提示：请确认选择的模型是否正确",)
            
            # 确保不删除所有内置模型
            built_in_count = 0
            for model_tuple in lora_models:
                if isinstance(model_tuple, list) and len(model_tuple) > 0:
                    for built_in_model in SUPPORTED_LORA_MODELS:
                        if built_in_model[0] == model_tuple[0]:
                            built_in_count += 1
                            break
            
            # 检查是否是最后一个内置模型
            is_last_built_in = False
            if model_index < len(lora_models):
                model_to_remove = lora_models[model_index]
                if isinstance(model_to_remove, list) and len(model_to_remove) > 0:
                    for built_in_model in SUPPORTED_LORA_MODELS:
                        if built_in_model[0] == model_to_remove[0]:
                            if built_in_count <= 1:
                                is_last_built_in = True
                            break
            
            if is_last_built_in:
                return ("删除失败: 不能删除所有内置Lora模型\n提示：至少保留一个内置模型以确保功能正常",)
            
            # 删除Lora模型
            model_removed = lora_models.pop(model_index)
            config["lora_models"] = lora_models
            success = save_lora_config(config)
            
            if success:
                display_name = model_removed[1] if isinstance(model_removed, list) and len(model_removed) >= 2 else "未知名称"
                return (f"成功删除魔搭API Lora模型: {display_name} ({lora_model_to_delete})\n提示：请重启ComfyUI以在魔搭API-Lora模型选择器中看到更新",)
            else:
                return ("删除魔搭API Lora模型失败，请检查日志\n可能原因：文件权限问题或磁盘空间不足",)
        
        return ("未知操作\n提示：请选择有效的操作类型（list、add或delete）",)

# 节点映射和显示名称映射
NODE_CLASS_MAPPINGS = {
    "ModelscopeApiLoraSelector": ModelscopeApiLoraSelector,
    "ModelscopeApiLoraManager": ModelscopeApiLoraManager
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ModelscopeApiLoraSelector": "魔搭API-Lora模型选择器",
    "ModelscopeApiLoraManager": "魔搭API-Lora列表管理"
}

# 确保模块被正确导入
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]