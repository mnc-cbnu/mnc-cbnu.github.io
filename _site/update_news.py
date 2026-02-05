import requests
import yaml
import os
import sys

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

if not NOTION_TOKEN or not DATABASE_ID:
    print("Error: 환경 변수(NOTION_TOKEN, DATABASE_ID)가 설정되지 않았습니다.")
    sys.exit(1)

DATA_FILES = {
    "News": {"yaml": "_data/news.yml", "folder": "news"},
    "Notice": {"yaml": "_data/notice.yml", "folder": "notice"} # notice 폴더 미리 만들어두세요!
}

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_ready_pages():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": "Status",
            "select": {
                "equals": "Ready"
            }
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get("results", [])


def get_block_children(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    response = requests.get(url, headers=headers)
    return response.json().get("results", [])


def rich_text_to_md_string(rich_text_list):
    output_text = ""

    for text_obj in rich_text_list:
        content = text_obj["plain_text"]

        annotations = text_obj["annotations"]
        if annotations["code"]:
            content = f"`{content}`"
        if annotations["bold"]:
            content = f"**{content}**"
        if annotations["italic"]:
            content = f"*{content}*"
        if annotations["strikethrough"]:
            content = f"~~{content}~~"

        href = text_obj.get("href")
        if href:
            content = f"[{content}]({href})"

        output_text += content

    return output_text


def notion_blocks_to_markdown(blocks):
    md_text = ""

    for block in blocks:
        b_type = block["type"]

        if b_type == "paragraph":
            rich_text = block["paragraph"]["rich_text"]
            md_text += rich_text_to_md_string(rich_text) + "\n\n"

        elif b_type == "heading_1":
            rich_text = block["heading_1"]["rich_text"]
            md_text += "# " + rich_text_to_md_string(rich_text) + "\n\n"

        elif b_type == "heading_2":
            rich_text = block["heading_2"]["rich_text"]
            md_text += "## " + rich_text_to_md_string(rich_text) + "\n\n"

        elif b_type == "heading_3":
            rich_text = block["heading_3"]["rich_text"]
            md_text += "### " + rich_text_to_md_string(rich_text) + "\n\n"

        elif b_type == "bulleted_list_item":
            rich_text = block["bulleted_list_item"]["rich_text"]
            md_text += "- " + rich_text_to_md_string(rich_text) + "\n"

        elif b_type == "numbered_list_item":
            rich_text = block["numbered_list_item"]["rich_text"]
            md_text += "1. " + rich_text_to_md_string(rich_text) + "\n"

        elif b_type == "quote":
            rich_text = block["quote"]["rich_text"]
            md_text += "> " + rich_text_to_md_string(rich_text) + "\n\n"


    return md_text


def update_notion_status(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "Status": {
                "select": {
                    "name": "Published"
                }
            }
        }
    }
    requests.patch(url, json=payload, headers=headers)


def main():
    pages = get_ready_pages()
    
    if not pages:
        print("업데이트할 새 글이 없습니다.")
        return

    yaml_data = {}
    for cat, paths in DATA_FILES.items():
        if os.path.exists(paths["yaml"]):
            with open(paths["yaml"], 'r', encoding='utf-8') as f:
                yaml_data[cat] = yaml.safe_load(f) or {'issue': []}
        else:
            yaml_data[cat] = {'issue': []}

    for page in pages:
        props = page["properties"]
        
        try:
            category = props["Category"]["select"]["name"]
        except (KeyError, TypeError):
            print(f"[Skip] 카테고리가 없는 글이 있습니다: {page['id']}")
            continue

        if category not in DATA_FILES:
            print(f"[Skip] 지원하지 않는 카테고리입니다: {category}")
            continue
            
        target_conf = DATA_FILES[category]
        
        title = props["이름"]["title"][0]["plain_text"]
        date_str = props["Date"]["date"]["start"]
        page_id = page["id"]
        
        safe_title = title.replace(" ", "-").replace("/", "-")
        filename = f"{safe_title}.md"
        filepath = os.path.join(target_conf["folder"], filename)
        
        os.makedirs(target_conf["folder"], exist_ok=True)
        
        blocks = get_block_children(page_id)
        content_md = notion_blocks_to_markdown(blocks)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write("layout: default\n")
            f.write(f"title: {title}\n")
            f.write(f"date: {date_str}\n")
            f.write(f"permalink: /{target_conf['folder']}/{safe_title}/\n")
            f.write("---\n\n")
            f.write(content_md)
        
        print(f"[생성 완료] ({category}) {filepath}")

        new_entry = {
            "text": title,
            "date": date_str.replace("-", "/"),
            "url": f"/{target_conf['folder']}/{safe_title}/"
        }
        
        if 'issue' not in yaml_data[category]:
            yaml_data[category]['issue'] = []
            
        yaml_data[category]['issue'].append(new_entry)

    for cat, data in yaml_data.items():
        path = DATA_FILES[cat]["yaml"]
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    
    print("모든 작업 완료!")
    

if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()