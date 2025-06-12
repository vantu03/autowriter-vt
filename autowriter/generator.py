from datetime import date
from openai import OpenAI
from bs4 import BeautifulSoup
from slugify import slugify
import json, os

class ArticleGenerator:
    def __init__(self, api_key: str, model="gpt-4.1", temperature=0.3):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def load_prompt(self, filename: str, **replacements) -> str:
        # Đảm bảo luôn đọc file trong thư mục "prompts" của thư viện
        prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
        path = os.path.join(prompts_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        for key, val in replacements.items():
            content = content.replace(f"#{key}", val)
        return content

    def generate_article(self, topic: str, save_html = False, save_json = False) -> dict:
        try:
            # Bước 1: Sinh cấu trúc HTML ban đầu
            print("🔧 creating article structure...")
            structure_prompt = self.load_prompt("structure.txt", topic=topic)

            structure_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": structure_prompt}],
                temperature=self.temperature,
            )
            structure_text = structure_response.choices[0].message.content
            soup = BeautifulSoup(structure_text, "html.parser")

            # Bước 2: Sinh nội dung cho từng thẻ <h2>
            for h2 in soup.find_all("h2"):
                h2_text = h2.get_text(strip=True)
                print(f"📝 creating content for heading: {h2_text}")

                heading_prompt = self.load_prompt(
                    "heading.txt",
                    topic=topic,
                    h2=h2_text,
                    struct=str(soup)
                )

                try:
                    heading_response = self.client.responses.create(
                        model=self.model,
                        input=heading_prompt,
                        tools=[{
                            "type": "web_search_preview",
                            "recency": 365
                        }]
                    )
                    heading_content = heading_response.output_text

                    
                    # Xoá các node placeholder ngay sau <h2>
                    next_node = h2.find_next_sibling()
                    while next_node and (next_node.name in ["p", "ul", "ol", "h3", "h4", "h5"] or isinstance(next_node, type(soup.comment))):
                        to_delete = next_node
                        next_node = next_node.find_next_sibling()
                        to_delete.decompose()
    
                    # Parse nội dung HTML được sinh
                    content_fragment = BeautifulSoup(heading_content, "html.parser")

                    # Chèn từng thẻ nội dung ngay sau <h2>
                    for tag in reversed(content_fragment.contents):
                        h2.insert_after(tag)

                except Exception as e:
                    print(f"⚠️ Error generating content for {h2_text}: {e}")
                    continue

            print('done...')

            if save_html:
                with open(f"result/{slugify(topic)}.html", "w", encoding="utf-8") as f:
                    f.write(str(soup))
                
            result = {
                "topic": topic,
                "date": str(date.today()),
                "html": str(soup),
            }

            #Lấy title
            title_tag = soup.find('title')
            if title_tag and title_tag.text:
                result['title'] = title_tag.text
            else:
                h1_tag = soup.find("h1")
                if h1_tag and h1_tag.text:
                    result['title'] = h1_tag.text

            #Tạo slug
            if 'title' in result and result['title']:
                result['slug'] = slugify(result['title'])
            else:
                result['slug'] = slugify(topic)

                
            #Lấy description
            meta_description = soup.find("meta", attrs={"name": "description"})
            if meta_description:
                result['description'] = meta_description.get("content", "")
                
            #Lấy keywords
            meta_keywords = soup.find("meta", attrs={"name": "keywords"})
            if meta_keywords:
                result['keywords'] = meta_keywords.get("content", "")


            #Lấy content
            container = soup.find("div", class_="container")
            if container:
                h1_tag = container.find("h1")
                if h1_tag:
                    content_after_h1 = []
                    for sibling in h1_tag.find_next_siblings():
                        content_after_h1.append(str(sibling))
                    result['content'] = "\n".join(content_after_h1)

            if save_json:
                with open(f"result/{slugify(topic)}.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                    
            return result

        except Exception as e:
            return {
                "error": str(e),
                "topic": topic,
                "raw_response": structure_text if 'structure_text' in locals() else None
            }
