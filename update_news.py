import requests
import yaml
import os
import sys

# ================= 설정 =================
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID_NEWS = os.environ.get("DATABASE_ID")      # News/Notice
DATABASE_ID_PUBS = os.environ.get("DATABASE_ID_PUBS") # 논문 DB

if not NOTION_TOKEN:
    print("Error: NOTION_TOKEN 환경변수 누락")
    sys.exit(1)

HEADERS = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

DATA_FILES = {
    "News": {"yaml": "_data/news.yml", "folder": "news"},
    "Notice": {"yaml": "_data/notice.yml", "folder": "notice"}
}
PUBS_YAML_PATH = "_data/publications.yml"  # [1] 전체 목록 (계층형)
FEATURED_YAML_PATH = "_data/featured.yml"  # [2] 메인 화면용 (선택된 것만)

def get_pages(db_id, status="Ready"):
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = {"filter": {"property": "Status", "status": {"equals": status}}}
    response = requests.post(url, json=payload, headers=HEADERS)
    return response.json().get("results", [])

def update_status(page_id, new_status="Published"):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": {"Status": {"status": {"name": new_status}}}}
    requests.patch(url, json=payload, headers=HEADERS)

def get_block_children(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    return requests.get(url, headers=HEADERS).json().get("results", [])

def blocks_to_text(blocks):
    text = ""
    for b in blocks:
        try:
            b_type = b["type"]
            if "rich_text" in b[b_type]:
                content = "".join([t["plain_text"] for t in b[b_type]["rich_text"]])
                if b_type == "heading_1": text += f"# {content}\n\n"
                elif b_type == "heading_2": text += f"## {content}\n\n"
                elif b_type == "bulleted_list_item": text += f"- {content}\n"
                else: text += f"{content}\n\n"
        except: pass
    return text

def main():
    print("=== 🔄 홈페이지 업데이트 시작 ===")


    if DATABASE_ID_NEWS:
        print("\n[1] News/Notice 처리 중...")

    if DATABASE_ID_PUBS:
        print("\n[2] Publications 처리 중...")

        nested_pubs = {}
        featured_list = []

        pubs = get_pages(DATABASE_ID_PUBS, "Ready")
                
        if os.path.exists(PUBS_YAML_PATH):
            with open(PUBS_YAML_PATH, 'r', encoding='utf-8') as f:
                nested_pubs = yaml.safe_load(f) or {}

        count = 0
        for p in pubs:
            try:
                props = p["properties"]
                title_text = props["이름"]["title"][0]["plain_text"]
                authors = props["Authors"]["rich_text"][0]["plain_text"]
                venue = props["Venue"]["rich_text"][0]["plain_text"]
                year = props["Year"]["number"]
                category_raw = props["Category"]["select"]["name"] # Journal or Conference
                selected = props["Selected"]["checkbox"]
                p_id = p["id"]
                
                # 카테고리 소문자 변환 (journal / conference)
                cat_key = "conference" if "Conference" in category_raw else "journal"
                
                formatted_title = f"{title_text}. {venue}, {year} ({year})"
                
            except Exception as e:
                print(f"   ⚠️ 데이터 누락: {p.get('id')} / {e}")
                continue

            if year not in nested_pubs:
                nested_pubs[year] = {"journal": [], "conference": []}
            if cat_key not in nested_pubs[year]: # 혹시 키가 없을 경우 대비
                nested_pubs[year][cat_key] = []
            if nested_pubs[year][cat_key] is None: # null일 경우
                nested_pubs[year][cat_key] = []

            existing_ids = [x.get('page_id') for x in nested_pubs[year][cat_key] if isinstance(x, dict)]
            
            if p_id not in existing_ids:
                entry = {
                    "title": formatted_title, # 포맷팅된 제목
                    "authors": authors,
                    "page_id": p_id
                }
                nested_pubs[year][cat_key].append(entry)
                count += 1
            
            if selected:
                featured_list.append({
                    "title": title_text,
                    "authors": authors,
                    "venue": venue,
                    "year": year,
                    "page_id": p_id
                })

            update_status(p_id, "Published")

        sorted_pubs = dict(sorted(nested_pubs.items(), key=lambda item: item[0], reverse=True))
        
        with open(PUBS_YAML_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(sorted_pubs, f, allow_unicode=True, sort_keys=False)
            
        if featured_list:
            if os.path.exists(FEATURED_YAML_PATH):
                with open(FEATURED_YAML_PATH, 'r', encoding='utf-8') as f:
                    old_featured = yaml.safe_load(f) or []
                old_ids = {x['page_id'] for x in old_featured}
                for f_item in featured_list:
                    if f_item['page_id'] not in old_ids:
                        old_featured.insert(0, f_item) # 최신을 위로
                featured_list = old_featured
            
            with open(FEATURED_YAML_PATH, 'w', encoding='utf-8') as f:
                yaml.dump(featured_list, f, allow_unicode=True, sort_keys=False)


if __name__ == "__main__":
    main()