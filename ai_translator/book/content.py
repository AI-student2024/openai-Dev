import pandas as pd
from enum import Enum, auto
from PIL import Image as PILImage
from utils import LOG

class ContentType(Enum):
    TEXT = auto()
    TABLE = auto()
    IMAGE = auto()

class Content:
    def __init__(self, content_type, original, translation=None):
        self.content_type = content_type
        self.original = original
        self.translation = translation
        self.status = False

    def set_translation(self, translation, status):
        if not self.check_translation_type(translation):
            raise ValueError(f"Invalid translation type. Expected {self.content_type}, but got {type(translation)}")
        self.translation = translation
        self.status = status

    def check_translation_type(self, translation):
        if self.content_type == ContentType.TEXT and isinstance(translation, str):
            return True
        elif self.content_type == ContentType.TABLE and isinstance(translation, list):
            return True
        elif self.content_type == ContentType.IMAGE and isinstance(translation, PILImage.Image):
           return True
        return False
    
  
    # 【新增GUI】Content类中添加一个新的方法来获取翻译内容的字符串表示
    def get_translation_as_string(self):
        if self.content_type == ContentType.TEXT:
            return self.translation or ""  # 返回翻译的文本或空字符串
        elif self.content_type == ContentType.TABLE:
            return self.translation.to_csv(index=False) if self.translation is not None else ""
        elif self.content_type == ContentType.IMAGE:
            # 处理图片的情况可能会更复杂，这里只是一个示例
            return "[Image content]"  
        else:
            return str(self.translation)  # 通用的转换为字符串的处理
        

class TableContent(Content):
    def __init__(self, data, translation=None):
        df = pd.DataFrame(data)

        # Verify if the number of rows and columns in the data and DataFrame object match
        if len(data) != len(df) or len(data[0]) != len(df.columns):
            raise ValueError("The number of rows and columns in the extracted table data and DataFrame object do not match.")
        
        super().__init__(ContentType.TABLE, df)

    def set_translation(self, translation, status):
        try:
            if not isinstance(translation, str):
                raise ValueError(f"Invalid translation type. Expected str, but got {type(translation)}")
            LOG.debug(translation)
            # Convert the string to a list of lists
            #table_data = [row.strip().split() for row in translation.strip().split('\n')]
            #LOG.debug(table_data)
            # Convert the string to a list of lists
            # 把字符串根据换行符分割为列表，每行是表的一行
            table_rows = translation.strip().split('\n')
            # 分割每行的单元格，使用管道符 "|" 作为分隔符
            table_data = [row.split('|') for row in table_rows]
            # 处理分割后的数据，去除每个单元格的首尾空白
            table_data = [[cell.strip() for cell in row] for row in table_data]
            # 去除空的单元格列表
            table_data = [list(filter(None, row)) for row in table_data]
            # 输出数据检查
            LOG.debug(table_data)

            # Create a DataFrame from the table_data
            translated_df = pd.DataFrame(table_data[1:], columns=table_data[0])           
            LOG.debug(translated_df)
            self.translation = translated_df
            self.status = status
        except Exception as e:
            LOG.error(f"An error occurred during table translation: {e}")
            self.translation = None
            self.status = False

    def __str__(self):
        return self.original.to_string(header=False, index=False)

    def iter_items(self, translated=False):
        target_df = self.translation if translated else self.original
        for row_idx, row in target_df.iterrows():
            for col_idx, item in enumerate(row):
                yield (row_idx, col_idx, item)

    def update_item(self, row_idx, col_idx, new_value, translated=False):
        target_df = self.translation if translated else self.original
    
        target_df.at[row_idx, col_idx] = new_value

    def get_original_as_str(self):
        return self.original.to_string(header=False, index=False)
    

