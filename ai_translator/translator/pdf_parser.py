import pdfplumber
import os
from typing import Optional
from book import Book, Page, Content, ContentType, TableContent
from translator.exceptions import PageOutOfRangeException
from utils import LOG


class PDFParser:
    def __init__(self):
        pass

    def parse_pdf(self, pdf_file_path: str, pages: Optional[int] = None) -> Book:
        book = Book(pdf_file_path)
       
        # 获取PDF文件所在的目录路径
        pdf_dir = os.path.dirname(pdf_file_path)

        # 创建图像保存目录，如果它不存在的话
        images_dir = os.path.join(pdf_dir, 'parserimages')
        if not os.path.isdir(images_dir):
            os.makedirs(images_dir)

        

        with pdfplumber.open(pdf_file_path) as pdf:
            if pages is not None and pages > len(pdf.pages):
                raise PageOutOfRangeException(len(pdf.pages), pages)

            if pages is None:
                pages_to_parse = pdf.pages
            else:
                pages_to_parse = pdf.pages[:pages]

            for pdf_page in pages_to_parse:
                page = Page()

                # Store the original text content
                raw_text = pdf_page.extract_text()
                tables = pdf_page.extract_tables()


                # Remove each cell's content from the original text
                for table_data in tables:
                    for row in table_data:
                        for cell in row:
                            raw_text = raw_text.replace(cell, "", 1)

                # Handling text
                if raw_text:
                    # Remove empty lines and leading/trailing whitespaces
                    raw_text_lines = raw_text.splitlines()
                    cleaned_raw_text_lines = [line.strip() for line in raw_text_lines if line.strip()]
                    cleaned_raw_text = "\n".join(cleaned_raw_text_lines)

                    text_content = Content(content_type=ContentType.TEXT, original=cleaned_raw_text)
                    page.add_content(text_content)
                    LOG.debug(f"[raw_text]\n {cleaned_raw_text}")

                # Handling tables
                if tables:
                    table = TableContent(tables)
                    page.add_content(table)
                    LOG.debug(f"[table]\n{table}")

                # 【新增图片处理过程】Handinging images
                images = pdf_page.images
                if images:
                   for idx, image_details in enumerate(images):
                       
                        # 提取图像的矩形边界
                        x0, top, x1, bottom = image_details["x0"], image_details["top"], image_details["x1"], image_details["bottom"]
                       
                        # 确保坐标值在页面实际尺寸之内
                        x0 = max(0, x0)
                        top = max(0, top)
                        x1 = min(pdf_page.width, x1)
                        bottom = min(pdf_page.height, bottom)
                        cropped_image = pdf_page.within_bbox((x0, top, x1, bottom)).to_image(antialias=True)

                        # 使用pdfplumber的裁剪、抗锯齿及导出功能
                        cropped_image = pdf_page.within_bbox((x0, top, x1, bottom)).to_image(antialias=True)
                        # 构造保存图像的路径，使用PDF文件所在的目录
                        image_filename = f"parserimages/page_{pdf_page.page_number}_image_{idx}.png"
                        # 生成图片url地址，windows中默认是反斜杠'\'
                        image_jionpath = os.path.join(pdf_dir, image_filename)
                        # 替换反斜杠为正斜杠，以便在 Markdown 中使用
                        image_path = image_jionpath.replace('\\', '/')
                        cropped_image.save(image_path, format="PNG")
                        image_content = Content(content_type=ContentType.IMAGE, original=image_path)
                        page.add_content(image_content)
                        LOG.debug(f"[image]\n{image_path}") 

                book.add_page(page)

        return book
