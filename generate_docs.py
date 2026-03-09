import os
import re
import json
from datetime import datetime
import pandas as pd

class DocGenerator:
    def __init__(self, project_root):
        """初始化文档生成器"""
        self.project_root = project_root
        self.doc_content = ""
        self.html_content = ""
        self.version = "3.5.0"
        self.company = "广东何氏模具有限公司"
        self.product_name = "财务数据小能手"
        # 配置样式变量
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.accent_color = "#e74c3c"
        self.light_bg = "#f8f9fa"
        self.code_bg = "#559ee7"
        self.text_color = "#4C85D4"
        
    def read_file_content(self, file_path):
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败 {file_path}: {str(e)}")
            return ""
    
    def extract_commands(self, package_json_content):
        """从package.json提取命令"""
        try:
            package_data = json.loads(package_json_content)
            return package_data.get('scripts', {})
        except Exception as e:
            print(f"解析package.json失败: {str(e)}")
            return {}
    
    def extract_dependencies(self, requirements_content):
        """从requirements.txt提取依赖"""
        dependencies = []
        for line in requirements_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                dependencies.append(line)
        return dependencies
    
    def generate_file_structure(self):
        """生成文件结构说明"""
        structure = """
HS3.5/
├── icons/                  # 图标文件夹
├── python/   
|   ├──dist
|   |   ├──cat_errer.exe        # 错误检查工具
|   |   ├──工作流json信息.exe    # JSON配置生成工具
|   |   └──one_HsZZexcel_end.exe # 核心数据处理工具  
│   ├── one_HsZZexcel_end.py    # 核心处理脚本
│   ├── cat_errer.py            # 错误检查脚本
│   ├── 工作流json信息.py        # JSON配置生成脚本
│   └── requirements.txt        # Python依赖清单
├── src/                        # Electron源码
│   ├── main.js                 # 主进程
│   ├── preload.js              # 预加载脚本
│   └── renderer.js             # 渲染进程
├── index.html                  # 主页面
├── package.json                # 项目配置
└── README.md                   # 说明文档
        """
        return structure.strip()
    
    def build_markdown_document(self):
        """构建Markdown文档内容"""
        # 读取关键文件内容
        package_json_content = self.read_file_content(
            os.path.join(self.project_root, 'package.json'))
        requirements_content = self.read_file_content(
            os.path.join(self.project_root, 'python', 'requirements.txt'))
        
        # 提取信息
        scripts = self.extract_commands(package_json_content)
        dependencies = self.extract_dependencies(requirements_content)
        file_structure = self.generate_file_structure()
        
        # 构建文档
        self.doc_content = f"# {self.product_name} - 操作文档\n\n"
        self.doc_content += f"![Logo](icons/favicon.ico)\n\n"  # 添加Logo
        self.doc_content += f"**版本**: v{self.version} | **生成日期**: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        print(f"生成文档版本: {self.version}, 日期: {datetime.now().strftime('%Y-%m-%d')}")
        # 目录（带样式）
        self.doc_content += "## 📋 目录\n"
        self.doc_content += "- [1. 软件简介](#1-软件简介)\n"
        self.doc_content += "- [2. 安装指南](#2-安装指南)\n"
        self.doc_content += "- [3. 功能说明](#3-功能说明)\n"
        self.doc_content += "- [4. 操作步骤](#4-操作步骤)\n"
        self.doc_content += "- [5. 文件结构](#5-文件结构)\n"
        self.doc_content += "- [6. 开发与打包](#6-开发与打包)\n"
        self.doc_content += "- [7. 常见问题](#7-常见问题)\n"
        self.doc_content += "- [8. 联系方式](#8-联系方式)\n\n"
        
        # 软件简介
        self.doc_content += "## 1. 软件简介\n"
        self.doc_content += f"{self.product_name}是专为{self.company}设计的财务数据处理工具，主要用于自动化处理发票和流水数据，生成标准化的财务报表，提高财务工作效率。\n\n"
        self.doc_content += "### 核心功能:\n"
        self.doc_content += "- ✅ JSON配置生成：创建处理所需的JSON配置文件\n"
        self.doc_content += "- ✅ 数据处理：根据配置文件自动处理发票和流水数据\n"
        self.doc_content += "- ✅ 错误检查：检查数据处理过程中可能出现的错误\n\n"
        
        # 安装指南
        self.doc_content += "## 2. 安装指南\n"
        self.doc_content += "### 2.1 系统要求\n"
        self.doc_content += "| 项目 | 要求 |\n"
        self.doc_content += "|------|------|\n"
        self.doc_content += "| 操作系统 | Windows 7/8/10/11（32位或64位） |\n"
        self.doc_content += "| 最低配置 | 2GB内存，500MB可用磁盘空间 |\n"
        self.doc_content += "| 依赖软件 | Excel（支持.xlsx和.xls格式） |\n\n"
        
        self.doc_content += "### 2.2 安装步骤\n"
        self.doc_content += "1. 下载最新版本的安装包（`财务数据小能手_Setup.exe`）\n"
        self.doc_content += "2. 双击安装包，启动安装程序\n"
        self.doc_content += "3. 在安装向导中，点击\"下一步\"\n"
        self.doc_content += "4. 阅读并同意用户许可协议\n"
        self.doc_content += "5. 选择安装目录（默认路径：`C:\\Program Files\\财务数据小能手`）\n"
        self.doc_content += "6. 点击\"安装\"，等待安装完成\n"
        self.doc_content += "7. 安装完成后，勾选\"运行财务数据小能手\"，点击\"完成\"\n\n"
        
        # 功能说明
        self.doc_content += "## 3. 功能说明\n"
        self.doc_content += "### 3.1 主要功能模块\n"
        self.doc_content += "| 功能 | 说明 | 可执行文件 |\n"
        self.doc_content += "|------|------|------------|\n"
        self.doc_content += "| JSON配置生成 | 创建包含公司信息、文件路径的配置文件 | 工作流json信息.exe |\n"
        self.doc_content += "| 数据处理 | 处理发票和流水数据，生成报表 | one_HsZZexcel_end.exe |\n"
        self.doc_content += "| 错误检查 | 检查文件格式和数据错误 | cat_errer.exe |\n\n"
        
        # 操作步骤（添加流程图说明）
        self.doc_content += "## 4. 操作步骤\n"
        self.doc_content += "> 完整处理流程：生成JSON配置 → 处理财务数据 → 错误检查（可选）\n\n"
        
        self.doc_content += "### 4.1 第一步：生成JSON配置\n"
        self.doc_content += "1. 打开应用，点击\"生成JSON配置\"按钮\n"
        self.doc_content += "2. 选择公司（川源、何氏或源创达）\n"
        self.doc_content += "3. 选择开票文件（支持Excel或PDF格式）\n"
        self.doc_content += "4. 选择流水文件夹\n"
        self.doc_content += "5. 点击\"保存信息\"，系统会自动生成JSON配置文件到`D:/one_json/`目录下\n\n"
        
        self.doc_content += "### 4.2 第二步：处理财务数据\n"
        self.doc_content += "1. 点击\"立即处理\"按钮\n"
        self.doc_content += "2. 系统自动读取JSON配置文件并处理数据\n"
        self.doc_content += "3. 处理完成后，在原文件目录生成带\"_供应商明细表\"后缀的Excel文件\n\n"
        
        self.doc_content += "### 4.3 第三步：错误检查（可选）\n"
        self.doc_content += "1. 点击\"数据处理报错核心工具\"按钮\n"
        self.doc_content += "2. 点击\"刷新JSON列表\"加载配置文件\n"
        self.doc_content += "3. 分别检查开票表格和流水表格格式\n"
        self.doc_content += "4. 根据提示修正错误\n\n"
        
        # 文件结构
        self.doc_content += "## 5. 文件结构\n"
        self.doc_content += "```\n"
        self.doc_content += file_structure + "\n"
        self.doc_content += "```\n\n"
        
        # 开发与打包
        self.doc_content += "## 6. 开发与打包\n"
        self.doc_content += "### 6.1 开发依赖\n"
        self.doc_content += "Python依赖:\n"
        self.doc_content += "```\n"
        self.doc_content += "\n".join(dependencies) + "\n"
        self.doc_content += "```\n\n"
        
        self.doc_content += "### 6.2 打包命令\n"
        self.doc_content += "| 命令 | 说明 |\n"
        self.doc_content += "|------|------|\n"
        for cmd, desc in scripts.items():
            self.doc_content += f"| `npm run {cmd}` | {desc} |\n"
        self.doc_content += "\n"
        
        # 常见问题（添加图标和高亮）
        self.doc_content += "## 7. 常见问题\n"
        self.doc_content += "### ❓ 工具启动失败\n"
        self.doc_content += "- 检查是否有管理员权限\n"
        self.doc_content += "- 确认系统是否满足最低配置要求\n"
        self.doc_content += "- 尝试重新安装应用\n\n"
        
        self.doc_content += "### ❓ 处理文件时提示错误\n"
        self.doc_content += "- 检查输入文件格式是否正确\n"
        self.doc_content += "- 确认文件内容是否包含所需的必要列\n"
        self.doc_content += "- 检查文件是否被其他程序占用\n\n"
        
        self.doc_content += "### ❓ JSON配置文件无法生成\n"
        self.doc_content += "- 确认`D:/one_json/`目录是否存在，如不存在请手动创建\n"
        self.doc_content += "- 检查是否有该目录的写入权限\n\n"
        
        # 联系方式
        self.doc_content += "## 8. 联系方式\n"
        self.doc_content += f"如在使用过程中遇到任何问题，请联系{self.company} IT部\n"
        self.doc_content += "📧 联系邮箱：2787326121@qq.com\n"
        self.doc_content += "📞 联系电话：18072740843\n\n"
        
        self.doc_content += f"© {datetime.now().year} {self.company} 版权所有\n"
    def build_html_document(self):
        """构建美观的HTML文档，包含飞花特效"""
        self.html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>财务数据小能手 - 操作文档</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {{
            --primary: #2e50c3;
            --secondary: #3498db;
            --accent: #e74c3c;
            --light-bg: #f8f9fa;
            --card-bg: #ffffff;
            --text: #333333;
            --text-light: #666666;
            --border: #e1e4e8;
            --code-bg: #f6f8fa;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft YaHei', 'SimHei', Arial, sans-serif;
            line-height: 1.8;
            color: var(--text);
            background-color: var(--light-bg);
            padding: 0;
            margin: 0;
            position: relative;
            overflow-x: hidden;
        }}
        
        /* 飞花特效容器 */
        #flower-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 100;
            overflow: hidden;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 200; /* 确保内容在飞花之上 */
        }}
        
        header {{
            background-color: var(--primary);
            color: white;
            padding: 30px 0;
            margin-bottom: 40px;
            box-shadow: var(--shadow);
        }}
        
        .header-content {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .logo {{
            width: 60px;
            height: 60px;
            border-radius: 8px;
            background-color: white;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .logo img {{
            max-width: 50px;
            max-height: 50px;
        }}
        
        .header-text h1 {{
            font-size: 28px;
            color: white;
            margin-bottom: 5px;
        }}
        
        .header-text .version {{
            opacity: 0.8;
            font-size: 14px;
        }}
        
        .card {{
            background-color: var(--card-bg);
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: var(--shadow);
            transition: transform 0.2s;
        }}
        
        .card:hover {{
            transform: translateY(-3px);
        }}
        
        h1, h2, h3, h4 {{
            color: var(--primary);
            margin-bottom: 20px;
            line-height: 1.3;
        }}
        
        h1 {{
            font-size: 32px;
        }}
        
        h2 {{
            font-size: 24px;
            border-bottom: 2px solid var(--secondary);
            padding-bottom: 10px;
            margin-top: 40px;
        }}
        
        h3 {{
            font-size: 20px;
            margin-top: 30px;
            color: var(--secondary);
        }}
        
        p {{
            margin-bottom: 18px;
        }}
        
        ul, ol {{
            margin-left: 30px;
            margin-bottom: 18px;
        }}
        
        li {{
            margin-bottom: 8px;
        }}
        
        a {{
            color: var(--secondary);
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background-color: var(--light-bg);
            font-weight: bold;
            color: var(--primary);
        }}
        
        tr:hover {{
            background-color: rgba(52, 152, 219, 0.05);
        }}
        
        pre {{
            background-color: var(--code-bg);
            padding: 20px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 20px 0;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            line-height: 1.5;
        }}
        
        .toc {{
            background-color: var(--light-bg);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        
        .toc h2 {{
            margin-top: 0;
            border-bottom: none;
        }}
        
        .toc ul {{
            list-style-type: none;
            margin-left: 0;
        }}
        
        .toc li {{
            margin-bottom: 10px;
        }}
        
        .toc a {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .note {{
            background-color: rgba(52, 152, 219, 0.1);
            border-left: 4px solid var(--secondary);
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 4px 4px 0;
        }}
        
        .warning {{
            background-color: rgba(231, 76, 60, 0.1);
            border-left: 4px solid var(--accent);
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 4px 4px 0;
        }}
        
        .faq-item {{
            margin-bottom: 25px;
        }}
        
        .faq-question {{
            font-weight: bold;
            color: var(--primary);
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        footer {{
            text-align: center;
            padding: 30px 0;
            margin-top: 50px;
            color: var(--text-light);
            border-top: 1px solid var(--border);
        }}

        .step-number {{
            display: inline-block;
            width: 30px;
            height: 30px;
            background-color: var(--secondary);
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            margin-right: 10px;
            font-weight: bold;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .card {{
                padding: 20px;
            }}
            
            h1 {{
                font-size: 26px;
                color: white;
            }}
            
            h2 {{
                font-size: 22px;
            }}
            
            h3 {{
                font-size: 18px;
            }}
            
            th, td {{
                padding: 8px 10px;
            }}
        }}
    </style>
</head>
<body>
    <!-- 飞花特效容器 -->
    <div id="flower-container"></div>

    <header>
        <div class="header-content">
            <div class="logo">
                <img src="../icons/favicon.ico" alt="Logo">
            </div>
            <div class="header-text">
                <h1>财务数据小能手 - 操作文档</h1>
                <div class="version">版本: v{version} | 生成日期: {date}</div>
            </div>
        </div>
    </header>

    <div class="container">
        <!-- 目录 -->
        <div class="card toc">
            <h2><i class="fas fa-list-ul"></i> 目录</h2>
            <ul>
                <li><a href="#intro"><i class="fas fa-info-circle"></i> 1. 软件简介</a></li>
                <li><a href="#installation"><i class="fas fa-download"></i> 2. 安装指南</a></li>
                <li><a href="#features"><i class="fas fa-cogs"></i> 3. 功能说明</a></li>
                <li><a href="#steps"><i class="fas fa-walking"></i> 4. 操作步骤</a></li>
                <li><a href="#structure"><i class="fas fa-folder-tree"></i> 5. 文件结构</a></li>
                <li><a href="#development"><i class="fas fa-code"></i> 6. 开发与打包</a></li>
                <li><a href="#faq"><i class="fas fa-question-circle"></i> 7. 常见问题</a></li>
                <li><a href="#contact"><i class="fas fa-envelope"></i> 8. 联系方式</a></li>
            </ul>
        </div>

        <!-- 软件简介 -->
        <div id="intro" class="card">
            <h2><i class="fas fa-info-circle"></i> 1. 软件简介</h2>
            <p>财务数据小能手是专为广东何氏模具有限公司设计的财务数据处理工具，主要用于自动化处理发票和流水数据，生成标准化的财务报表，提高财务工作效率。</p>
            
            <h3>核心功能:</h3>
            <ul>
                <li><i class="fas fa-check-circle"></i> JSON配置生成：创建处理所需的JSON配置文件</li>
                <li><i class="fas fa-check-circle"></i> 数据处理：根据配置文件自动处理发票和流水数据</li>
                <li><i class="fas fa-check-circle"></i> 错误检查：检查数据处理过程中可能出现的错误</li>
            </ul>
        </div>

        <!-- 安装指南 -->
        <div id="installation" class="card">
            <h2><i class="fas fa-download"></i> 2. 安装指南</h2>
            <h3>2.1 系统要求</h3>
            <table>
                <tr><th>项目</th><th>要求</th></tr>
                <tr><td>操作系统</td><td>Windows 7/8/10/11（32位或64位）</td></tr>
                <tr><td>最低配置</td><td>2GB内存，500MB可用磁盘空间</td></tr>
                <tr><td>依赖软件</td><td>Excel（支持.xlsx和.xls格式）</td></tr>
            </table>
            
            <h3>2.2 安装步骤</h3>
            <ol>
                <li><span class="step-number">1</span>下载最新版本的安装包（<code>财务数据小能手_Setup.exe</code>）</li>
                <li><span class="step-number">2</span>双击安装包，启动安装程序</li>
                <li><span class="step-number">3</span>在安装向导中，点击"下一步"</li>
                <li><span class="step-number">4</span>阅读并同意用户许可协议</li>
                <li><span class="step-number">5</span>选择安装目录（默认路径：<code>C:\Program Files\财务数据小能手</code>）</li>
                <li><span class="step-number">6</span>点击"安装"，等待安装完成</li>
                <li><span class="step-number">7</span>安装完成后，勾选"运行财务数据小能手"，点击"完成"</li>
            </ol>
        </div>

        <!-- 功能说明 -->
        <div id="features" class="card">
            <h2><i class="fas fa-cogs"></i> 3. 功能说明</h2>
            <h3>3.1 主要功能模块</h3>
            <table>
                <tr><th>功能</th><th>说明</th><th>可执行文件</th></tr>
                <tr><td>JSON配置生成</td><td>创建包含公司信息、文件路径的配置文件</td><td>工作流json信息.exe</td></tr>
                <tr><td>数据处理</td><td>处理发票和流水数据，生成报表</td><td>one_HsZZexcel_end.exe</td></tr>
                <tr><td>错误检查</td><td>检查文件格式和数据错误</td><td>cat_errer.exe</td></tr>
            </table>
        </div>

        <!-- 操作步骤 -->
        <div id="steps" class="card">
            <h2><i class="fas fa-walking"></i> 4. 操作步骤</h2>
            <div class="note">
                <strong>完整处理流程：</strong>生成JSON配置 → 处理财务数据 → 错误检查（可选）
            </div>
            
            <h3>4.1 第一步：生成JSON配置</h3>
            <ol>
                <li>打开应用，点击"生成JSON配置"按钮</li>
                <li>选择公司（川源、何氏或源创达）</li>
                <li>选择开票文件（支持Excel或PDF格式）</li>
                <li>选择流水文件夹</li>
                <li>点击"保存信息"，系统会自动生成JSON配置文件到<code>D:/one_json/</code>目录下</li>
            </ol>
            
            <h3>4.2 第二步：处理财务数据</h3>
            <ol>
                <li>点击"立即处理"按钮</li>
                <li>系统自动读取JSON配置文件并处理数据</li>
                <li>处理完成后，在原文件目录生成带"_供应商明细表"后缀的Excel文件</li>
            </ol>
            
            <h3>4.3 第三步：错误检查（可选）</h3>
            <ol>
                <li>点击"数据处理报错核心工具"按钮</li>
                <li>点击"刷新JSON列表"加载配置文件</li>
                <li>分别检查开票表格和流水表格格式</li>
                <li>根据提示修正错误</li>
            </ol>
        </div>

        <!-- 文件结构 -->
        <div id="structure" class="card">
            <h2><i class="fas fa-folder-tree"></i> 5. 文件结构</h2>
            <pre>{file_structure}</pre>
        </div>

        <!-- 开发与打包 -->
        <div id="development" class="card">
            <h2><i class="fas fa-code"></i> 6. 开发与打包</h2>
            <h3>6.1 开发依赖</h3>
            <p>Python依赖:</p>
            <pre>{dependencies}</pre>
            
            <h3>6.2 打包命令</h3>
            <table>
                <tr><th>命令</th><th>说明</th></tr>
                {scripts_table}
            </table>
        </div>

        <!-- 常见问题 -->
        <div id="faq" class="card">
            <h2><i class="fas fa-question-circle"></i> 7. 常见问题</h2>
            
            <div class="faq-item">
                <div class="faq-question"><i class="fas fa-exclamation-circle"></i> 工具启动失败</div>
                <ul>
                    <li>检查是否有管理员权限</li>
                    <li>确认系统是否满足最低配置要求</li>
                    <li>尝试重新安装应用</li>
                </ul>
            </div>
            
            <div class="faq-item">
                <div class="faq-question"><i class="fas fa-exclamation-circle"></i> 处理文件时提示错误</div>
                <ul>
                    <li>检查输入文件格式是否正确</li>
                    <li>确认文件内容是否包含所需的必要列</li>
                    <li>检查文件是否被其他程序占用</li>
                </ul>
            </div>
            
            <div class="faq-item">
                <div class="faq-question"><i class="fas fa-exclamation-circle"></i> JSON配置文件无法生成</div>
                <ul>
                    <li>确认<code>D:/one_json/</code>目录是否存在，如不存在请手动创建</li>
                    <li>检查是否有该目录的写入权限</li>
                </ul>
            </div>
        </div>

        <!-- 联系方式 -->
        <div id="contact" class="card">
            <h2><i class="fas fa-envelope"></i> 8. 联系方式</h2>
            <p>如在使用过程中遇到任何问题，请联系广东何氏模具有限公司 IT部</p>
            <p><i class="fas fa-envelope"></i> 联系邮箱：2787326121@qq.com</p>
            <p><i class="fas fa-phone"></i> 联系电话：18072740843</p>
        </div>

        <footer>
            © {year} 广东何氏模具有限公司 版权所有
        </footer>
    </div>

    <script>
        // 飞花特效实现
        (function() {{
            const container = document.getElementById('flower-container');
            
            // 设置容器尺寸为窗口大小
            function resizeContainer() {{
                container.style.width = `${{window.innerWidth}}px`;
                container.style.height = `${{window.innerHeight}}px`;
            }}
            
            resizeContainer();
            window.addEventListener('resize', resizeContainer);
            
            // 花瓣图案和颜色
            const petals = ['❀', '✿', '❁', '🌼', '🌸', '💮'];
            const colors = ['#FF69B4', '#FFD700', '#9370DB', '#3CB371', '#1E90FF', '#FF6347'];
            const petalCount = 180; // 花瓣数量
            
            // 创建花瓣元素
            function createPetal() {{
                const petal = document.createElement('div');
                
                // 随机选择花瓣图案和颜色
                petal.textContent = petals[Math.floor(Math.random() * petals.length)];
                petal.style.color = colors[Math.floor(Math.random() * colors.length)];
                
                // 随机大小、位置和动画
                const size = Math.random() * 20 + 10; // 10-30px
                petal.style.fontSize = `${{size}}px`;
                petal.style.position = 'absolute';
                petal.style.top = `-${{size}}px`; // 从顶部外开始
                petal.style.left = `${{Math.random() * 100}}%`;
                petal.style.opacity = Math.random() * 0.7 + 0.3; // 0.3-1.0
                petal.style.animation = `
                    fall ${{Math.random() * 10 + 10}}s linear infinite,
                    sway ${{Math.random() * 3 + 2}}s ease-in-out infinite alternate
                `;
                petal.style.transform = `rotate(${{Math.random() * 360}}deg)`;
                petal.style.animationDelay = `${{Math.random() * 10}}s`;
                
                container.appendChild(petal);
                
                // 花瓣移除（动画结束后）
                setTimeout(() => {{
                    petal.remove();
                }}, 2000000);
            }}
            
            // 创建花瓣样式
            const style = document.createElement('style');
            style.textContent = `
                 @keyframes fall {{
                    0% {{
                        transform: translateY(0) rotate(0deg) translateX(-50px) rotate(0deg);
                    }}
                    20% {{
                        transform: translateY(${{0.2 * window.innerHeight}}px) rotate(0.2 * 360deg) translateX(50px) rotate(${{(Math.random() * 40) - 20}}deg);
                    }}
                    40% {{
                        transform: translateY(${{0.4 * window.innerHeight}}px) rotate(0.4 * 360deg) translateX(50px) rotate(${{(Math.random() * 40) - 20}}deg);
                    }}
                    60% {{
                        transform: translateY(${{0.6 * window.innerHeight}}px) rotate(0.6 * 360deg) translateX(50px) rotate(${{(Math.random() * 40) - 20}}deg);
                    }}
                    80% {{
                        transform: translateY(${{0.8 * window.innerHeight}}px) rotate(0.8 * 360deg) translateX(50px) rotate(${{(Math.random() * 40) - 20}}deg);
                    }}
                    100% {{
                        transform: translateY(${{window.innerHeight}}px) rotate(360deg) translateX(50px) rotate(${{(Math.random() * 40) - 20}}deg);
                    }}
                }}
            `;
            document.head.appendChild(style);
            
            // 初始创建花瓣
            for (let i = 0; i < petalCount; i++) {{
                createPetal();
            }}
            
            // 定时补充花瓣
            setInterval(createPetal, 1000);
        }})();
    </script>
</body>
</html>"""   
            
        # 替换占位符
        package_json_content = self.read_file_content(
            os.path.join(self.project_root, 'package.json'))
        requirements_content = self.read_file_content(
            os.path.join(self.project_root, 'python', 'requirements.txt'))
        
        scripts = self.extract_commands(package_json_content)
        dependencies = self.extract_dependencies(requirements_content)
        file_structure = self.generate_file_structure()
        
        # 构建脚本表格
        scripts_table = ""
        for cmd, desc in scripts.items():
            scripts_table += f"<tr><td><code>npm run {cmd}</code></td><td>{desc}</td></tr>\n"
        
        # 替换变量
        self.html_content = self.html_content.format(
            version=self.version,
            date=datetime.now().strftime('%Y-%m-%d'),
            file_structure=file_structure,
            dependencies="\n".join(dependencies),
            scripts_table=scripts_table,
            year=datetime.now().year
        )
   
    def save_document(self, output_path="操作文档.md"):
        """保存文档"""
        project_docs = "./md-docs"
        md_path = os.path.join(project_docs, output_path)
        # 保存Markdown版本
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self.doc_content)
        print(f"操作文档已生成：{os.path.abspath(md_path)}")
        
        # 保存HTML版本
        html_path = output_path.replace('.md', '.html')
        html_path = os.path.join(project_docs, html_path)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(self.html_content)
        print(f"HTML版本文档已生成：{os.path.abspath(html_path)}")

if __name__ == "__main__":
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 创建文档生成器并生成文档
    doc_gen = DocGenerator(project_root)
    doc_gen.build_markdown_document()
    doc_gen.build_html_document()
    doc_gen.save_document()