#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class PresetManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图片视频提示词预设管理器")
        self.root.geometry("900x700")
        
        # 设置JSON文件路径
        self.json_file_path = os.path.join(os.path.dirname(__file__), 'nodes', 'image_video_prompt_presets.json')
        self.presets = []
        
        # 拖拽相关变量
        self.drag_item = None
        self.drag_placeholder = None
        
        # 创建界面
        self.create_widgets()
        
        # 加载预设数据
        self.load_presets()
        
        # 初始化界面
        self.refresh_preset_list()
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="图片视频提示词预设管理器", font=("", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件信息
        file_info_frame = ttk.Frame(main_frame)
        file_info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(file_info_frame, text=f"数据文件: {self.json_file_path}").grid(row=0, column=0, sticky=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.N, tk.W), padx=(0, 10))
        
        # 列表框架
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 编辑框架
        edit_frame = ttk.Frame(main_frame)
        edit_frame.grid(row=2, column=2, sticky=(tk.N, tk.E), padx=(10, 0))
        edit_frame.columnconfigure(0, weight=1)
        
        # 按钮区域
        ttk.Button(button_frame, text="添加预设", command=self.add_preset).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="删除预设", command=self.delete_preset).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="上移预设", command=self.move_preset_up).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="下移预设", command=self.move_preset_down).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="保存数据", command=self.save_presets).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="重新加载", command=self.load_presets).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="清空表单", command=self.clear_form).pack(fill=tk.X, pady=5)
        
        # 搜索区域
        search_frame = ttk.Frame(button_frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="搜索:").pack(anchor=tk.W)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X)
        
        # 预设列表
        list_label = ttk.Label(list_frame, text="预设列表", font=("", 12, "bold"))
        list_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 创建Treeview
        columns = ('name', 'image_prompt', 'video_prompt')
        self.preset_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        # 定义列标题
        self.preset_tree.heading('name', text='预设名称')
        self.preset_tree.heading('image_prompt', text='图片提示词')
        self.preset_tree.heading('video_prompt', text='视频提示词')
        
        # 设置列宽
        self.preset_tree.column('name', width=150)
        self.preset_tree.column('image_prompt', width=200)
        self.preset_tree.column('video_prompt', width=200)
        
        # 添加滚动条
        list_scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.preset_tree.yview)
        list_scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.preset_tree.xview)
        self.preset_tree.configure(yscrollcommand=list_scrollbar_y.set, xscrollcommand=list_scrollbar_x.set)
        
        # 布局
        self.preset_tree.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        list_scrollbar_y.grid(row=1, column=1, sticky=(tk.N, tk.S))
        list_scrollbar_x.grid(row=2, column=0, sticky=(tk.E, tk.W))
        
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # 绑定选择事件
        self.preset_tree.bind('<<TreeviewSelect>>', self.on_preset_select)
        
        # 绑定拖拽事件
        self.preset_tree.bind('<Button-1>', self.on_drag_start)
        self.preset_tree.bind('<B1-Motion>', self.on_drag_motion)
        self.preset_tree.bind('<ButtonRelease-1>', self.on_drag_release)
        
        # 编辑表单
        edit_label = ttk.Label(edit_frame, text="编辑预设", font=("", 12, "bold"))
        edit_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 表单字段
        form_fields = [
            ("预设名称:", "name"),
            ("图片提示词:", "image_prompt"),
            ("视频提示词:", "video_prompt"),
            ("图片路径:", "image_path")
        ]
        
        self.form_vars = {}
        for i, (label_text, field_name) in enumerate(form_fields):
            ttk.Label(edit_frame, text=label_text).grid(row=i*2+1, column=0, sticky=tk.W, pady=(5, 0))
            var = tk.StringVar()
            entry = tk.Text(edit_frame, height=3, width=30)
            entry.grid(row=i*2+2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            self.form_vars[field_name] = (var, entry)
            edit_frame.rowconfigure(i*2+2, weight=1)
        
        # 保存按钮
        ttk.Button(edit_frame, text="保存更改", command=self.save_current_preset).grid(row=len(form_fields)*2+1, column=0, pady=10)
        
        edit_frame.columnconfigure(0, weight=1)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def load_presets(self):
        """加载预设数据"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.presets = data.get('prompt_presets', [])
            self.update_status(f"成功加载 {len(self.presets)} 个预设")
            self.refresh_preset_list()
        except FileNotFoundError:
            self.update_status(f"文件 {self.json_file_path} 不存在")
            self.presets = []
        except json.JSONDecodeError as e:
            self.update_status(f"JSON解析错误: {e}")
            self.presets = []
        except Exception as e:
            self.update_status(f"加载预设时出错: {e}")
            self.presets = []
    
    def save_presets(self):
        """保存预设数据"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)
            
            data = {
                'prompt_presets': self.presets
            }
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.update_status("预设已保存")
            messagebox.showinfo("成功", "预设已保存")
        except Exception as e:
            self.update_status(f"保存预设时出错: {e}")
            messagebox.showerror("错误", f"保存预设时出错: {e}")
    
    def refresh_preset_list(self):
        """刷新预设列表"""
        # 清空现有项目
        for item in self.preset_tree.get_children():
            self.preset_tree.delete(item)
        
        # 添加预设到列表
        search_term = self.search_var.get().lower()
        for preset in self.presets:
            # 如果有搜索词，过滤结果
            if search_term:
                if not (search_term in preset.get('name', '').lower() or
                       search_term in preset.get('image_prompt', '').lower() or
                       search_term in preset.get('video_prompt', '').lower()):
                    continue
            
            self.preset_tree.insert('', tk.END, values=(
                preset.get('name', ''),
                preset.get('image_prompt', '')[:50] + '...' if len(preset.get('image_prompt', '')) > 50 else preset.get('image_prompt', ''),
                preset.get('video_prompt', '')[:50] + '...' if len(preset.get('video_prompt', '')) > 50 else preset.get('video_prompt', '')
            ), tags=(self.presets.index(preset),))
    
    def on_search_change(self, *args):
        """搜索框变化时刷新列表"""
        self.refresh_preset_list()
    
    def on_preset_select(self, event):
        """选择预设时填充表单"""
        selection = self.preset_tree.selection()
        if selection:
            item = self.preset_tree.item(selection[0])
            index = int(self.preset_tree.item(selection[0])['tags'][0]) if self.preset_tree.item(selection[0])['tags'] else 0
            
            if 0 <= index < len(self.presets):
                preset = self.presets[index]
                self.form_vars['name'][1].delete(1.0, tk.END)
                self.form_vars['name'][1].insert(tk.END, preset.get('name', ''))
                
                self.form_vars['image_prompt'][1].delete(1.0, tk.END)
                self.form_vars['image_prompt'][1].insert(tk.END, preset.get('image_prompt', ''))
                
                self.form_vars['video_prompt'][1].delete(1.0, tk.END)
                self.form_vars['video_prompt'][1].insert(tk.END, preset.get('video_prompt', ''))
                
                self.form_vars['image_path'][1].delete(1.0, tk.END)
                self.form_vars['image_path'][1].insert(tk.END, preset.get('image_path', ''))
    
    def add_preset(self):
        """添加新预设"""
        new_preset = {
            'name': '新预设',
            'image_prompt': '',
            'video_prompt': '',
            'image_path': 'image_video_prompt_presets_node/新预设.png'
        }
        self.presets.append(new_preset)
        self.refresh_preset_list()
        self.update_status("已添加新预设")
    
    def delete_preset(self):
        """删除选中的预设"""
        selection = self.preset_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的预设")
            return
        
        if len(self.presets) <= 1:
            messagebox.showwarning("警告", "至少需要保留一个预设")
            return
        
        if messagebox.askyesno("确认", "确定要删除这个预设吗？"):
            item = self.preset_tree.item(selection[0])
            index = int(self.preset_tree.item(selection[0])['tags'][0]) if self.preset_tree.item(selection[0])['tags'] else 0
            
            if 0 <= index < len(self.presets):
                deleted = self.presets.pop(index)
                self.refresh_preset_list()
                self.clear_form()
                self.update_status(f"已删除预设: {deleted['name']}")
    
    def save_current_preset(self):
        """保存当前编辑的预设"""
        selection = self.preset_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要保存的预设")
            return
        
        item = self.preset_tree.item(selection[0])
        index = int(self.preset_tree.item(selection[0])['tags'][0]) if self.preset_tree.item(selection[0])['tags'] else 0
        
        if 0 <= index < len(self.presets):
            # 获取表单数据
            name = self.form_vars['name'][1].get(1.0, tk.END).strip()
            image_prompt = self.form_vars['image_prompt'][1].get(1.0, tk.END).strip()
            video_prompt = self.form_vars['video_prompt'][1].get(1.0, tk.END).strip()
            image_path = self.form_vars['image_path'][1].get(1.0, tk.END).strip()
            
            # 更新预设
            self.presets[index] = {
                'name': name,
                'image_prompt': image_prompt,
                'video_prompt': video_prompt,
                'image_path': image_path
            }
            
            # 刷新列表
            self.refresh_preset_list()
            self.update_status("预设已更新")
            messagebox.showinfo("成功", "预设已更新")
    
    def clear_form(self):
        """清空表单"""
        for var, entry in self.form_vars.values():
            entry.delete(1.0, tk.END)

    def move_preset_up(self):
        """向上移动选中的预设"""
        selection = self.preset_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要移动的预设")
            return
        
        item = self.preset_tree.item(selection[0])
        index = int(self.preset_tree.item(selection[0])['tags'][0]) if self.preset_tree.item(selection[0])['tags'] else 0
        
        # 检查是否可以向上移动
        if index <= 0:
            messagebox.showinfo("提示", "该预设已在最顶部，无法继续上移")
            return
        
        # 交换位置
        self.presets[index], self.presets[index-1] = self.presets[index-1], self.presets[index]
        
        # 刷新列表
        self.refresh_preset_list()
        
        # 重新选中移动后的项目
        for i, child in enumerate(self.preset_tree.get_children()):
            if int(self.preset_tree.item(child)['tags'][0]) == index-1:
                self.preset_tree.selection_set(child)
                self.preset_tree.see(child)
                break
        
        self.update_status(f"预设 '{self.presets[index-1]['name']}' 已上移")
    
    def move_preset_down(self):
        """向下移动选中的预设"""
        selection = self.preset_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要移动的预设")
            return
        
        item = self.preset_tree.item(selection[0])
        index = int(self.preset_tree.item(selection[0])['tags'][0]) if self.preset_tree.item(selection[0])['tags'] else 0
        
        # 检查是否可以向下移动
        if index >= len(self.presets) - 1:
            messagebox.showinfo("提示", "该预设已在最底部，无法继续下移")
            return
        
        # 交换位置
        self.presets[index], self.presets[index+1] = self.presets[index+1], self.presets[index]
        
        # 刷新列表
        self.refresh_preset_list()
        
        # 重新选中移动后的项目
        for i, child in enumerate(self.preset_tree.get_children()):
            if int(self.preset_tree.item(child)['tags'][0]) == index+1:
                self.preset_tree.selection_set(child)
                self.preset_tree.see(child)
                break
        
        self.update_status(f"预设 '{self.presets[index+1]['name']}' 已下移")

    def on_drag_start(self, event):
        """开始拖拽"""
        item = self.preset_tree.identify_row(event.y)
        if item:
            self.drag_item = item
            self.preset_tree.selection_set(item)
        else:
            self.drag_item = None

    def on_drag_motion(self, event):
        """拖拽进行中"""
        if not self.drag_item:
            return
            
        # 获取目标位置
        target_item = self.preset_tree.identify_row(event.y)
        
        # 如果目标位置有效且不同于当前拖拽项
        if target_item and target_item != self.drag_item:
            # 在目标位置之前插入拖拽项
            self.preset_tree.move(self.drag_item, '', self.preset_tree.index(target_item))

    def on_drag_release(self, event):
        """释放拖拽"""
        if not self.drag_item:
            return
            
        # 获取拖拽项
        dragged_item = self.drag_item
        self.drag_item = None
        
        # 获取新的索引位置
        new_index = self.preset_tree.index(dragged_item)
        
        # 更新数据模型
        # 首先找到该项目在原始数据中的索引
        for i, child in enumerate(self.preset_tree.get_children()):
            if child == dragged_item:
                # 获取原始数据索引
                original_index = int(self.preset_tree.item(child)['tags'][0])
                
                # 移动数据项
                if 0 <= original_index < len(self.presets) and original_index != new_index:
                    moved_preset = self.presets.pop(original_index)
                    # 调整插入位置，因为删除操作会影响索引
                    adjusted_index = new_index
                    if new_index > original_index:
                        adjusted_index = new_index - 1
                    self.presets.insert(adjusted_index, moved_preset)
                    
                    # 刷新整个列表以确保一致性
                    self.refresh_preset_list()
                    
                    # 更新状态栏
                    self.update_status(f"预设 '{moved_preset['name']}' 已移动到位置 {adjusted_index + 1}")
                break


def main():
    root = tk.Tk()
    app = PresetManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()