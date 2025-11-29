import asyncio
import copy
import base64
from io import BytesIO
from typing import Any, Literal
from pprint import pprint
import re
from ollama import Client, AsyncClient
import numpy as np
from PIL import Image
from dataclasses import dataclass, field

# For type checking only. Torch is not installed at runtime
try:
    import torch
except ImportError:
    torch = None

@dataclass
class ChatSession:
    messages: list[dict] = field(default_factory=list)
    model: str = ""

# Dictionary global per session_id
CHAT_SESSIONS: dict[str, ChatSession] = {}

# Function to filter enabled options
def _filter_enabled_options(options: dict[str, Any] | None) -> dict[str, Any] | None:
    """仅返回 'enable_*' 标志为 True 的 Ollama 选项。"""
    if not options:
        return None
    enablers = [
        "enable_mirostat",
        "enable_mirostat_eta",
        "enable_mirostat_tau",
        "enable_num_ctx",
        "enable_repeat_last_n",
        "enable_repeat_penalty",
        "enable_temperature",
        "enable_seed",
        "enable_stop",
        "enable_tfs_z",
        "enable_num_predict",
        "enable_top_k",
        "enable_top_p",
        "enable_min_p",
    ]
    out: dict[str, Any] = {}
    for enabler in enablers:
        if options.get(enabler, False):
            key = enabler.replace("enable_", "")
            out[key] = options[key]
    return out or None

class OllamaGenerateRefactored:
    """
    重构版的 Ollama 文本生成节点，具有以下增强功能：
    1. 支持连接验证和重连功能
    2. 异步处理支持
    3. 增强的错误处理和日志记录
    4. 改进的会话管理
    """
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "system": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "You are a helpful AI assistant.",
                        "tooltip": "系统提示词 - 用于设置模型的角色和一般行为。",
                    },
                ),
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "请介绍一下人工智能技术的发展现状。",
                        "tooltip": "用户提示词 - 想让模型回答的问题或执行的任务。对于视觉任务，可以引用输入图像为'这张图片'、'照片'等，例如'详细描述这张图片'",
                    },
                ),
                "think": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "如果启用，模型将在回答前进行思考过程。这可以产生更准确的结果。思考过程作为一个单独的输出可用于调试或理解模型如何得出答案。某些模型不支持此功能，生成可能会失败。",
                    },
                ),
                "format": (
                    ["text", "json"],
                    {
                        "tooltip": "响应的输出格式。'text'将返回纯文本响应，而'json'将返回JSON格式的结构化响应。当模型是较大管道的一部分并且需要对响应进行额外处理时，这很有用。在这种情况下，我建议在系统提示中显示模型示例输出。某些模型在结构化输出方面表现不佳。"
                    },
                ),
                "validate_connection": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "是否验证连接配置的有效性。启用后，节点会在生成前检查Ollama服务器连接和模型可用性。",
                    },
                ),
                "reconnect": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "是否在每次生成前重新连接到Ollama服务器。对于不稳定的网络连接或长时间运行的工作流很有用。",
                    },
                ),
            },
            "optional": {
                "connectivity": (
                    "OLLAMA_CONNECTIVITY",
                    {
                        "forceInput": False,
                        "tooltip": "设置Ollama提供者用于生成。如果此输入为空，则必须设置'meta'输入。",
                    },
                ),
                "options": (
                    "OLLAMA_OPTIONS",
                    {
                        "forceInput": False,
                        "tooltip": "连接Ollama选项节点以进行高级推理配置。",
                    },
                ),
                "images": (
                    "IMAGE",
                    {
                        "forceInput": False,
                        "tooltip": "为视觉任务提供图像或图像批次。确保所选模型支持视觉，否则可能会产生幻觉响应。",
                    },
                ),
                "meta": (
                    "OLLAMA_META",
                    {
                        "forceInput": False,
                        "tooltip": "使用此输入链接多个'Ollama生成'节点。在这种情况下，连接性和选项输入会被传递。",
                    },
                ),
                "history": (
                    "OLLAMA_HISTORY",
                    {
                        "forceInput": False,
                        "tooltip": "可选择设置现有模型历史记录，对于多轮对话、后续问题很有用。",
                    },
                ),
                "reset_session": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "清除对话历史记录。警告：如果使用共享历史记录，这将影响所有使用相同历史记录ID的节点。",
                    },
                ),
                "timeout": (
                    "INT",
                    {
                        "default": 300,
                        "min": 1,
                        "max": 3600,
                        "step": 1,
                        "tooltip": "请求超时时间（秒）。如果服务器在此时间内没有响应，请求将被取消。",
                    },
                ),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = (
        "STRING",
        "STRING",
        "OLLAMA_META",
        "OLLAMA_HISTORY",
    )
    RETURN_NAMES = (
        "result",
        "thinking",
        "meta",
        "history",
    )
    FUNCTION = "ollama_generate_refactored"
    CATEGORY = "XnanTool/Ollama"
    DESCRIPTION = "重构版的Ollama文本生成节点。支持视觉任务、多轮对话和高级推理选项。具有连接验证、重连功能和异步处理支持。"

    async def validate_connection_async(self, url: str, model: str, timeout: int = 30) -> bool:
        """
        异步验证Ollama连接和模型可用性
        
        Args:
            url: Ollama服务器URL
            model: 模型名称
            timeout: 超时时间（秒）
            
        Returns:
            bool: 连接是否有效
        """
        try:
            client = AsyncClient(host=url, timeout=timeout)
            # 尝试列出模型以验证连接
            models = await client.list()
            # 检查指定模型是否存在
            available_models = [m['model'] for m in models.get('models', [])]
            return model in available_models
        except Exception as e:
            print(f"连接验证失败: {str(e)}")
            return False

    def validate_connection_sync(self, url: str, model: str, timeout: int = 30) -> bool:
        """
        同步验证Ollama连接和模型可用性
        
        Args:
            url: Ollama服务器URL
            model: 模型名称
            timeout: 超时时间（秒）
            
        Returns:
            bool: 连接是否有效
        """
        try:
            client = Client(host=url, timeout=timeout)
            # 尝试列出模型以验证连接
            models = client.list()
            # 检查指定模型是否存在
            available_models = [m['model'] for m in models.get('models', [])]
            return model in available_models
        except Exception as e:
            print(f"连接验证失败: {str(e)}")
            return False

    async def ollama_chat_async(
        self,
        system: str,
        prompt: str,
        think: bool,
        unique_id: str,
        format: str,
        timeout: int = 300,
        options: dict[str, Any] | None = None,
        connectivity: dict[str, Any] | None = None,
        images: list[Any] | None = None,
        meta: dict[str, Any] | None = None,
        history: str | None = None,
        reset_session: bool = False,
    ) -> tuple[str | None, str | None, dict[str, Any], str | None]:
        """
        异步Ollama聊天生成方法
        
        Args:
            system: 系统提示词
            prompt: 用户提示词
            think: 是否启用思考过程
            unique_id: 节点唯一ID
            format: 输出格式
            timeout: 请求超时时间
            options: Ollama选项
            connectivity: 连接配置
            images: 图像数据
            meta: 元数据
            history: 历史记录ID
            reset_session: 是否重置会话
            
        Returns:
            tuple: (结果文本, 思考过程, 元数据, 历史记录ID)
        """
        if meta is None:
            if connectivity is None:
                raise ValueError("必须提供'connectivity'或'meta'中的一个。")
            meta = {}

        # 更新提供的值（覆盖）
        if connectivity is not None:
            meta["connectivity"] = connectivity
        if options is not None:
            meta["options"] = options
        else:
            meta["options"] = None

        # 最终验证
        if "connectivity" not in meta or meta["connectivity"] is None:
            raise ValueError("meta中必须存在'connectivity'。")

        url = meta["connectivity"]["url"]
        model = meta["connectivity"]["model"]
        client = AsyncClient(host=url, timeout=timeout)

        debug_print = (
            True if meta["options"] is not None and meta["options"].get("debug", False) else False
        )

        ollama_format: Literal["", "json"] | None = None

        if format == "json":
            ollama_format = "json"
        elif format == "text":
            ollama_format = ""

        # 处理keep_alive参数
        keep_alive_value = meta["connectivity"].get("keep_alive", 5)
        keep_alive_unit = meta["connectivity"].get("keep_alive_unit", "minutes")
        keep_alive_unit_short = "m" if keep_alive_unit == "minutes" else "h"
        request_keep_alive = str(keep_alive_value) + keep_alive_unit_short

        # 使用共享助手而不是self.get_request_options
        request_options = _filter_enabled_options(options)

        images_b64: list[str] | None = None
        if images is not None and torch is not None:
            images_b64 = []
            for batch_number, image in enumerate(images):
                i = 255.0 * image.cpu().numpy()
                img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_bytes = base64.b64encode(buffered.getvalue()).decode("utf-8")
                images_b64.append(img_bytes)

        if debug_print:
            print(
                f"""
--- Ollama异步聊天请求: 

url: {url}
model: {model}
system: {system}
prompt: {prompt}
images: {0 if images_b64 is None else len(images_b64)}
think: {think}
options: {request_options}
keep alive: {request_keep_alive}
format: {format}
timeout: {timeout}
---------------------------------------------------------
"""
            )

        # 确定使用哪个会话
        session_key = history if history is not None else unique_id

        # 如果reset_session为True，重置会话
        if reset_session:
            CHAT_SESSIONS[session_key] = ChatSession()
            if debug_print:
                print(f"会话 {session_key} 已重置")

        # 如果会话不存在，创建它
        if session_key not in CHAT_SESSIONS:
            CHAT_SESSIONS[session_key] = ChatSession()

        session = CHAT_SESSIONS[session_key]

        # 更新返回的历史记录
        history = session_key

        # 如果有系统提示词，替换它或添加到开头
        if system:
            if session.messages and session.messages[0].get("role") == "system":
                session.messages[0] = {"role": "system", "content": system}
            else:
                session.messages.insert(0, {"role": "system", "content": system})

        # 为历史记录构造用户消息
        user_message_for_history: dict[str, Any] = {
            "role": "user",
            "content": prompt,
        }

        # 将用户消息添加到历史记录（不带图像）
        session.messages.append(user_message_for_history)

        if debug_print:
            print("\n--- Ollama聊天会话:")
            for message in session.messages:
                pprint(f"{message['role']}> {message['content'][:50]}...")
                if "images" in message:
                    for image in message["images"]:
                        pprint(f"图像: {image[:50]}...")
            print("---------------------------------------------------------")

        # 为API调用构造消息（带图像）
        messages_for_api = copy.deepcopy(session.messages)

        # 如果有图像，修改最后一条用户消息用于API调用
        if images_b64 is not None:
            messages_for_api[-1]["images"] = images_b64

        try:
            response = await client.chat(
                model=model,
                messages=messages_for_api,
                options=request_options,
                keep_alive=request_keep_alive,
                format=ollama_format,
            )

            if debug_print:
                print("\n--- Ollama聊天响应:")
                pprint(response)
                print("---------------------------------------------------------")

            ollama_response_text = response.message.content
            ollama_response_thinking = response.message.thinking if think else None

            # 将助手消息添加到历史记录
            session.messages.append(
                {
                    "role": "assistant",
                    "content": ollama_response_text,
                }
            )

            return (
                ollama_response_text,
                ollama_response_thinking,
                meta,
                history,
            )
        except Exception as e:
            error_msg = f"Ollama异步请求失败: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

    def ollama_generate_refactored(
        self,
        system: str,
        prompt: str,
        think: bool,
        format: str,
        validate_connection: bool = True,
        reconnect: bool = False,
        timeout: int = 300,
        options: dict[str, Any] | None = None,
        connectivity: dict[str, Any] | None = None,
        images: list[Any] | None = None,
        meta: dict[str, Any] | None = None,
        history: str | None = None,
        reset_session: bool = False,
        unique_id: str = "",
    ) -> tuple[str | None, str | None, dict[str, Any], str | None]:
        """
        重构版的Ollama生成方法，支持连接验证、重连和异步处理
        
        Args:
            system: 系统提示词
            prompt: 用户提示词
            think: 是否启用思考过程
            format: 输出格式
            validate_connection: 是否验证连接
            reconnect: 是否重新连接
            timeout: 请求超时时间
            options: Ollama选项
            connectivity: 连接配置
            images: 图像数据
            meta: 元数据
            history: 历史记录ID
            reset_session: 是否重置会话
            unique_id: 节点唯一ID
            
        Returns:
            tuple: (结果文本, 思考过程, 元数据, 历史记录ID)
        """
        # 如果需要验证连接或重新连接，则先验证连接
        if validate_connection or reconnect:
            if meta is not None and "connectivity" in meta and meta["connectivity"] is not None:
                url = meta["connectivity"]["url"]
                model = meta["connectivity"]["model"]
                is_valid = self.validate_connection_sync(url, model, timeout)
                if not is_valid:
                    raise Exception(f"无法连接到Ollama服务器 {url} 或模型 {model} 不可用")
            elif connectivity is not None:
                url = connectivity["url"]
                model = connectivity["model"]
                is_valid = self.validate_connection_sync(url, model, timeout)
                if not is_valid:
                    raise Exception(f"无法连接到Ollama服务器 {url} 或模型 {model} 不可用")

        # 如果启用了重新连接，使用异步方法处理
        if reconnect:
            try:
                # 在同步上下文中运行异步方法
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.ollama_chat_async(
                        system=system,
                        prompt=prompt,
                        think=think,
                        unique_id=unique_id,
                        format=format,
                        timeout=timeout,
                        options=options,
                        connectivity=connectivity,
                        images=images,
                        meta=meta,
                        history=history,
                        reset_session=reset_session,
                    )
                )
                loop.close()
                return result
            except Exception as e:
                raise Exception(f"重新连接模式下生成失败: {str(e)}")
        else:
            # 使用原始的同步方法
            if meta is None:
                if connectivity is None:
                    raise ValueError("必须提供'connectivity'或'meta'中的一个。")
                meta = {}

            # 更新提供的值（覆盖）
            if connectivity is not None:
                meta["connectivity"] = connectivity
            if options is not None:
                meta["options"] = options
            else:
                meta["options"] = None

            # 最终验证
            if "connectivity" not in meta or meta["connectivity"] is None:
                raise ValueError("meta中必须存在'connectivity'。")

            url = meta["connectivity"]["url"]
            model = meta["connectivity"]["model"]
            client = Client(host=url, timeout=timeout)

            debug_print = (
                True if meta["options"] is not None and meta["options"].get("debug", False) else False
            )

            ollama_format: Literal["", "json"] | None = None

            if format == "json":
                ollama_format = "json"
            elif format == "text":
                ollama_format = ""

            # 处理keep_alive参数
            keep_alive_value = meta["connectivity"].get("keep_alive", 5)
            keep_alive_unit = meta["connectivity"].get("keep_alive_unit", "minutes")
            keep_alive_unit_short = "m" if keep_alive_unit == "minutes" else "h"
            request_keep_alive = str(keep_alive_value) + keep_alive_unit_short

            # 使用共享助手而不是self.get_request_options
            request_options = _filter_enabled_options(options)

            images_b64: list[str] | None = None
            if images is not None and torch is not None:
                images_b64 = []
                for batch_number, image in enumerate(images):
                    i = 255.0 * image.cpu().numpy()
                    img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    img_bytes = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    images_b64.append(img_bytes)

            if debug_print:
                print(
                    f"""
--- Ollama聊天请求: 

url: {url}
model: {model}
system: {system}
prompt: {prompt}
images: {0 if images_b64 is None else len(images_b64)}
think: {think}
options: {request_options}
keep alive: {request_keep_alive}
format: {format}
timeout: {timeout}
---------------------------------------------------------
"""
                )

            # 确定使用哪个会话
            session_key = history if history is not None else unique_id

            # 如果reset_session为True，重置会话
            if reset_session:
                CHAT_SESSIONS[session_key] = ChatSession()
                if debug_print:
                    print(f"会话 {session_key} 已重置")

            # 如果会话不存在，创建它
            if session_key not in CHAT_SESSIONS:
                CHAT_SESSIONS[session_key] = ChatSession()

            session = CHAT_SESSIONS[session_key]

            # 更新返回的历史记录
            history = session_key

            # 如果有系统提示词，替换它或添加到开头
            if system:
                if session.messages and session.messages[0].get("role") == "system":
                    session.messages[0] = {"role": "system", "content": system}
                else:
                    session.messages.insert(0, {"role": "system", "content": system})

            # 为历史记录构造用户消息
            user_message_for_history: dict[str, Any] = {
                "role": "user",
                "content": prompt,
            }

            # 将用户消息添加到历史记录（不带图像）
            session.messages.append(user_message_for_history)

            if debug_print:
                print("\n--- Ollama聊天会话:")
                for message in session.messages:
                    pprint(f"{message['role']}> {message['content'][:50]}...")
                    if "images" in message:
                        for image in message["images"]:
                            pprint(f"图像: {image[:50]}...")
                print("---------------------------------------------------------")

            # 为API调用构造消息（带图像）
            messages_for_api = copy.deepcopy(session.messages)

            # 如果有图像，修改最后一条用户消息用于API调用
            if images_b64 is not None:
                messages_for_api[-1]["images"] = images_b64

            try:
                response = client.chat(
                    model=model,
                    messages=messages_for_api,
                    options=request_options,
                    keep_alive=request_keep_alive,
                    format=ollama_format,
                )

                if debug_print:
                    print("\n--- Ollama聊天响应:")
                    pprint(response)
                    print("---------------------------------------------------------")

                ollama_response_text = response.message.content
                ollama_response_thinking = response.message.thinking if think else None

                # 将助手消息添加到历史记录
                session.messages.append(
                    {
                        "role": "assistant",
                        "content": ollama_response_text,
                    }
                )

                return (
                    ollama_response_text,
                    ollama_response_thinking,
                    meta,
                    history,
                )
            except Exception as e:
                error_msg = f"Ollama请求失败: {str(e)}"
                print(error_msg)
                raise Exception(error_msg)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "OllamaGenerateRefactored": OllamaGenerateRefactored,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaGenerateRefactored": "Ollama生成-重构版",
}