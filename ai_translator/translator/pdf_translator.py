from typing import Optional
from model import Model
from book import ContentType
from translator.pdf_parser import PDFParser
from translator.writer import Writer
from utils import LOG
from PIL import Image as PILImage



class PDFTranslator:
    def __init__(self, model: Model):
        self.model = model
        self.pdf_parser = PDFParser()
        self.writer = Writer()

    def translate_pdf(self, pdf_file_path: str, target_language: str, file_format: str = 'PDF',  output_file_path: str = None, pages: Optional[int] = None):
        self.book = self.pdf_parser.parse_pdf(pdf_file_path, pages)  
        
        for page_idx, page in enumerate(self.book.pages):
            for content_idx, content in enumerate(page.contents):
                
                #只处理文本和表格
                if content.content_type in [ContentType.TEXT, ContentType.TABLE]:       
                   prompt = self.model.translate_prompt(content, target_language)
                   LOG.debug(prompt)
                   translation, status = self.model.make_request(prompt)
                   LOG.info(translation)
                # 更新self.book.pages中的内容
                   content.set_translation(translation, status)
                
                # 如果内容是图像，则跳过翻译步骤  
                elif content.content_type == ContentType.IMAGE: 
                    LOG.info(f"Skipping translation for image content at page {page_idx + 1}, content {content_idx + 1}")
                    with PILImage.open(content.original) as original_image:
                       content.set_translation(original_image, status=True)
                  
        # 保存翻译后的 PDF
        output_file_path = self.writer.save_translated_book(self.book, output_file_path, file_format)
        return output_file_path
    

    def translate_pdf_text(self, pdf_file_path: str, target_language: str, file_format: str = 'PDF',  output_file_path: str = None, pages: Optional[int] = None):
        self.book = self.pdf_parser.parse_pdf(pdf_file_path, pages)  
        translated_text = ''  # 初始化翻译后的文本字符串      

        for page_idx, page in enumerate(self.book.pages):
            for content_idx, content in enumerate(page.contents):
                
                #只处理文本和表格
                if content.content_type in [ContentType.TEXT, ContentType.TABLE]:       
                   prompt = self.model.translate_prompt(content, target_language)
                   LOG.debug(prompt)
                   translation, status = self.model.make_request(prompt)
                   LOG.info(translation)
                # 更新self.book.pages中的内容
                   content.set_translation(translation, status)
                # 将翻译后的文本添加到 translated_text
                   translated_text += translation + '\n'
                
                # 如果内容是图像，则跳过翻译步骤  
                elif content.content_type == ContentType.IMAGE: 
                    LOG.info(f"Skipping translation for image content at page {page_idx + 1}, content {content_idx + 1}")
                    with PILImage.open(content.original) as original_image:
                       content.set_translation(original_image, status=True)
                       # 对于图像内容，这里不做处理
                
        # 只返回翻译后的文本字符串，为gui.py提供翻译后的文本返回。
        return translated_text          
    
        


# 以下代码为初期调试时用，后续可删除
"""         # [GUI新增]收集所有页面的翻译内容
        translated_textsforgui = []
        for page in self.book.pages:
            for content in page.contents:
                translation_string = content.get_translation_as_string()
                translated_textsforgui.append(translation_string)
        # 【GUI新增】将所有翻译的文本合并成一个字符串并返回
        return '\n'.join(translated_textsforgui) """














# 以下是老师原始的代码
""" def translate_pdf(self, pdf_file_path: str, file_format: str = 'PDF', target_language: str = '中文', output_file_path: str = None, pages: Optional[int] = None):
    self.book = self.pdf_parser.parse_pdf(pdf_file_path, pages)

    for page_idx, page in enumerate(self.book.pages):
        for content_idx, content in enumerate(page.contents):
            prompt = self.model.translate_prompt(content, target_language)
            LOG.debug(prompt)
            translation, status = self.model.make_request(prompt)
            LOG.info(translation)
            
            # Update the content in self.book.pages directly
            self.book.pages[page_idx].contents[content_idx].set_translation(translation, status)

    self.writer.save_translated_book(self.book, output_file_path, file_format)

    # [GUI新增]收集所有页面的翻译内容
    translated_textsforgui = []
    for page in self.book.pages:
        for content in page.contents:
            translation_string = content.get_translation_as_string()
            translated_textsforgui.append(translation_string)

    # 【GUI新增】将所有翻译的文本合并成一个字符串并返回
    return '\n'.join(translated_textsforgui) """


