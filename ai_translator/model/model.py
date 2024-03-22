from book import ContentType

class Model:
    def make_text_prompt(self, text: str, target_language: str) -> str:
        return f"你是一个语言翻译专家，擅长多国语言翻译，你的目标是仔细阅读输入文字，然后把输入的文字全部翻译为{target_language}，记住是全部翻译为{target_language}，并保持文本结构不变。将翻译结果按原文本格式呈现:{text}"

    def make_table_prompt(self, table: str, target_language: str) -> str:
        return f"你是一个语言翻译专家，支持多国语言翻译，你的目标是仔细阅读表格内容，然后把表格内容全部翻译为{target_language}，记住是全部翻译为{target_language}，并保持表格结构不变。将翻译结果按原表格格式呈现:\n{table}"

    def translate_prompt(self, content, target_language: str) -> str:
        if content.content_type == ContentType.TEXT:
            return self.make_text_prompt(content.original, target_language)
        elif content.content_type == ContentType.TABLE:
            return self.make_table_prompt(content.get_original_as_str(), target_language)

    def make_request(self, prompt):
        raise NotImplementedError("子类必须实现 make_request 方法")



