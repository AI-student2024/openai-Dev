import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from utils import ArgumentParser, ConfigLoader
from model import OpenAIModel
from translator import PDFTranslator

# 假设你已经定义了 supported_languages 字典
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

class GuiApp(tk.Tk):
    def __init__(self, model, config):
        super().__init__()
        self.model = model
        self.config = config
        self.translator = PDFTranslator(model)  # 用于翻译 PDF 文件
        self.title('PDF Translator GUI')
        self.geometry('800x600')

        # 创建 GUI 组件
        self.create_widgets()

    def create_widgets(self):
        # 文件选择按钮
        self.open_button = tk.Button(self, text='Open PDF', command=self.open_file)
        self.open_button.pack(pady=10)

        # 文件信息标签
        self.file_info_label = tk.Label(self, text='No file selected.')
        self.file_info_label.pack(pady=5)

        # 语言选择下拉菜单
        self.language_label = tk.Label(self, text='Select target language:')
        self.language_label.pack(pady=5)
        self.language_var = tk.StringVar(self)
        self.language_dropdown = ttk.Combobox(self, textvariable=self.language_var, values=list(supported_languages.values()))
        self.language_dropdown.pack(pady=5)

        # 翻译按钮
        self.translate_button = tk.Button(self, text='Translate', command=self.translate, state=tk.DISABLED)
        self.translate_button.pack(pady=10)

        # 结果显示框
        self.result_text = tk.Text(self, height=25, width=100)
        self.result_text.pack(pady=10)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('PDF Files', '*.pdf')])
        if file_path:
            self.file_path = file_path
            self.translate_button['state'] = tk.NORMAL
            # 更新文件信息标签内容
            self.file_info_label.config(text=f'Selected File: {file_path}')
            # 弹出消息框包含文件名
            messagebox.showinfo('Success', f'PDF file "{file_path.split("/")[-1]}" loaded successfully.')

    def translate(self):
        # 获取语言的友好名称，然后查找对应的代码
        language_friendly_name = self.language_var.get()
        language_code = next((code for code, name in supported_languages.items() if name == language_friendly_name), None)
        if not language_code:
            messagebox.showerror('Error', 'Please select a valid target language.')
            return
        
        try:
            self.result_text.delete(1.0, tk.END)  # 清空文本框
            # 使用 translate_pdf_text 方法获取翻译后的文本
            translated_text = self.translator.translate_pdf_text(self.file_path, language_code)
            self.result_text.insert(tk.END, translated_text)
        except Exception as e:
            messagebox.showerror('Error', str(e))


# 以下代码，实现了翻译为中文的功能。

""" import tkinter as tk
from tkinter import filedialog, messagebox
from utils import ArgumentParser, ConfigLoader
from model import OpenAIModel
from translator import PDFTranslator

class GuiApp(tk.Tk):
    def __init__(self, model, config):
        super().__init__()
        self.model = model
        self.config = config
        self.translator = PDFTranslator(model)
        self.title('PDF Translator GUI')
        self.geometry('600x400')

        # 创建 GUI 组件
        self.create_widgets()

    def create_widgets(self):
        # 文件选择按钮
        self.open_button = tk.Button(self, text='Open PDF', command=self.open_pdf)
        self.open_button.pack(pady=10)

        # 翻译按钮
        self.translate_button = tk.Button(self, text='Translate to Chinese', command=self.translate, state=tk.DISABLED)
        self.translate_button.pack(pady=10)

        # 结果显示框
        self.result_text = tk.Text(self, height=15, width=80)
        self.result_text.pack(pady=10)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[('PDF Files', '*.pdf')])
        if file_path:
            self.pdf_file_path = file_path
            self.translate_button['state'] = tk.NORMAL
            messagebox.showinfo('Success', 'PDF file loaded successfully.')

    def translate(self):
        try:
            self.result_text.delete(1.0, tk.END)  # 清空文本框
            trans_texts = self.translator.translate_pdf(self.pdf_file_path, 'pdf')
            self.result_text.insert(tk.END, trans_texts)
        except Exception as e:           
            messagebox.showerror('Error', str(e))
     """