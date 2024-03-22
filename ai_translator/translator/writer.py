import os
from reportlab.platypus import Image #增加Image模块导入
from reportlab.lib import colors, pagesizes, units
from reportlab.lib.units import inch #增加inch单位导入
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

from book import Book, ContentType
from utils import LOG

class Writer:
    def __init__(self):
        pass

    def save_translated_book(self, book: Book, output_file_path: str = None, file_format: str = "PDF"):
        if file_format.lower() == "pdf":
            output_file_path = self._save_translated_book_pdf(book, output_file_path)
        elif file_format.lower() == "markdown":
            output_file_path = self._save_translated_book_markdown(book, output_file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
        
        return output_file_path  # 为api.py增加返回值

    def _save_translated_book_pdf(self, book: Book, output_file_path: str = None):
        if output_file_path is None:
            output_file_path = book.pdf_file_path.replace('.pdf', f'_translated.pdf')

        LOG.info(f"pdf_file_path: {book.pdf_file_path}")
        LOG.info(f"开始翻译: {output_file_path}")

        # Register Chinese font
        font_path = "../fonts/simsun.ttc"  # 请将此路径替换为您的字体文件路径
        pdfmetrics.registerFont(TTFont("SimSun", font_path))

        # Create a new ParagraphStyle with the SimSun font
        simsun_style = ParagraphStyle('SimSun', fontName='SimSun', fontSize=12, leading=14)

        # Create a PDF document
        from reportlab.lib.pagesizes import A4 # 导入A4页面大小
        doc = SimpleDocTemplate(output_file_path, pagesize=pagesizes.A4)
        styles = getSampleStyleSheet()
        story = []

        # Define maximum image size based on the document's page size and margins
        max_image_width = doc.width
        max_image_height = doc.height
                            
        # Iterate over the pages and contents
        for page in book.pages:
            for content in page.contents:
                if content.status:
                    if content.content_type == ContentType.TEXT:
                        # Add translated text to the PDF
                        text = content.translation
                        para = Paragraph(text, simsun_style)
                        story.append(para)

                    elif content.content_type == ContentType.TABLE:
                        # Add table to the PDF
                        table = content.translation

                        if table.empty:
                            # 处理空表格的情况，例如跳过或添加一个占位符
                            LOG.warning(f"空的表格在PDF中被忽略: {content}")
                            continue
                        
                        # 假设 'table' 是一个DataFrame
                        table_data = table.values.tolist()
                        if not table_data or not isinstance(table_data[0], (list, tuple)):
                           # 如果 'table_data' 是空的或不是二维列表
                           LOG.error("表格数据不是有效的二维列表格式。")
                           continue  # 或者其他错误处理

                        table_style = TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'SimSun'),  # 更改表头字体为 "SimSun"
                            ('FONTSIZE', (0, 0), (-1, 0), 14),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('FONTNAME', (0, 1), (-1, -1), 'SimSun'),  # 更改表格中的字体为 "SimSun"
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ])
                        pdf_table = Table(table.values.tolist())
                        pdf_table.setStyle(table_style)
                        story.append(pdf_table)
                    
                    # 【新增】图像类型判断     
                    elif content.content_type == ContentType.IMAGE:
                        image_path = content.original
                        if os.path.isfile(image_path):
                            img = Image(image_path)

                            # 获取图片原始大小
                            img_width, img_height = img.drawWidth, img.drawHeight
                            aspect_ratio = img_height / img_width

                            # 调整图片大小以适应最大尺寸
                            if img_width > max_image_width or img_height > max_image_height:
                                if (max_image_width / img_width) < (max_image_height / img_height):
                                    img_width = max_image_width
                                    img_height = img_width * aspect_ratio
                                else:
                                    img_height = max_image_height
                                    img_width = img_height / aspect_ratio

                            img.drawWidth = img_width
                            img.drawHeight = img_height

                            story.append(img)
                            LOG.info(f"Image added to story: {image_path}")
                        else:
                            LOG.error(f"Image file not found: {image_path}")

            # Add a page break after each page except the last one
            if page != book.pages[-1]:
                story.append(PageBreak())

        # Save the translated book as a new PDF file
        doc.build(story)
        LOG.info(f"翻译完成: {output_file_path}")
        return output_file_path # 为api.py增加返回值

    def _save_translated_book_markdown(self, book: Book, output_file_path: str = None):
        if output_file_path is None:
            output_file_path = book.pdf_file_path.replace('.pdf', f'_translated.md')

        LOG.info(f"pdf_file_path: {book.pdf_file_path}")
        LOG.info(f"开始翻译: {output_file_path}")
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            # Iterate over the pages and contents
            for page in book.pages:
                for content in page.contents:
                    if content.status:
                        if content.content_type == ContentType.TEXT:
                            # Add translated text to the Markdown file
                            text = content.translation
                            output_file.write(text + '\n\n')

                        elif content.content_type == ContentType.TABLE:
                            # Add table to the Markdown file
                            table = content.translation
                            header = '| ' + ' | '.join(str(column) for column in table.columns) + ' |' + '\n'
                            separator = '| ' + ' | '.join(['---'] * len(table.columns)) + ' |' + '\n'
                            body = '\n'.join(['| ' + ' | '.join(str(cell) for cell in row) + ' |' for row in table.values.tolist()]) + '\n\n'
                            output_file.write(header + separator + body)

                        # 【新增】图像类型判断   
                        elif content.content_type == ContentType.IMAGE:
                            # Add image to the Markdown file
                            image_path = content.original  # 使用Content对象的original属性作为图像文件路径
                            if os.path.isfile(image_path):
                               
                                # markdown文件路径定义
                                markdown_file_path = output_file_path

                                # 判断图片文件路径，如果路径是相对于Markdown文件的，确保这里使用正确的相对路径
                                relative_image_path = os.path.relpath(image_path, os.path.dirname(markdown_file_path))
                                
                                image_markdown = f"![Image]({relative_image_path})\n\n"
                                output_file.write(image_markdown) 
                                LOG.info(f"Image link added to Markdown file: {relative_image_path}")
                            else:
                                LOG.error(f"Image file not found: {image_path}")


                # Add a page break (horizontal rule) after each page except the last one
                if page != book.pages[-1]:
                    output_file.write('---\n\n')

        LOG.info(f"翻译完成: {output_file_path}")
        
        return output_file_path # 为api.py增加返回值