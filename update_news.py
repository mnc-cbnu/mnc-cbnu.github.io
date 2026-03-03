import requests
import yaml
import os
import sys
import urllib.request
from datetime import datetime
import re

# ================= 설정 =================
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID_NEWS = os.environ.get("DATABASE_ID")      # News/Notice DB
DATABASE_ID_PUBS = os.environ.get("DATABASE_ID_PUBS") # 논문 DB

if not NOTION_TOKEN:
    print("Error: NOTION_TOKEN 환경변수 누락")
    sys.exit(1)

HEADERS = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 파일 경로 설정
DATA_FILES = {
    "News": {"yaml": "_data/news.yml", "folder": "news"},
    "Notice": {"yaml": "_data/notice.yml", "folder": "notice"}
}
PUBS_YAML_PATH = "_data/publications.yml"
FEATURED_YAML_PATH = "_data/featured.yml"

# 다운로드된 이미지가 저장될 로컬 경로
IMG_DIR = "assets/img/" 

# ================= 공통 함수 =================
def get_pages(db_id, status="Ready"):
    """한 번에 100개 이상의 페이지도 전부 긁어오는 함수"""
    all_results = []
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = {"filter": {"property": "Status", "status": {"equals": status}}}
    
    has_more = True
    next_cursor = None
    while has_more:
        if next_cursor: payload["start_cursor"] = next_cursor
        response = requests.post(url, json=payload, headers=HEADERS)
        data = response.json()
        all_results.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")
    return all_results

def update_status(page_id, new_status="Published"):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": {"Status": {"status": {"name": new_status}}}}
    requests.patch(url, json=payload, headers=HEADERS)

def download_image(url, save_dir, filename):
    """이미지 URL을 로컬에 다운로드하고 웹에서 쓸 수 있는 경로를 반환"""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    
    ext = "png" if "png" in url else "jpg"
    save_path = f"{save_dir}/{filename}.{ext}"
    try:
        urllib.request.urlretrieve(url, save_path)
        return f"/{save_path}" # 브라우저에서 읽을 수 있는 절대 경로
    except Exception as e:
        print(f"   ⚠️ 이미지 다운로드 실패: {e}")
        return None

def get_block_children(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    return requests.get(url, headers=HEADERS).json().get("results", [])

def blocks_to_markdown(blocks, save_dir, prefix):
    """Notion 블록을 마크다운으로 변환 (이미지 블록 포함)"""
    text = ""
    img_count = 1
    for b in blocks:
        try:
            b_type = b["type"]
            
            # 1. 일반 텍스트 블록 처리
            if "rich_text" in b.get(b_type, {}):
                content = "".join([t["plain_text"] for t in b[b_type]["rich_text"]])
                if b_type == "heading_1": text += f"# {content}\n\n"
                elif b_type == "heading_2": text += f"## {content}\n\n"
                elif b_type == "heading_3": text += f"### {content}\n\n"
                elif b_type == "bulleted_list_item": text += f"- {content}\n"
                elif b_type == "numbered_list_item": text += f"1. {content}\n"
                else: text += f"{content}\n\n"
                
            # 2. 이미지 블록 처리 (다운로드 로직 포함)
            elif b_type == "image":
                img_url = b["image"].get("file", {}).get("url") or b["image"].get("external", {}).get("url")
                if img_url:
                    img_filename = f"{prefix}_img{img_count}"
                    local_img_path = download_image(img_url, save_dir, img_filename)
                    if local_img_path:
                        text += f"![image]({local_img_path})\n\n" # 마크다운 이미지 문법
                    img_count += 1
        except:
            pass
    return text

# ================= Main Logic =================
def main():
    print("=== 🔄 홈페이지 업데이트 시작 ===")

    # ---------------------------------------------------------
    # [1] News & Notice 처리 (이미지 다운로드 및 날짜 자동입력)
    # ---------------------------------------------------------
    if DATABASE_ID_NEWS:
        print("\n[1] News/Notice 처리 중...")
        yaml_data = {}
        for cat, conf in DATA_FILES.items():
            if os.path.exists(conf["yaml"]):
                with open(conf["yaml"], 'r', encoding='utf-8') as f:
                    yaml_data[cat] = yaml.safe_load(f) or {'issue': []}
            else:
                yaml_data[cat] = {'issue': []}

        pages = get_pages(DATABASE_ID_NEWS, "Ready")
        for p in pages:
            try:
                props = p["properties"]
                cat = props["Category"]["select"]["name"]
                if cat not in DATA_FILES: continue
                
                title = props["이름"]["title"][0]["plain_text"]
                
                # [✨추가됨] Date가 비어있으면 오늘 날짜 자동 입력
                if props.get("Date") and props["Date"].get("date"):
                    date = props["Date"]["date"]["start"]
                else:
                    date = datetime.now().strftime("%Y-%m-%d")
                    
                p_id = p["id"]
            except Exception as e: 
                print(f"   ⚠️ 건너뜀 (필수 정보 누락): {p.get('id')}")
                continue

            # 파일명으로 쓸 수 없는 특수문자 제거
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "-")
            conf = DATA_FILES[cat]
            filepath = os.path.join(conf["folder"], f"{safe_title}.md")
            os.makedirs(conf["folder"], exist_ok=True)
            
            # [✨추가됨] 본문을 읽어오면서 이미지도 다운로드하여 Markdown 생성
            blocks = get_block_children(p_id)
            content = blocks_to_markdown(blocks, IMG_DIR+f'conf["folder"]', safe_title)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"---\nlayout: pretty_post\ntitle: \"{title}\"\ndate: {date}\n---\n\n{content}")
            
            entry = {"text": title, "date": date.replace("-", "/"), "url": f"/{conf['folder']}/{safe_title}/", "page_id": p_id}
            yaml_data[cat]['issue'] = [i for i in yaml_data[cat]['issue'] if i.get('page_id') != p_id]
            yaml_data[cat]['issue'].append(entry)
            
            update_status(p_id, "Published")
            print(f"   ✅ [{cat}] {title}")

        for cat, data in yaml_data.items():
            data['issue'].sort(key=lambda x: x['date'], reverse=True)
            with open(DATA_FILES[cat]["yaml"], 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    # ---------------------------------------------------------
    # [2] Publications 처리 (기존 구조 유지)
    # ---------------------------------------------------------
    if DATABASE_ID_PUBS:
        print("\n[2] Publications 처리 중...")
        nested_pubs = {}
        featured_list = []

        if os.path.exists(PUBS_YAML_PATH):
            with open(PUBS_YAML_PATH, 'r', encoding='utf-8') as f:
                nested_pubs = yaml.safe_load(f) or {}

        pubs = get_pages(DATABASE_ID_PUBS, "Ready")
        count = 0
        for p in pubs:
            try:
                props = p["properties"]
                title_text = props["이름"]["title"][0]["plain_text"]
                authors = props["Authors"]["rich_text"][0]["plain_text"]
                venue = props["Venue"]["rich_text"][0]["plain_text"]
                year = props["Year"]["number"]
                category_raw = props["Category"]["select"]["name"]
                selected = props["Selected"]["checkbox"]
                p_id = p["id"]
                
                cat_key = "conference" if "Conference" in category_raw else "journal"
                formatted_title = f"{title_text}. {venue}, {year} ({year})"
            except Exception as e:
                continue

            if year not in nested_pubs: nested_pubs[year] = {"journal": [], "conference": []}
            if cat_key not in nested_pubs[year]: nested_pubs[year][cat_key] = []
            if nested_pubs[year][cat_key] is None: nested_pubs[year][cat_key] = []

            existing_ids = [x.get('page_id') for x in nested_pubs[year][cat_key] if isinstance(x, dict)]
            if p_id not in existing_ids:
                nested_pubs[year][cat_key].append({"title": formatted_title, "authors": authors, "page_id": p_id})
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

        if count > 0:
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
                        old_featured.insert(0, f_item)
                featured_list = old_featured
            
            with open(FEATURED_YAML_PATH, 'w', encoding='utf-8') as f:
                yaml.dump(featured_list, f, allow_unicode=True, sort_keys=False)
                
        print(f"   ✅ 총 {count}건의 논문 업데이트 완료")

    print("\n=== ✨ 모든 업데이트 완료 ===")

if __name__ == "__main__":
    main()