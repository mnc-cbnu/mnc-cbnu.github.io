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

# 카테고리별 설정 (News / Notice)
DATA_FILES = {
    "News": {"yaml": "_data/news.yml", "folder": "news"},
    "Notice": {"yaml": "_data/notice.yml", "folder": "notice"}
}

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
# ===========================================

def get_pages_by_status(status_option):
    """특정 상태(Status)인 페이지들을 가져옵니다."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    # [주의] Notion 속성 이름이 "Status"가 아니라 "상태"라면 아래 property를 수정하세요.
    # [주의] 속성 타입이 '선택(Select)'인지 '상태(Status)'인지에 따라 구조가 다릅니다.
    # 아래는 '선택(Select)' 타입 기준입니다.
    payload = {
        "filter": {
            "property": "Status", 
            "select": {
                "equals": status_option
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
            "Status": { # 속성 이름 확인
                "select": {
                    "name": new_status
                }
            }
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
        
        # 데이터가 None일 경우 빈 리스트로 방어 코드
        if 'issue' not in yaml_data[cat] or yaml_data[cat]['issue'] is None:
            yaml_data[cat]['issue'] = []

    # ---------------------------------------------------------
    # [기능 1] 게시글 생성/업데이트 (Ready -> Published)
    # ---------------------------------------------------------
    ready_pages = get_pages_by_status("Ready")
    for page in ready_pages:
        try:
            category = page["properties"]["Category"]["select"]["name"]
        except (KeyError, TypeError):
            continue
            
        if category not in DATA_FILES: continue
        target_conf = DATA_FILES[category]
        
        props = page["properties"]
        title = props["이름"]["title"][0]["plain_text"]
        date_str = props["Date"]["date"]["start"]
        page_id = page["id"]
        
        safe_title = title.replace(" ", "-").replace("/", "-")
        filename = f"{safe_title}.md"
        filepath = os.path.join(target_conf["folder"], filename)
        
        # 폴더 생성 및 md 파일 쓰기
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
            f.write(f"## {title}\n\n")
            f.write(content_md)
        
        print(f"[생성] {filepath}")

        # YAML 데이터 업데이트 (기존에 있으면 삭제 후 추가 - 업데이트 효과)
        target_url = f"/{target_conf['folder']}/{safe_title}/"
        new_entry = {"text": title, "date": date_str.replace("-", "/"), "url": target_url}
        
        # 기존 목록에서 같은 URL을 가진 항목 제거 (중복 방지)
        yaml_data[category]['issue'] = [item for item in yaml_data[category]['issue'] if item.get('url') != target_url]
        yaml_data[category]['issue'].append(new_entry)

        update_notion_status(page_id, "Published")

    # ---------------------------------------------------------
    # [기능 2] 게시글 삭제 (Delete -> Deleted)
    # ---------------------------------------------------------
    unpublish_pages = get_pages_by_status("Unpublish") 
    
    for page in unpublish_pages:
        try:
            category = page["properties"]["Category"]["select"]["name"]
        except: continue
        
        if category not in DATA_FILES: continue
        target_conf = DATA_FILES[category]
        
        title = page["properties"]["이름"]["title"][0]["plain_text"]
        safe_title = title.replace(" ", "-").replace("/", "-")
        filename = f"{safe_title}.md"
        filepath = os.path.join(target_conf["folder"], filename)
        
        # 1. 홈페이지 파일(.md) 삭제 (GitHub에서는 사라짐)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"[삭제] 파일 제거됨: {filepath}")
        else:
            print(f"[알림] 삭제할 파일이 없음: {filepath}")
            
        # 2. YAML 목록에서 제거 (홈페이지 목록에서 사라짐)
        target_url = f"/{target_conf['folder']}/{safe_title}/"
        # URL이 일치하지 않는 것만 남김 = 일치하는 것 제거
        yaml_data[category]['issue'] = [item for item in yaml_data[category]['issue'] if item.get('url') != target_url]
        
        print(f"[목록제거] 리스트에서 숨김 처리됨: {title}")

        # 3. 노션 상태 변경 (Unpublished) -> 데이터는 노션에 안전하게 남음
        update_notion_status(page["id"], "Unpublished")

    # ---------------------------------------------------------
    # [기능 3] 날짜순 정렬 및 저장
    # ---------------------------------------------------------
    for cat, data in yaml_data.items():
        # 날짜 오름차순 정렬 (옛날 -> 최신)
        # 이유: Jekyll에서 'reversed'를 쓰기 때문에, 파일에는 옛날게 위에 있어야 함
        data['issue'].sort(key=lambda x: x['date'])
        
        path = DATA_FILES[cat]["yaml"]
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
            
    print("모든 작업 완료! (생성/삭제/정렬)")

if __name__ == "__main__":
    main()