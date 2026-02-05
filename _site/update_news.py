import requests
import yaml
import os
import sys
import datetime

# ================= 설정 =================
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

if not NOTION_TOKEN or not DATABASE_ID:
    print("Error: 환경 변수(NOTION_TOKEN, DATABASE_ID)가 설정되지 않았습니다.")
    sys.exit(1)

DATA_FILES = {
    "News": {"yaml": "_data/news.yml", "folder": "news"},
    "Notice": {"yaml": "_data/notice.yml", "folder": "notice"}
}

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_pages_by_status(status_option):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": "Status", 
            "status": { "equals": status_option }
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
        if annotations["code"]: content = f"`{content}`"
        if annotations["bold"]: content = f"**{content}**"
        if annotations["italic"]: content = f"*{content}*"
        if annotations["strikethrough"]: content = f"~~{content}~~"
        href = text_obj.get("href")
        if href: content = f"[{content}]({href})"
        output_text += content
    return output_text

def notion_blocks_to_markdown(blocks):
    md_text = ""
    for block in blocks:
        b_type = block["type"]
        if b_type == "paragraph":
            md_text += rich_text_to_md_string(block["paragraph"]["rich_text"]) + "\n\n"
        elif b_type == "heading_1":
            md_text += "# " + rich_text_to_md_string(block["heading_1"]["rich_text"]) + "\n\n"
        elif b_type == "heading_2":
            md_text += "## " + rich_text_to_md_string(block["heading_2"]["rich_text"]) + "\n\n"
        elif b_type == "heading_3":
            md_text += "### " + rich_text_to_md_string(block["heading_3"]["rich_text"]) + "\n\n"
        elif b_type == "bulleted_list_item":
            md_text += "- " + rich_text_to_md_string(block["bulleted_list_item"]["rich_text"]) + "\n"
        elif b_type == "numbered_list_item":
            md_text += "1. " + rich_text_to_md_string(block["numbered_list_item"]["rich_text"]) + "\n"
        elif b_type == "quote":
            md_text += "> " + rich_text_to_md_string(block["quote"]["rich_text"]) + "\n\n"
    return md_text

def update_notion_status(page_id, new_status):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "Status": { "status": { "name": new_status } }
        }
    }
    requests.patch(url, json=payload, headers=headers)

def main():
    # 1. 기존 데이터 파일(yml) 로드
    yaml_data = {}
    for cat, paths in DATA_FILES.items():
        if os.path.exists(paths["yaml"]):
            with open(paths["yaml"], 'r', encoding='utf-8') as f:
                yaml_data[cat] = yaml.safe_load(f) or {'issue': []}
        else:
            yaml_data[cat] = {'issue': []}
        
        if 'issue' not in yaml_data[cat] or yaml_data[cat]['issue'] is None:
            yaml_data[cat]['issue'] = []

    # ---------------------------------------------------------
    # [기능 1] 게시글 생성/업데이트 (Ready -> Published)
    # ---------------------------------------------------------
    ready_pages = get_pages_by_status("Ready")
    print(f"발견된 Ready 페이지 수: {len(ready_pages)}")

    for page in ready_pages:
        try:
            category = page["properties"]["Category"]["select"]["name"]
        except: continue
        if category not in DATA_FILES: continue
        target_conf = DATA_FILES[category]
        
        try:
            title = page["properties"]["이름"]["title"][0]["plain_text"]
            date_str = page["properties"]["Date"]["date"]["start"]
        except: continue

        page_id = page["id"] # Notion 고유 ID
        
        safe_title = title.replace(" ", "-").replace("/", "-")
        filename = f"{safe_title}.md"
        filepath = os.path.join(target_conf["folder"], filename)
        target_url = f"/{target_conf['folder']}/{safe_title}/"

        # [핵심 로직] ID 기반 중복/변경 체크
        # 기존 YAML 목록에서 '같은 Page ID'를 가진 항목이 있는지 찾습니다.
        existing_entry = None
        for item in yaml_data[category]['issue']:
            if item.get('page_id') == page_id:
                existing_entry = item
                break
        
        # 만약 ID는 없는데 URL(제목)이 같은 게 있다면? (구 버전 데이터 호환용)
        if not existing_entry:
            for item in yaml_data[category]['issue']:
                if item.get('url') == target_url:
                    existing_entry = item
                    break

        # [파일 정리] 제목이 바뀌어서 URL이 달라졌다면, 옛날 파일 삭제
        if existing_entry:
            old_url = existing_entry.get('url')
            if old_url and old_url != target_url:
                # URL에서 파일 경로 역추적 (/news/old-title/ -> news/old-title.md)
                old_filename = old_url.strip('/').split('/')[-1] + ".md"
                old_filepath = os.path.join(target_conf["folder"], old_filename)
                
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
                    print(f"[이름변경] 기존 파일 삭제됨: {old_filepath}")
        
        # 새 파일 생성
        os.makedirs(target_conf["folder"], exist_ok=True)
        blocks = get_block_children(page_id)
        content_md = notion_blocks_to_markdown(blocks)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write("layout: pretty_post\n")
            f.write(f"title: {title}\n")
            f.write(f"date: {date_str}\n")
            f.write(f"permalink: {target_url}\n")
            f.write("---\n\n")
            f.write(f"## {title}\n\n")
            f.write(content_md)
        print(f"[생성] {filepath}")

        # YAML 리스트 업데이트 (ID 포함)
        new_entry = {
            "text": title, 
            "date": date_str.replace("-", "/"), 
            "url": target_url, 
            "page_id": page_id  # <--- ID 저장!
        }
        
        # 기존 리스트에서 '같은 ID' 또는 '같은 URL'을 가진 항목 제거 후 새거 추가
        new_issue_list = []
        for item in yaml_data[category]['issue']:
            # ID가 같거나 URL이 같으면 제외 (덮어쓰기 위해)
            if item.get('page_id') == page_id or item.get('url') == target_url:
                continue
            new_issue_list.append(item)
        
        new_issue_list.append(new_entry)
        yaml_data[category]['issue'] = new_issue_list

        update_notion_status(page_id, "Published")

    # ---------------------------------------------------------
    # [기능 2] 게시글 삭제 (Unpublish) - 기존 코드와 동일
    # ---------------------------------------------------------
    unpublish_pages = get_pages_by_status("Unpublish") 
    for page in unpublish_pages:
        try: category = page["properties"]["Category"]["select"]["name"]
        except: continue
        if category not in DATA_FILES: continue
        target_conf = DATA_FILES[category]
        
        page_id = page["id"]
        
        # ID로 삭제할 파일 찾기
        target_item = None
        for item in yaml_data[category]['issue']:
            if item.get('page_id') == page_id:
                target_item = item
                break
        
        # ID로 못 찾았으면 제목으로 찾기 (호환성)
        if not target_item:
            try:
                title = page["properties"]["이름"]["title"][0]["plain_text"]
                safe_title = title.replace(" ", "-").replace("/", "-")
                target_url = f"/{target_conf['folder']}/{safe_title}/"
                for item in yaml_data[category]['issue']:
                    if item.get('url') == target_url:
                        target_item = item
                        break
            except: pass

        if target_item:
            # 파일 삭제
            del_url = target_item.get('url')
            del_filename = del_url.strip('/').split('/')[-1] + ".md"
            del_filepath = os.path.join(target_conf["folder"], del_filename)
            
            if os.path.exists(del_filepath):
                os.remove(del_filepath)
                print(f"[삭제] {del_filepath}")
            
            # 리스트에서 제거
            yaml_data[category]['issue'] = [i for i in yaml_data[category]['issue'] if i != target_item]
            print(f"[목록제거] {target_item['text']}")

        update_notion_status(page["id"], "Unpublished")

    # ---------------------------------------------------------
    # [기능 3] 저장 및 정렬
    # ---------------------------------------------------------
    for cat, data in yaml_data.items():
        data['issue'].sort(key=lambda x: x['date'])
        with open(DATA_FILES[cat]["yaml"], 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    print("완료.")

if __name__ == "__main__":
    main()