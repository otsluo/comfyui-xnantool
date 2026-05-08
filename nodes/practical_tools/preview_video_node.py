import folder_paths
import os
import av
import tempfile

class PreviewVideoNode:
    """预览视频节点 - 预览处理后的视频"""
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "multiline": False}),
            },
            "optional": {
                "max_width": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 1, "tooltip": "最大预览宽度，0表示不限制"}),
            },
        }
    
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "preview_video"
    CATEGORY = "XnanTool/视频剪辑"
    
    def preview_video(self, video, filename_prefix="ComfyUI", max_width=0):
        try:
            if hasattr(video, 'get_stream_source'):
                video_path = video.get_stream_source()
                if isinstance(video_path, str) and os.path.exists(video_path):
                    pass
                else:
                    video_path = None
            else:
                video_path = None
            
            if video_path is None:
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                    video.save_to(tmp)
                    video_path = tmp.name
        except Exception as e:
            return {"ui": {"text": f"错误: 无法获取视频数据 - {str(e)}"}}
        
        if not video_path or not os.path.exists(video_path):
            return {"ui": {"text": "错误: 无法获取视频路径"}}
        
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix,
            self.output_dir,
            1920,
            1080
        )
        
        file = f"{filename}_{counter:05}_.mp4"
        full_output_path = os.path.join(full_output_folder, file)
        
        with av.open(video_path) as src_container:
            video_stream = None
            audio_stream = None
            
            for stream in src_container.streams:
                if stream.type == 'video' and video_stream is None:
                    video_stream = stream
                elif stream.type == 'audio' and audio_stream is None:
                    audio_stream = stream
            
            if video_stream is None:
                return {"ui": {"text": "错误: 视频中无视频流"}}
            
            # 确保宽高为偶数（libx264要求）
            width = video_stream.width
            height = video_stream.height
            if width % 2 != 0:
                width += 1
            if height % 2 != 0:
                height += 1
            
            out_container = av.open(full_output_path, mode='w')
            
            stream_map = {}
            for stream in src_container.streams:
                if stream.type in ('video', 'audio'):
                    if stream.type == 'video':
                        # 视频流使用模板但调整尺寸
                        out_stream = out_container.add_stream_from_template(template=stream, opaque=True)
                        out_stream.width = width
                        out_stream.height = height
                    else:
                        out_stream = out_container.add_stream_from_template(template=stream, opaque=True)
                    stream_map[stream] = out_stream
            
            for packet in src_container.demux():
                if packet.stream in stream_map and packet.dts is not None:
                    packet.stream = stream_map[packet.stream]
                    out_container.mux(packet)
            
            out_container.close()
        
        result = {
            "filename": file,
            "subfolder": subfolder,
            "type": "output"
        }
        
        print(f"👁️ 视频预览: {full_output_path}")
        
        return {"ui": {"images": [result], "animated": (True,)}}


NODE_CLASS_MAPPINGS = {
    "PreviewVideoNode": PreviewVideoNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PreviewVideoNode": "预览视频"
}
