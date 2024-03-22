from flask import Flask, request, send_file, send_from_directory,jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
import logging
import traceback

from model import GLMModel, OpenAIModel
from translator import PDFTranslator
from utils import ArgumentParser, ConfigLoader, LOG

# 初始化 Flask 应用
app = Flask(__name__)

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

#实例化PDFTranslator
argument_parser = ArgumentParser()
args = argument_parser.parse_arguments()
config_loader = ConfigLoader(args.config)
config = config_loader.load_config()

#采用openai的模型
model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']
api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']
model = OpenAIModel(model=model_name, api_key=api_key)
translator = PDFTranslator(model)   
#采用其他模型（省略）

# 应用配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'md'}  # 允许的文件扩展名集合

# 检查 UPLOAD_FOLDER 是否存在，如果不存在，则创建它
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 定义一个函数，用于验证文件扩展名是否在允许的文件扩展名集合中
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 当API接收到一个POST 请求，我们从请求的 JSON 数据中提取 target_language 字段，并验证该语言是否受支持
@app.route('/translate', methods=['POST'])
def translate():
    # 从请求中获取目标语言代码
    data = request.json
    target_language_code = data.get('target_language')  # 假设请求是 JSON 格式，并包含 'target_language' 字段
    if target_language_code in supported_languages:
        target_language = supported_languages[target_language_code]
        # 执行您的翻译代码...
        # 假设这里调用了一个实际的翻译函数并获得了结果
        translation_result = "翻译结果示例"  # 这里应该是调用翻译函数的结果
        return jsonify(
            message="翻译请求已成功处理。",
            target_language=target_language,
            translation=translation_result
        ), 200
    else:
        return jsonify(error="输入的语言代码不受支持。"), 400


@app.route('/translate_pdf', methods=['POST'])
def translate_pdf_route():
    """处理 PDF 翻译请求的路由."""
    file = request.files.get('file')
    target_language_code = request.form.get('target_language')
    
    # 验证目标语言是否受支持
    if target_language_code not in supported_languages:
        return jsonify(error="输入的语言代码不受支持。"), 400
    target_language = supported_languages[target_language_code]

    # 验证文件是否存在
    if file is None or file.filename == '':
        return jsonify(message="未提供文件或文件为空"), 400
    
    # 验证文件类型是否允许
    if not allowed_file(file.filename):
        return jsonify(message="不允许的文件类型"), 400
       
    # 处理文件
    try:
        # 确保文件名安全，避免不安全的路径
        filename = secure_filename(file.filename)
        # 将文件保存到 uploads 文件夹
        pdf_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_file_path)

        # 调用翻译函数
        # translate_pdf 只返回翻译后文件的路径
        output_file_path = translator.translate_pdf(
            pdf_file_path=pdf_file_path,
            target_language=target_language,  # 用户选择的目标语言,
            output_file_path=None,
            pages=None
        )

        # 确定正确的文件类型和内容类型
        # 假定 output_file_path 是一个包含文件路径和扩展名的字符串
        if output_file_path.endswith('.pdf'):
            content_type = 'application/pdf'
        elif output_file_path.endswith('.md'):
            content_type = 'text/markdown'
        else:
            raise ValueError("无法识别的文件类型")

        # 返回文件
        directory = os.path.dirname(output_file_path)
        filename = os.path.basename(output_file_path)
        return send_from_directory(directory, filename, as_attachment=True)
  
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"发生错误: {error_trace}")
        # 在调试时返回完整的堆栈跟踪信息给用户（仅在调试环境中建议这么做）
        return jsonify(message=f"发生内部错误: {error_trace}"), 500
       # 生产环境应返回更通用的错误消息
       # return jsonify(message="内部服务器错误，请联系支持。"), 500
    
  

# 以下代码为发生错误的代码，感兴趣可以调试下：

""" from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
import logging
import traceback

from model import GLMModel, OpenAIModel
from translator import PDFTranslator
from utils import ArgumentParser, ConfigLoader, LOG

# 初始化翻译器和Flask应用程序
app = Flask(__name__)

#实例化PDFTranslator
argument_parser = ArgumentParser()
args = argument_parser.parse_arguments()
config_loader = ConfigLoader(args.config)
config = config_loader.load_config()
model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']
api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']
model = OpenAIModel(model=model_name, api_key=api_key)
translator = PDFTranslator(model)   

# 应用程序配置直接设置在脚本中
UPLOAD_FOLDER = 'C:\\Users\\zf\\openai-quickstart\\openai-translator\\uploads'  # Change this to your preferred directory
ALLOWED_EXTENSIONS = {'pdf','md'}  # Set of allowed file extensions

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return "Welcome to the PDF Translation API!"

@app.route('/translate_pdf', methods=['POST'])
def translate_pdf_route():
    file = request.files.get('file')
    if file is None or file.filename == '':
        return jsonify(message="No file provided or file is empty"), 400

    if not allowed_file(file.filename):
        return jsonify(message="File type not allowed"), 400

    try:
        filename = secure_filename(file.filename)
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_file_path = os.path.join(temp_dir, filename)
            file.save(pdf_file_path)

            # 调用翻译函数
            output_file_path = translator.translate_pdf(
                pdf_file_path=pdf_file_path,
                target_language=None,
                output_file_path=None,
                pages=None
            )

            # 假设 output_file_path 是一个字符串，包含了文件路径和扩展名
            if output_file_path.endswith('.pdf'):
                 content_type = 'application/pdf'
            elif output_file_path.endswith('.md'):
                 content_type = 'text/markdown'
            else:
               raise ValueError("无法识别的文件类型")

            # 确定正确的文件类型和内容类型
            output_file = output_file_path

            # 检查文件是否存在
            if not os.path.exists(output_file):
               raise FileNotFoundError("文件未找到: {}".format(output_file))

            # 返回文件
            return send_file(output_file, as_attachment=True, mimetype=content_type)
  
    
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"An error occurred: {error_trace}")
        # 在调试时返回完整的堆栈跟踪信息给用户（仅在调试环境中建议这么做）在生产环境中，你可能想返回更通用的消息，如 "An internal error occurred."
        return jsonify(message=f"An error occurred during file processing: {error_trace}"), 500
 """
