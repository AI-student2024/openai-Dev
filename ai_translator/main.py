# main.py
import tkinter as tk
from tkinter import filedialog, messagebox
from gui import GuiApp
from flask import Flask
from api import app as api_app

import sys
import os

# 确保添加当前文件夹到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ArgumentParser, ConfigLoader, LOG
from model import GLMModel, OpenAIModel
from translator import PDFTranslator

# 定义支持的语言列表
supported_languages = {
    'en': 'English',
    'zh': '中文',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'ja': '日本語',
    'it': 'Italiano',
    'ko': '한국어',
    'ru': 'Русский',
    'pt': 'Português',
    'ar': 'العربية',
    # ...继续添加其他支持的语言...
}

if __name__ == "__main__":
    argument_parser = ArgumentParser()
    args = argument_parser.parse_arguments()
    config_loader = ConfigLoader(args.config)
    config = config_loader.load_config()

    model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']
    api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']
    model = OpenAIModel(model=model_name, api_key=api_key)

    # 根据命令行参数或配置文件来选择启动 GUI 或命令行版本或 API 服务
    if args.gui:
        # 启动 GUI
        app = GuiApp(model, config)
        app.mainloop()
    elif args.api:
        # 启动 Flask API 服务
        api_app.run(debug=True)       
    else:
        # 让用户选择目标语言
        print("请选择目标语言的代码：")
        for code, language in supported_languages.items():
            print(f"{code}: {language}")
        selected_language_code = input("输入语言代码：").strip().lower()

        # 检查用户输入是否在支持的语言列表中
        if selected_language_code in supported_languages:
            target_language = supported_languages[selected_language_code]
        else:
            print("错误：输入的语言代码不受支持。请重新输入。")
            sys.exit(1)  # 或者您可以要求用户重新输入

        # 命令行版本的逻辑
        pdf_file_path = args.book if args.book else config['common']['book']
        file_format = args.file_format if args.file_format else config['common']['file_format']
        translator = PDFTranslator(model)
        translator.translate_pdf(pdf_file_path, target_language,file_format) #传入目标语言
