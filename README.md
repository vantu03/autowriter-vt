# AutoWriter-VT

Công cụ tạo bài viết tiếng Việt bằng AI (OpenAI GPT). Hỗ trợ xuất HTML, JSON chuẩn SEO.

## Cài đặt
```bash
pip install git+https://github.com/vantu03/autowriter-vt.git
````

## Sử dụng

```python
from autowriter import ArticleGenerator

gen = ArticleGenerator(api_key="sk-...")#Chứa API Key của bạn
result = gen.generate_article("Chủ đề cần viết", save_html=True, save_json=True)
```
