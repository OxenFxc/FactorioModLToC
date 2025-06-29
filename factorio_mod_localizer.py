#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异星工厂模组汉化工具
Factorio Mod Localization Tool

用于批量处理异星工厂模组的汉化工作
"""

import os
import zipfile
import json
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

class FactorioModLocalizer:
    def __init__(self):
        self.mods_path = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "Factorio" / "mods"
        self.cache_dir = Path(tempfile.gettempdir()) / "factorio_mod_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # 支持的语言列表
        self.supported_languages = {
            'zh-CN': '简体中文',
            'zh-TW': '繁体中文', 
            'en': '英语',
            'ja': '日语',
            'ko': '韩语',
            'ru': '俄语',
            'es-ES': '西班牙语',
            'pt-BR': '葡萄牙语',
            'fr': '法语',
            'de': '德语',
            'it': '意大利语',
            'pl': '波兰语',
            'cs': '捷克语',
            'hu': '匈牙利语',
            'nl': '荷兰语',
            'sv-SE': '瑞典语',
            'da': '丹麦语',
            'fi': '芬兰语',
            'no': '挪威语',
            'uk': '乌克兰语',
            'tr': '土耳其语',
            'vi': '越南语'
        }
        
        self.setup_gui()
    
    def setup_gui(self):
        """设置图形用户界面"""
        self.root = tk.Tk()
        self.root.title("异星工厂模组汉化工具")
        self.root.geometry("1200x900")  # 增大窗口，特别是高度
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 模组路径设置
        ttk.Label(main_frame, text="模组目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.path_var = tk.StringVar(value=str(self.mods_path))
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        path_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(path_frame, textvariable=self.path_var, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(path_frame, text="浏览", command=self.browse_mods_directory).grid(row=0, column=1)
        ttk.Button(path_frame, text="扫描模组", command=self.scan_mods).grid(row=0, column=2, padx=(5, 0))
        
        # 搜索框
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="搜索模组:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(search_frame, text="清除", command=self.clear_search).grid(row=0, column=2)
        ttk.Button(search_frame, text="显示全部", command=self.show_all_mods).grid(row=0, column=3, padx=(5, 0))
        
        # 模组列表
        ttk.Label(main_frame, text="模组列表:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=5)
        
        # 创建模组列表框架
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 模组列表树视图
        self.mod_tree = ttk.Treeview(list_frame, columns=('size', 'languages'), show='tree headings')
        self.mod_tree.heading('#0', text='模组名称', anchor=tk.W)
        self.mod_tree.heading('size', text='大小', anchor=tk.W)
        self.mod_tree.heading('languages', text='支持语言', anchor=tk.W)
        
        self.mod_tree.column('#0', width=300, minwidth=200)
        self.mod_tree.column('size', width=100, minwidth=80)
        self.mod_tree.column('languages', width=200, minwidth=150)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.mod_tree.yview)
        self.mod_tree.configure(yscrollcommand=scrollbar.set)
        
        self.mod_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 绑定选择和双击事件
        self.mod_tree.bind('<<TreeviewSelect>>', self.on_mod_select)
        self.mod_tree.bind('<Double-1>', self.on_mod_double_click)
        
        # 绑定右键菜单
        self.mod_tree.bind('<Button-3>', self.show_context_menu)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(button_frame, text="查看语言详情", command=self.show_language_details).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="打开缓存目录", command=self.open_cache_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清理缓存", command=self.clear_cache).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="返回模组列表", command=self.show_mod_list).pack(side=tk.LEFT, padx=5)
        
        # 创建语言编辑框架（初始隐藏）
        self.editor_frame = ttk.Frame(main_frame)
        self.setup_editor_interface()
        
        # 当前显示的界面
        self.current_view = "list"  # "list" 或 "editor"
        self.current_mod_path = None
        self.current_mod_info = None
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.mods_data = {}
        self.all_mods_data = {}  # 存储所有模组数据用于搜索
        
        # 配置文件路径
        self.config_file = Path("factorio_localizer_config.json")
    
    def setup_editor_interface(self):
        """设置语言编辑界面"""
        # 模组信息区域
        info_frame = ttk.LabelFrame(self.editor_frame, text="模组信息", padding="10")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="模组名称:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.mod_name_label = ttk.Label(info_frame, text="")
        self.mod_name_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(info_frame, text="版本:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.mod_version_label = ttk.Label(info_frame, text="")
        self.mod_version_label.grid(row=1, column=1, sticky=tk.W)
        
        # 语言文件选择区域
        lang_select_frame = ttk.LabelFrame(self.editor_frame, text="语言文件", padding="10")
        lang_select_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        lang_select_frame.columnconfigure(1, weight=1)
        
        ttk.Label(lang_select_frame, text="源语言:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.source_lang_combo = ttk.Combobox(lang_select_frame, state="readonly", width=15)
        self.source_lang_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        self.source_lang_combo.bind('<<ComboboxSelected>>', self.on_source_lang_change)
        
        ttk.Label(lang_select_frame, text="目标语言:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.target_lang_combo = ttk.Combobox(lang_select_frame, state="readonly", width=15)
        self.target_lang_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        # 设置目标语言默认值
        self.target_lang_combo['values'] = ['zh-CN', 'zh-TW']
        self.target_lang_combo.set('zh-CN')
        
        # 默认导出路径设置
        ttk.Label(lang_select_frame, text="导出路径:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.export_path_var = tk.StringVar(value=str(Path.home() / "Desktop" / "factorio_exports"))
        export_path_frame = ttk.Frame(lang_select_frame)
        export_path_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        export_path_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(export_path_frame, textvariable=self.export_path_var, width=30).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(export_path_frame, text="浏览", command=self.browse_export_path).grid(row=0, column=1)
        ttk.Button(export_path_frame, text="设为默认", command=self.set_default_export_path).grid(row=0, column=2, padx=(5, 0))
        
        # 操作模式选择
        ttk.Label(lang_select_frame, text="操作模式:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.operation_var = tk.StringVar(value="new")
        ttk.Radiobutton(lang_select_frame, text="新建汉化文件", variable=self.operation_var, value="new").grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        ttk.Radiobutton(lang_select_frame, text="替换现有文件", variable=self.operation_var, value="replace").grid(row=1, column=2, sticky=tk.W, pady=(10, 0))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.editor_frame, text="语言文件内容", padding="10")
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.file_combo = ttk.Combobox(file_frame, state="readonly", width=30)
        self.file_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.file_combo.bind('<<ComboboxSelected>>', self.on_file_change)
        
        ttk.Button(file_frame, text="加载文件", command=self.load_selected_file).grid(row=0, column=2)
        
        # 文件操作按钮
        file_ops_frame = ttk.Frame(file_frame)
        file_ops_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(file_ops_frame, text="导出源文件", command=self.export_source_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_ops_frame, text="导出目标文件", command=self.export_target_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="从本地导入", command=self.import_local_file).pack(side=tk.LEFT, padx=5)
        
        # 编辑区域 - 增加高度和权重
        edit_frame = ttk.LabelFrame(self.editor_frame, text="编辑内容", padding="10")
        edit_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        edit_frame.columnconfigure(0, weight=1)
        edit_frame.rowconfigure(0, weight=1)
        
        # 创建可拖拽调整大小的上下分栏 - 增加整体高度
        self.paned_window = ttk.PanedWindow(edit_frame, orient=tk.VERTICAL)
        self.paned_window.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 上方：原文
        top_frame = ttk.LabelFrame(self.paned_window, text="原文 (只读)", padding="5")
        top_frame.columnconfigure(0, weight=1)
        top_frame.rowconfigure(0, weight=1)
        
        self.source_text = ScrolledText(top_frame, height=18, state=tk.DISABLED, wrap=tk.WORD)
        self.source_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 下方：译文
        bottom_frame = ttk.LabelFrame(self.paned_window, text="译文 (可编辑)", padding="5")
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.rowconfigure(0, weight=1)
        
        self.target_text = ScrolledText(bottom_frame, height=18, wrap=tk.WORD)
        self.target_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加到分栏窗口，设置权重
        self.paned_window.add(top_frame, weight=1)
        self.paned_window.add(bottom_frame, weight=1)
        
        # 设置最小窗格大小（使用正确的方法）- 减小最小尺寸以增加拖拽范围
        try:
            self.paned_window.pane(top_frame, minsize=100)
            self.paned_window.pane(bottom_frame, minsize=100)
        except Exception:
            # 如果设置失败，不影响正常使用
            pass
        
        # 延迟设置初始分隔位置（50:50）
        self.root.after(100, self.set_initial_pane_position)
        
        # 保存按钮
        save_frame = ttk.Frame(self.editor_frame)
        save_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(save_frame, text="保存到ZIP", command=self.save_to_zip).pack(side=tk.LEFT, padx=5)
        ttk.Button(save_frame, text="预览更改", command=self.preview_changes).pack(side=tk.LEFT, padx=5)
        
        # 配置编辑器框架的权重 - 给编辑区域更大的权重
        self.editor_frame.columnconfigure(0, weight=1)
        self.editor_frame.columnconfigure(1, weight=1)
        self.editor_frame.rowconfigure(3, weight=3)  # 编辑区域占据更多垂直空间
        self.editor_frame.rowconfigure(0, weight=0)  # 模组信息区域固定高度
        self.editor_frame.rowconfigure(1, weight=0)  # 语言选择区域固定高度
        self.editor_frame.rowconfigure(2, weight=0)  # 文件选择区域固定高度
        self.editor_frame.rowconfigure(4, weight=0)  # 按钮区域固定高度
        
        # 加载配置
        self.load_config()
    
    def set_initial_pane_position(self):
        """设置分栏窗口的初始位置（50:50）"""
        try:
            # 获取分栏窗口的高度（垂直分栏）
            self.paned_window.update_idletasks()
            height = self.paned_window.winfo_height()
            if height > 200:  # 确保窗口已经正确显示
                # 设置分隔位置为中间（垂直分栏用y坐标）
                self.paned_window.sash_place(0, 0, height // 2)
        except Exception:
            # 如果设置失败，不影响正常使用
            pass
    
    def browse_mods_directory(self):
        """浏览模组目录"""
        directory = filedialog.askdirectory(initialdir=str(self.mods_path))
        if directory:
            self.path_var.set(directory)
            self.mods_path = Path(directory)
    
    def scan_mods(self):
        """扫描模组目录"""
        self.mods_path = Path(self.path_var.get())
        
        if not self.mods_path.exists():
            messagebox.showerror("错误", f"目录不存在: {self.mods_path}")
            return
        
        self.status_var.set("正在扫描模组...")
        self.root.update()
        
        # 清空现有数据
        for item in self.mod_tree.get_children():
            self.mod_tree.delete(item)
        self.mods_data.clear()
        self.all_mods_data.clear()
        
        # 扫描模组文件和备份文件
        zip_files = list(self.mods_path.glob("*.zip"))
        backup_files = list(self.mods_path.glob("*.zip.backup"))
        all_files = zip_files + backup_files
        
        if not all_files:
            self.status_var.set("未找到任何zip模组文件或备份文件")
            return
        
        for i, file_path in enumerate(all_files):
            self.status_var.set(f"扫描进度: {i+1}/{len(all_files)}")
            self.root.update()
            
            try:
                is_backup = str(file_path).endswith('.backup')
                
                if is_backup:
                    # 备份文件的处理
                    size_str = self.format_file_size(file_path.stat().st_size)
                    file_stem = file_path.name.replace('.zip.backup', '')
                    
                    # 备份文件不分析语言，直接添加
                    item_id = self.mod_tree.insert('', 'end', 
                                                 text=f"[备份] {file_stem}",
                                                 values=(size_str, "备份文件"))
                    
                    # 存储备份文件信息
                    self.mods_data[str(file_path)] = {
                        'name': file_stem,
                        'is_backup': True,
                        'languages': [],
                        'has_locale': False
                    }
                    
                    # 设置备份文件的标签样式（如果可能的话）
                    self.mod_tree.set(item_id, 'languages', "备份文件 (双击还原/右键删除)")
                else:
                    # 普通模组文件的处理
                    mod_info = self.analyze_mod(file_path)
                    if mod_info:
                        self.mods_data[str(file_path)] = mod_info
                        
                        # 添加到树视图
                        size_str = self.format_file_size(file_path.stat().st_size)
                        languages_str = ", ".join(mod_info.get('languages', []))
                        if not languages_str:
                            languages_str = "无语言文件"
                        
                        item_id = self.mod_tree.insert('', 'end', 
                                                     text=file_path.stem,
                                                     values=(size_str, languages_str))
                        
                        # 如果没有中文支持，高亮显示
                        if 'zh-CN' not in mod_info.get('languages', []):
                            self.mod_tree.set(item_id, 'languages', languages_str + " (需要汉化)")
            
            except Exception as e:
                print(f"分析文件失败 {file_path.name}: {e}")
        
        # 保存完整的模组数据用于搜索
        self.all_mods_data = self.mods_data.copy()
        
        regular_mods = len([p for p in self.mods_data.values() if not p.get('is_backup', False)])
        backup_count = len([p for p in self.mods_data.values() if p.get('is_backup', False)])
        self.status_var.set(f"扫描完成，找到 {regular_mods} 个模组，{backup_count} 个备份文件")
    
    def analyze_mod(self, zip_path: Path) -> Optional[Dict]:
        """分析模组信息"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # 查找info.json
                info_json = None
                for file_info in zf.filelist:
                    if file_info.filename.endswith('/info.json') or file_info.filename == 'info.json':
                        info_json = file_info.filename
                        break
                
                mod_info = {'languages': [], 'has_locale': False, 'name': zip_path.stem}
                
                if info_json:
                    try:
                        info_content = zf.read(info_json).decode('utf-8', errors='ignore')
                        info_data = json.loads(info_content)
                        mod_info['name'] = info_data.get('name', zip_path.stem)
                        mod_info['version'] = info_data.get('version', 'unknown')
                        mod_info['title'] = info_data.get('title', mod_info['name'])
                    except Exception as e:
                        print(f"解析info.json失败: {e}")
                        mod_info['name'] = zip_path.stem
                        mod_info['version'] = 'unknown'
                        mod_info['title'] = zip_path.stem
                
                # 查找locale目录
                languages = set()
                for file_info in zf.filelist:
                    filename = file_info.filename
                    if '/locale/' in filename and not file_info.is_dir():
                        # 例如: mod_name_1.0.0/locale/en/strings.cfg
                        parts = filename.split('/locale/')
                        if len(parts) > 1:
                            lang_parts = parts[1].split('/')
                            if len(lang_parts) > 0 and lang_parts[0]:
                                languages.add(lang_parts[0])
                
                if languages:
                    mod_info['has_locale'] = True
                    mod_info['languages'] = sorted(list(languages))
                    print(f"找到语言: {mod_info['languages']}")  # 调试信息
                else:
                    print(f"未找到语言文件: {zip_path.name}")  # 调试信息
                
                return mod_info
        
        except Exception as e:
            print(f"无法分析模组 {zip_path}: {e}")
            return None
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def on_mod_select(self, event):
        """模组选择事件"""
        selection = self.mod_tree.selection()
        if selection:
            item = selection[0]
            mod_name = self.mod_tree.item(item, 'text')
            self.status_var.set(f"选中模组: {mod_name} (双击打开编辑器)")
    
    def on_mod_double_click(self, event):
        """模组双击事件"""
        selection = self.mod_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        mod_name = self.mod_tree.item(item, 'text')
        
        # 查找对应的文件
        target_path = None
        target_info = None
        for path, info in self.mods_data.items():
            # 对于备份文件，匹配显示的名称
            if info.get('is_backup'):
                display_name = f"[备份] {info['name']}"
                if display_name == mod_name:
                    target_path = Path(path)
                    target_info = info
                    break
            else:
                # 普通模组文件
                if Path(path).stem == mod_name:
                    target_path = Path(path)
                    target_info = info
                    break
        
        if not target_path or not target_info:
            messagebox.showerror("错误", "找不到对应的文件")
            return
        
        # 如果是备份文件，询问是否还原
        if target_info.get('is_backup'):
            self.handle_backup_restore(target_path, target_info)
        else:
            # 普通模组文件，切换到编辑器界面
            self.current_mod_path = target_path
            self.current_mod_info = target_info
            self.show_editor()
    
    def handle_backup_restore(self, backup_path: Path, backup_info: dict):
        """处理备份文件还原"""
        original_name = backup_info['name']
        original_path = backup_path.parent / f"{original_name}.zip"
        
        # 检查是否存在同名的原文件
        if original_path.exists():
            choice = messagebox.askyesnocancel(
                "还原备份", 
                f"发现同名模组文件：{original_name}.zip\n\n"
                f"是否要用备份文件替换它？\n\n"
                f"选择'是'：替换原文件（原文件将被删除）\n"
                f"选择'否'：取消操作\n"
                f"选择'取消'：取消操作"
            )
            
            if choice is True:  # 用户选择"是"
                try:
                    # 删除原文件
                    original_path.unlink()
                    # 重命名备份文件
                    backup_path.rename(original_path)
                    
                    self.status_var.set(f"已从备份还原: {original_name}")
                    messagebox.showinfo("成功", f"已从备份还原模组：{original_name}")
                    
                    # 重新扫描模组列表并保持搜索状态
                    search_text = self.search_var.get().strip()
                    self.scan_mods()
                    if search_text:
                        self.search_var.set(search_text)  # 这会触发搜索
                    
                except Exception as e:
                    messagebox.showerror("错误", f"还原失败: {e}")
        else:
            # 没有同名文件，直接还原
            choice = messagebox.askyesno(
                "还原备份", 
                f"是否要还原备份文件：{original_name}？\n\n"
                f"备份文件将被重命名为：{original_name}.zip"
            )
            
            if choice:
                try:
                    backup_path.rename(original_path)
                    
                    self.status_var.set(f"已还原备份: {original_name}")
                    messagebox.showinfo("成功", f"已还原备份文件：{original_name}")
                    
                    # 重新扫描模组列表并保持搜索状态
                    search_text = self.search_var.get().strip()
                    self.scan_mods()
                    if search_text:
                        self.search_var.set(search_text)  # 这会触发搜索
                    
                except Exception as e:
                    messagebox.showerror("错误", f"还原失败: {e}")
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 确定选中的项目
        item = self.mod_tree.identify_row(event.y)
        if not item:
            return
        
        self.mod_tree.selection_set(item)
        mod_name = self.mod_tree.item(item, 'text')
        
        # 查找对应的文件信息
        target_info = None
        for path, info in self.mods_data.items():
            if info.get('is_backup'):
                display_name = f"[备份] {info['name']}"
                if display_name == mod_name:
                    target_info = info
                    self.context_menu_path = Path(path)
                    break
            else:
                if Path(path).stem == mod_name:
                    target_info = info
                    self.context_menu_path = Path(path)
                    break
        
        if not target_info:
            return
        
        # 创建右键菜单
        context_menu = tk.Menu(self.root, tearoff=0)
        
        if target_info.get('is_backup'):
            # 备份文件的右键菜单
            context_menu.add_command(label="还原备份", command=lambda: self.handle_backup_restore(self.context_menu_path, target_info))
            context_menu.add_separator()
            context_menu.add_command(label="删除备份", command=self.delete_backup_file)
        else:
            # 普通模组文件的右键菜单
            context_menu.add_command(label="编辑模组", command=lambda: self.edit_mod_from_context(self.context_menu_path, target_info))
            context_menu.add_separator()
            context_menu.add_command(label="查看语言详情", command=self.show_language_details)
        
        # 显示菜单
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def delete_backup_file(self):
        """删除备份文件"""
        if not hasattr(self, 'context_menu_path'):
            return
        
        backup_name = self.context_menu_path.name.replace('.zip.backup', '')
        choice = messagebox.askyesno(
            "删除备份", 
            f"确定要删除备份文件：{backup_name} 吗？\n\n此操作无法撤销！"
        )
        
        if choice:
            try:
                self.context_menu_path.unlink()
                self.status_var.set(f"已删除备份: {backup_name}")
                messagebox.showinfo("成功", f"已删除备份文件：{backup_name}")
                
                # 重新扫描模组列表并保持搜索状态
                search_text = self.search_var.get().strip()
                self.scan_mods()
                if search_text:
                    self.search_var.set(search_text)  # 这会触发搜索
                
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {e}")
    
    def edit_mod_from_context(self, mod_path: Path, mod_info: dict):
        """从右键菜单编辑模组"""
        self.current_mod_path = mod_path
        self.current_mod_info = mod_info
        self.show_editor()
    
    def on_search_change(self, *args):
        """搜索框内容改变时调用"""
        search_text = self.search_var.get().strip().lower()
        if search_text:
            self.filter_mods(search_text)
        else:
            self.show_all_mods()
    
    def clear_search(self):
        """清除搜索"""
        self.search_var.set("")
        self.show_all_mods()
    
    def show_all_mods(self):
        """显示所有模组"""
        self.mods_data = self.all_mods_data.copy()
        self.refresh_mod_tree()
    
    def filter_mods(self, search_text):
        """根据搜索文本过滤模组"""
        filtered_data = {}
        
        for path, info in self.all_mods_data.items():
            # 获取显示名称
            if info.get('is_backup'):
                display_name = f"[备份] {info['name']}"
            else:
                display_name = Path(path).stem
            
            # 检查名称是否匹配搜索文本
            mod_title = info.get('title', display_name)
            mod_name = info.get('name', display_name)
            
            if (search_text in display_name.lower() or 
                search_text in mod_title.lower() or 
                search_text in mod_name.lower()):
                filtered_data[path] = info
        
        self.mods_data = filtered_data
        self.refresh_mod_tree()
        
        # 更新状态栏显示搜索结果
        result_count = len(filtered_data)
        total_count = len(self.all_mods_data)
        self.status_var.set(f"搜索结果: {result_count}/{total_count} 项")
    
    def refresh_mod_tree(self):
        """刷新模组树视图"""
        # 清空现有项目
        for item in self.mod_tree.get_children():
            self.mod_tree.delete(item)
        
        # 重新添加过滤后的项目
        for path, info in self.mods_data.items():
            file_path = Path(path)
            
            try:
                is_backup = info.get('is_backup', False)
                
                if is_backup:
                    # 备份文件的处理
                    size_str = self.format_file_size(file_path.stat().st_size)
                    file_stem = info['name']
                    
                    item_id = self.mod_tree.insert('', 'end', 
                                                 text=f"[备份] {file_stem}",
                                                 values=(size_str, "备份文件"))
                    
                    self.mod_tree.set(item_id, 'languages', "备份文件 (双击还原/右键删除)")
                else:
                    # 普通模组文件的处理
                    size_str = self.format_file_size(file_path.stat().st_size)
                    languages_str = ", ".join(info.get('languages', []))
                    if not languages_str:
                        languages_str = "无语言文件"
                    
                    item_id = self.mod_tree.insert('', 'end', 
                                                 text=file_path.stem,
                                                 values=(size_str, languages_str))
                    
                    # 如果没有中文支持，高亮显示
                    if 'zh-CN' not in info.get('languages', []):
                        self.mod_tree.set(item_id, 'languages', languages_str + " (需要汉化)")
            
            except Exception as e:
                print(f"刷新树视图失败 {file_path.name}: {e}")
    
    def show_mod_list(self):
        """显示模组列表"""
        self.editor_frame.grid_remove()
        # 重新显示模组列表框架
        for slave in self.root.grid_slaves():
            for widget in slave.grid_slaves():
                widget_name = str(widget)
                if 'frame' in widget_name and hasattr(widget, 'grid_slaves'):
                    for subwidget in widget.grid_slaves():
                        if isinstance(subwidget, ttk.Treeview):
                            widget.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
                            break
        self.current_view = "list"
        self.status_var.set("模组列表")
    
    def show_editor(self):
        """显示编辑器界面"""
        # 隐藏模组列表框架
        for slave in self.root.grid_slaves():
            for widget in slave.grid_slaves():
                widget_name = str(widget)
                if 'frame' in widget_name and hasattr(widget, 'grid_slaves'):
                    for subwidget in widget.grid_slaves():
                        if isinstance(subwidget, ttk.Treeview):
                            widget.grid_remove()
                            break
        
        # 显示编辑器
        self.editor_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.current_view = "editor"
        
        # 更新界面信息
        self.update_editor_info()
    
    def update_editor_info(self):
        """更新编辑器信息"""
        if not self.current_mod_info:
            return
        
        # 更新模组信息
        self.mod_name_label.config(text=self.current_mod_info.get('title', 'Unknown'))
        self.mod_version_label.config(text=self.current_mod_info.get('version', 'Unknown'))
        
        # 更新源语言选择
        available_languages = self.current_mod_info.get('languages', [])
        print(f"可用语言: {available_languages}")  # 调试信息
        
        if available_languages:
            self.source_lang_combo['values'] = available_languages
            # 优先选择英语，否则选择第一个
            if 'en' in available_languages:
                self.source_lang_combo.set('en')
            else:
                self.source_lang_combo.set(available_languages[0])
        else:
            self.source_lang_combo['values'] = []
            self.source_lang_combo.set('')
            messagebox.showwarning("警告", "该模组没有找到语言文件，可能不支持本地化")
        
        # 更新文件列表
        self.update_file_list()
        
        self.status_var.set(f"编辑模组: {self.current_mod_info.get('title', 'Unknown')}")
    
    def on_source_lang_change(self, event=None):
        """源语言改变事件"""
        self.update_file_list()
    
    def update_file_list(self):
        """更新文件列表"""
        if not self.current_mod_path or not self.source_lang_combo.get():
            self.file_combo['values'] = []
            return
        
        try:
            files = self.get_locale_files(self.current_mod_path, self.source_lang_combo.get())
            self.file_combo['values'] = files
            if files:
                self.file_combo.set(files[0])  # 默认选择第一个文件
        except Exception as e:
            self.status_var.set(f"获取文件列表失败: {e}")
            self.file_combo['values'] = []
    
    def get_locale_files(self, zip_path: Path, language: str) -> List[str]:
        """获取指定语言的locale文件列表"""
        files = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for file_info in zf.filelist:
                    if f'/locale/{language}/' in file_info.filename and file_info.filename.endswith('.cfg'):
                        # 提取文件名
                        filename = file_info.filename.split('/')[-1]
                        files.append(filename)
        except Exception as e:
            print(f"获取locale文件失败: {e}")
        
        return sorted(files)
    
    def on_file_change(self, event=None):
        """文件改变事件"""
        # 可以在这里添加文件改变时的逻辑
        pass
    
    def load_selected_file(self):
        """加载选中的文件"""
        # 检查必要条件
        if not self.current_mod_path:
            messagebox.showwarning("警告", "请先选择一个模组")
            return
        
        if not self.source_lang_combo.get():
            messagebox.showwarning("警告", "请先选择源语言")
            return
            
        if not self.file_combo.get():
            messagebox.showwarning("警告", "请先选择要编辑的文件")
            return
        
        try:
            source_lang = self.source_lang_combo.get()
            filename = self.file_combo.get()
            target_lang = self.target_lang_combo.get()
            
            self.status_var.set("正在加载文件...")
            self.root.update()
            
            # 读取源文件内容
            print(f"正在读取源文件: {source_lang}/{filename}")  # 调试信息
            source_content = self.read_locale_file(self.current_mod_path, source_lang, filename)
            
            # 显示源文件内容
            self.source_text.config(state=tk.NORMAL)
            self.source_text.delete(1.0, tk.END)
            self.source_text.insert(1.0, source_content)
            self.source_text.config(state=tk.DISABLED)
            
            # 处理目标文件内容
            target_content = ""
            
            if self.operation_var.get() == "replace":
                # 尝试读取现有的目标语言文件
                try:
                    print(f"尝试读取现有目标文件: {target_lang}/{filename}")  # 调试信息
                    target_content = self.read_locale_file(self.current_mod_path, target_lang, filename)
                    print("找到现有目标文件")  # 调试信息
                except FileNotFoundError:
                    print("未找到现有目标文件，使用源文件作为模板")  # 调试信息
                    target_content = source_content
                except Exception as e:
                    print(f"读取目标文件出错: {e}")  # 调试信息
                    target_content = source_content
            else:
                # 新建模式，使用源文件内容作为模板
                print("新建模式，使用源文件作为模板")  # 调试信息
                target_content = source_content
            
            # 显示目标文件内容
            self.target_text.delete(1.0, tk.END)
            self.target_text.insert(1.0, target_content)
            
            self.status_var.set(f"已加载文件: {filename} ({source_lang} -> {target_lang})")
            print("文件加载完成")  # 调试信息
            
        except FileNotFoundError as e:
            error_msg = f"文件未找到: {e}"
            print(error_msg)  # 调试信息
            messagebox.showerror("错误", error_msg)
            self.status_var.set("文件加载失败")
        except Exception as e:
            error_msg = f"加载文件失败: {e}"
            print(error_msg)  # 调试信息
            messagebox.showerror("错误", error_msg)
            self.status_var.set("文件加载失败")
    
    def read_locale_file(self, zip_path: Path, language: str, filename: str) -> str:
        """从ZIP文件中读取locale文件内容"""
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for file_info in zf.filelist:
                if f'/locale/{language}/{filename}' in file_info.filename:
                    return zf.read(file_info.filename).decode('utf-8', errors='ignore')
        
        raise FileNotFoundError(f"文件未找到: locale/{language}/{filename}")
    
    def preview_changes(self):
        """预览更改"""
        target_content = self.target_text.get(1.0, tk.END).rstrip()
        
        # 创建预览窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title("预览更改")
        preview_window.geometry("600x400")
        
        # 预览内容
        preview_text = ScrolledText(preview_window, height=20)
        preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        target_lang = self.target_lang_combo.get()
        filename = self.file_combo.get()
        operation = "新建" if self.operation_var.get() == "new" else "替换"
        
        preview_text.insert(tk.END, f"操作: {operation}文件\n")
        preview_text.insert(tk.END, f"目标语言: {target_lang}\n")
        preview_text.insert(tk.END, f"文件名: {filename}\n")
        preview_text.insert(tk.END, "=" * 50 + "\n\n")
        preview_text.insert(tk.END, target_content)
        
        preview_text.config(state=tk.DISABLED)
    
    def save_to_zip(self):
        """保存到ZIP文件"""
        if not self.current_mod_path or not self.target_lang_combo.get() or not self.file_combo.get():
            messagebox.showwarning("警告", "请先加载文件")
            return
        
        target_content = self.target_text.get(1.0, tk.END).rstrip()
        if not target_content:
            messagebox.showwarning("警告", "目标内容为空")
            return
        
        try:
            target_lang = self.target_lang_combo.get()
            filename = self.file_combo.get()
            
            # 确认保存
            operation = "新建" if self.operation_var.get() == "new" else "替换"
            if not messagebox.askyesno("确认", f"确定要{operation}语言文件吗？\n\n语言: {target_lang}\n文件: {filename}"):
                return
            
            # 备份原文件
            backup_path = self.current_mod_path.with_suffix('.zip.backup')
            shutil.copy2(self.current_mod_path, backup_path)
            
            self.status_var.set("正在保存到ZIP文件...")
            self.root.update()
            
            # 修改ZIP文件
            self.modify_zip_file(self.current_mod_path, target_lang, filename, target_content)
            
            # 重新分析模组（更新语言列表）
            new_mod_info = self.analyze_mod(self.current_mod_path)
            if new_mod_info:
                self.mods_data[str(self.current_mod_path)] = new_mod_info
                self.current_mod_info = new_mod_info
                self.update_editor_info()
            
            self.status_var.set("保存成功！")
            messagebox.showinfo("成功", f"语言文件已保存到ZIP中\n\n备份文件: {backup_path.name}")
            
            # 保存成功后返回模组列表
            self.show_mod_list()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def modify_zip_file(self, zip_path: Path, target_lang: str, filename: str, content: str):
        """修改ZIP文件中的语言文件"""
        import tempfile
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_path = Path(temp_file.name)
        
        try:
            # 复制原ZIP内容到新ZIP，同时添加或替换目标文件
            with zipfile.ZipFile(zip_path, 'r') as source_zip:
                with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as target_zip:
                    
                    # 查找模组根目录
                    mod_root = ""
                    for file_info in source_zip.filelist:
                        if file_info.filename.endswith('/info.json'):
                            mod_root = file_info.filename.replace('/info.json', '')
                            break
                        elif file_info.filename == 'info.json':
                            mod_root = ""
                            break
                    
                    target_file_path = f"{mod_root}/locale/{target_lang}/{filename}".lstrip('/')
                    
                    # 复制所有文件，跳过要替换的文件
                    for file_info in source_zip.filelist:
                        if file_info.filename != target_file_path:
                            target_zip.writestr(file_info, source_zip.read(file_info.filename))
                    
                    # 添加新的语言文件
                    target_zip.writestr(target_file_path, content.encode('utf-8'))
            
            # 替换原文件
            shutil.move(temp_path, zip_path)
            
        except Exception as e:
            # 清理临时文件
            if temp_path.exists():
                temp_path.unlink()
            raise e
    

    
    def show_language_details(self):
        """显示语言详情"""
        selection = self.mod_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个模组")
            return
        
        item = selection[0]
        mod_name = self.mod_tree.item(item, 'text')
        
        # 查找模组信息
        mod_info = None
        for path, info in self.mods_data.items():
            if Path(path).stem == mod_name:
                mod_info = info
                break
        
        if not mod_info:
            messagebox.showerror("错误", "找不到模组信息")
            return
        
        # 创建详情窗口
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"语言详情 - {mod_name}")
        detail_window.geometry("500x400")
        
        # 模组信息
        info_frame = ttk.LabelFrame(detail_window, text="模组信息", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"名称: {mod_info.get('title', mod_name)}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"版本: {mod_info.get('version', 'unknown')}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"是否有语言文件: {'是' if mod_info.get('has_locale') else '否'}").pack(anchor=tk.W)
        
        # 语言支持情况
        lang_frame = ttk.LabelFrame(detail_window, text="语言支持情况", padding="10")
        lang_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建文本框显示语言详情
        text_widget = ScrolledText(lang_frame, height=15)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 显示语言信息
        current_languages = mod_info.get('languages', [])
        
        text_widget.insert(tk.END, "当前支持的语言:\n")
        text_widget.insert(tk.END, "=" * 30 + "\n")
        
        if current_languages:
            for lang in current_languages:
                lang_name = self.supported_languages.get(lang, lang)
                text_widget.insert(tk.END, f"✓ {lang} - {lang_name}\n")
        else:
            text_widget.insert(tk.END, "无语言文件\n")
        
        text_widget.insert(tk.END, "\n缺失的重要语言:\n")
        text_widget.insert(tk.END, "=" * 30 + "\n")
        
        important_languages = ['zh-CN', 'zh-TW', 'en', 'ja', 'ko', 'ru']
        missing_languages = [lang for lang in important_languages if lang not in current_languages]
        
        if missing_languages:
            for lang in missing_languages:
                lang_name = self.supported_languages.get(lang, lang)
                if lang.startswith('zh'):
                    text_widget.insert(tk.END, f"✗ {lang} - {lang_name} (建议添加)\n")
                else:
                    text_widget.insert(tk.END, f"✗ {lang} - {lang_name}\n")
        else:
            text_widget.insert(tk.END, "所有重要语言都已支持\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def open_cache_directory(self):
        """打开缓存目录"""
        os.startfile(self.cache_dir)
    
    def clear_cache(self):
        """清理缓存"""
        if messagebox.askyesno("确认", "确定要清理所有缓存文件吗？"):
            try:
                if self.cache_dir.exists():
                    shutil.rmtree(self.cache_dir)
                    self.cache_dir.mkdir(exist_ok=True)
                self.status_var.set("缓存已清理")
                messagebox.showinfo("成功", "缓存已清理完毕")
            except Exception as e:
                messagebox.showerror("错误", f"清理缓存失败: {e}")
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    export_path = config.get('export_path', str(Path.home() / "Desktop" / "factorio_exports"))
                    if hasattr(self, 'export_path_var'):
                        self.export_path_var.set(export_path)
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置文件"""
        try:
            config = {
                'export_path': self.export_path_var.get() if hasattr(self, 'export_path_var') else str(Path.home() / "Desktop" / "factorio_exports")
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def browse_export_path(self):
        """浏览导出路径"""
        directory = filedialog.askdirectory(initialdir=self.export_path_var.get())
        if directory:
            self.export_path_var.set(directory)
    
    def set_default_export_path(self):
        """设置默认导出路径"""
        self.save_config()
        messagebox.showinfo("成功", "默认导出路径已保存")
    
    def export_source_file(self):
        """导出源文件"""
        if not self.current_mod_path or not self.source_lang_combo.get() or not self.file_combo.get():
            messagebox.showwarning("警告", "请先加载文件")
            return
        
        try:
            source_lang = self.source_lang_combo.get()
            filename = self.file_combo.get()
            
            # 读取源文件内容
            content = self.read_locale_file(self.current_mod_path, source_lang, filename)
            
            # 确保导出目录存在
            export_dir = Path(self.export_path_var.get())
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成导出文件名
            mod_name = self.current_mod_info.get('name', 'unknown')
            export_filename = f"{mod_name}_{source_lang}_{filename}"
            export_path = export_dir / export_filename
            
            # 保存文件
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.status_var.set(f"源文件已导出: {export_path}")
            messagebox.showinfo("成功", f"源文件已导出到:\n{export_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")
    
    def export_target_file(self):
        """导出目标文件（编辑器中的内容）"""
        target_content = self.target_text.get(1.0, tk.END).rstrip()
        if not target_content:
            messagebox.showwarning("警告", "目标内容为空")
            return
        
        try:
            target_lang = self.target_lang_combo.get()
            filename = self.file_combo.get()
            
            # 确保导出目录存在
            export_dir = Path(self.export_path_var.get())
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成导出文件名
            mod_name = self.current_mod_info.get('name', 'unknown')
            export_filename = f"{mod_name}_{target_lang}_{filename}"
            export_path = export_dir / export_filename
            
            # 保存文件
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(target_content)
            
            self.status_var.set(f"目标文件已导出: {export_path}")
            messagebox.showinfo("成功", f"目标文件已导出到:\n{export_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")
    
    def import_local_file(self):
        """从本地导入文件"""
        file_path = filedialog.askopenfilename(
            title="选择要导入的文件",
            filetypes=[
                ("配置文件", "*.cfg"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ],
            initialdir=self.export_path_var.get()
        )
        
        if not file_path:
            return
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 显示在目标文本框中
            self.target_text.delete(1.0, tk.END)
            self.target_text.insert(1.0, content)
            
            self.status_var.set(f"已导入文件: {Path(file_path).name}")
            messagebox.showinfo("成功", f"文件已导入:\n{Path(file_path).name}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {e}")
    
    def run(self):
        """运行程序"""
        # 启动时自动扫描
        self.root.after(100, self.scan_mods)
        self.root.mainloop()
        # 程序退出时保存配置
        self.save_config()

if __name__ == "__main__":
    app = FactorioModLocalizer()
    app.run()