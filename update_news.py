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
DATABASE_ID_MEMBERS = os.environ.get("DATABASE_ID_MEMBERS")
DATABASE_ID_PAGES = os.environ.get("DATABASE_ID_PAGES")

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
IMG_DIR_NEWS = "assets/img/news" 

# ================= 공통 함수 =================
def get_pages(db_id, status="Ready"):
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
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    
    ext = "png" if "png" in url else "jpg"
    save_path = f"{save_dir}/{filename}.{ext}"
    try:
        urllib.request.urlretrieve(url, save_path)
        return f"/{save_path}" 
    except Exception as e:
        print(f"   ⚠️ 이미지 다운로드 실패: {e}")
        return None

def get_block_children(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    return requests.get(url, headers=HEADERS).json().get("results", [])

def parse_rich_text(rich_text_array):
    """Notion의 글자 꾸밈 효과(색상, 굵기 등)를 HTML/마크다운으로 변환"""
    parsed_text = ""
    for t in rich_text_array:
        text = t.get("plain_text", "")
        if not text:
            continue
            
        annotations = t.get("annotations", {})
        color = annotations.get("color", "default")
        
        # 1. 글자색 및 배경색 처리
        if color != "default":
            if "_background" in color:
                bg_color = color.replace("_background", "")
                # 회색 배경은 너무 진할 수 있어 연한 회색으로 보정
                if bg_color == "gray": bg_color = "lightgray" 
                text = f'<span style="background-color: {bg_color};">{text}</span>'
            else:
                text = f'<span style="color: {color};">{text}</span>'
                
        # 2. 굵게, 기울임, 밑줄, 취소선, 인라인 코드 처리
        if annotations.get("code"):
            text = f"`{text}`"
        if annotations.get("bold"):
            text = f"**{text}**"
        if annotations.get("italic"):
            text = f"*{text}*"
        if annotations.get("strikethrough"):
            text = f"~~{text}~~"
        if annotations.get("underline"):
            text = f"<u>{text}</u>"
            
        parsed_text += text
    return parsed_text

def blocks_to_markdown(blocks, save_dir, prefix):
    text = ""
    img_count = 1
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for b in blocks:
        try:
            b_type = b["type"]
            if "rich_text" in b.get(b_type, {}):
                content = parse_rich_text(b[b_type]["rich_text"])
                if b_type == "heading_1": text += f"# {content}\n\n"
                elif b_type == "heading_2": text += f"## {content}\n\n"
                elif b_type == "heading_3": text += f"### {content}\n\n"
                elif b_type == "bulleted_list_item": text += f"- {content}\n"
                elif b_type == "numbered_list_item": text += f"1. {content}\n"
                else: text += f"{content}\n\n"
                
            elif b_type == "image":
                img_url = b["image"].get("file", {}).get("url") or b["image"].get("external", {}).get("url")
                if img_url:
                    img_filename = f"{prefix}_{timestamp}_img{img_count}"
                    local_img_path = download_image(img_url, save_dir, img_filename)
                    if local_img_path:
                        text += f"![image]({local_img_path})\n\n" 
                    img_count += 1
        except:
            pass
    return text
def blocks_to_sections(blocks, save_dir, prefix):
    """Notion 블록을 '# 제목' 기준으로 쪼개서 딕셔너리로 반환"""
    sections = {"Profile": "", "Profile_Image": "/assets/img/professor.jpg"} 
    current_section = "Profile"
    img_count = 1
    heading_count = 0  # 💡 [추가됨] 제목이 몇 번 나왔는지 세는 카운터
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for b in blocks:
        try:
            b_type = b["type"]
            
            # 1. 제목(Heading) 처리
            if b_type in ["heading_1", "heading_2", "heading_3"]:
                clean_title = "".join([t["plain_text"] for t in b[b_type]["rich_text"]]).strip()
                
                # 💡 [핵심] 문서의 첫 번째 제목(보통 교수님 이름)은 카드로 쪼개지 않고 프로필 영역에 큰 글씨로 추가합니다!
                if heading_count == 0 and current_section == "Profile":
                    sections["Profile"] += f"# {clean_title}\n\n"
                    heading_count += 1
                    continue
                    
                # 두 번째 제목부터는 새로운 카드(섹션)으로 분리합니다.
                current_section = clean_title
                sections[current_section] = "" 
                heading_count += 1
                continue 
                
            # 2. 텍스트 내용 처리
            elif "rich_text" in b.get(b_type, {}):
                content = parse_rich_text(b[b_type]["rich_text"])
                if b_type == "bulleted_list_item": sections[current_section] += f"- {content}\n"
                elif b_type == "numbered_list_item": sections[current_section] += f"1. {content}\n"
                else: sections[current_section] += f"{content}\n\n"
                
            # 3. 이미지 처리
            elif b_type == "image":
                img_url = b["image"].get("file", {}).get("url") or b["image"].get("external", {}).get("url")
                if img_url:
                    img_filename = f"{prefix}_{timestamp}_img{img_count}"
                    local_img_path = download_image(img_url, save_dir, img_filename)
                    if local_img_path:
                        # 맨 처음 나오는 이미지는 무조건 교수님 프로필 사진으로 지정
                        if current_section == "Profile" and sections["Profile_Image"] == "/assets/img/professor.jpg":
                            sections["Profile_Image"] = local_img_path
                        else:
                            sections[current_section] += f"![image]({local_img_path})\n\n"
                    img_count += 1
        except:
            pass
            
    # 글자 끝의 쓸데없는 줄바꿈들 정리
    for key in sections:
        sections[key] = sections[key].strip()
    return sections
# ================= Main Logic =================
def main():
    print("=== 🔄 홈페이지 업데이트 시작 ===")

    # ---------------------------------------------------------
    # [1] News & Notice 처리
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

        # --- [추가] 1-A. Unpublish 처리 ---
        unpublish_pages = get_pages(DATABASE_ID_NEWS, "Unpublish")
        for p in unpublish_pages:
            try:
                p_id = p["id"]
                props = p["properties"]
                cat = props["Category"]["select"]["name"]
                title = props["이름"]["title"][0]["plain_text"]
                safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "-")

                # YAML 명단에서 제거
                if cat in yaml_data:
                    yaml_data[cat]['issue'] = [i for i in yaml_data[cat]['issue'] if i.get('page_id') != p_id]
                
                # 마크다운 파일 삭제
                if cat in DATA_FILES:
                    filepath = os.path.join(DATA_FILES[cat]["folder"], f"{safe_title}.md")
                    if os.path.exists(filepath):
                        os.remove(filepath)

                update_status(p_id, "Unpublished") # 다시 올릴 수 있도록 Unpublished로 변경
                print(f"   🗑️ [{cat}] 숨김 처리 완료: {title}")
            except Exception as e:
                continue

        # --- 1-B. 신규 글 발행 (Ready -> Published) ---
        pages = get_pages(DATABASE_ID_NEWS, "Ready")
        for p in pages:
            try:
                props = p["properties"]
                cat = props["Category"]["select"]["name"]
                if cat not in DATA_FILES: continue
                
                title = parse_rich_text(props["이름"]["title"])
                authors = parse_rich_text(props["Authors"]["rich_text"])
                
                # title = props["이름"]["title"][0]["plain_text"]
                if props.get("Date") and props["Date"].get("date"):
                    date = props["Date"]["date"]["start"]
                else:
                    date = datetime.now().strftime("%Y-%m-%d")
                    
                p_id = p["id"]
            except Exception as e: 
                continue

            safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "-")
            conf = DATA_FILES[cat]
            filepath = os.path.join(conf["folder"], f"{safe_title}.md")
            os.makedirs(conf["folder"], exist_ok=True)
            
            blocks = get_block_children(p_id)
            content = blocks_to_markdown(blocks, IMG_DIR_NEWS, safe_title)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"---\nlayout: pretty_post\ntitle: \"{title}\"\ndate: {date}\npermalink: /{conf['folder']}/{safe_title}/\n---\n\n{content}")
            
            entry = {"text": title, "date": date.replace("-", "/"), "url": f"/{conf['folder']}/{safe_title}/", "page_id": p_id}
            yaml_data[cat]['issue'] = [i for i in yaml_data[cat]['issue'] if i.get('page_id') != p_id]
            yaml_data[cat]['issue'].append(entry)
            
            update_status(p_id, "Published")
            print(f"   ✅ [{cat}] 발행 완료: {title}")

        for cat, data in yaml_data.items():
            data['issue'].sort(key=lambda x: x['date'], reverse=True)
            with open(DATA_FILES[cat]["yaml"], 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    # ---------------------------------------------------------
    # [2] Publications 처리
    # ---------------------------------------------------------
    if DATABASE_ID_PUBS:
        print("\n[2] Publications 처리 중...")
        nested_pubs = {}
        featured_list = []

        if os.path.exists(PUBS_YAML_PATH):
            with open(PUBS_YAML_PATH, 'r', encoding='utf-8') as f:
                nested_pubs = yaml.safe_load(f) or {}
        if os.path.exists(FEATURED_YAML_PATH):
            with open(FEATURED_YAML_PATH, 'r', encoding='utf-8') as f:
                featured_list = yaml.safe_load(f) or []

        # --- [추가] 2-A. Unpublish 처리 ---
        unpublish_pubs = get_pages(DATABASE_ID_PUBS, "Unpublish")
        for p in unpublish_pubs:
            try:
                p_id = p["id"]
                # 1. 전체 Publications 목록에서 제거
                for year in list(nested_pubs.keys()):
                    for cat_key in ["journal", "conference"]:
                        if cat_key in nested_pubs[year] and nested_pubs[year][cat_key]:
                            nested_pubs[year][cat_key] = [x for x in nested_pubs[year][cat_key] if x.get('page_id') != p_id]
                    # 해당 연도에 논문이 하나도 안 남았으면 연도 삭제
                    if not nested_pubs[year].get("journal") and not nested_pubs[year].get("conference"):
                        del nested_pubs[year]
                
                # 2. Featured (선택된 연구) 목록에서 제거
                featured_list = [x for x in featured_list if x.get('page_id') != p_id]

                update_status(p_id, "Unpublished")
                print(f"   🗑️ 논문 숨김 처리 완료: {p_id}")
            except Exception as e:
                continue

        # --- 2-B. 신규 논문 발행 (Ready -> Published) ---
        pubs = get_pages(DATABASE_ID_PUBS, "Ready")
        count = 0
        for p in pubs:
            try:
                import copy
                props = p["properties"]
                # title_text = props["이름"]["title"][0]["plain_text"]
                # authors = props["Authors"]["rich_text"][0]["plain_text"]
                # venue = props["Venue"]["rich_text"][0]["plain_text"]
                title_text = parse_rich_text(props["이름"]["title"])
                authors = parse_rich_text(props["Authors"]["rich_text"])
                year = props["Year"]["number"]

                
                venue_data = copy.deepcopy(props["Venue"]["rich_text"])
                if venue_data:
                    # 가장 마지막 텍스트 덩어리에서 ', 2025' 같은 연도를 잘라냅니다 (실수로 뒤에 띄어쓰기가 있어도 커버함)
                    last_text = venue_data[-1]["plain_text"]
                    venue_data[-1]["plain_text"] = re.sub(rf'[,\s]+{year}\s*$', '', last_text)
                venue_clean = parse_rich_text(venue_data).strip()

                category_raw = props["Category"]["select"]["name"]
                selected = props["Selected"]["checkbox"]
                p_id = p["id"]
                
                cat_key = "conference" if "Conference" in category_raw else "journal"

                formatted_title = f"{title_text}. {venue_clean}, {year}"
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
                old_ids = {x['page_id'] for x in featured_list}
                if p_id not in old_ids:
                    featured_list.insert(0, {
                        "title": title_text,
                        "authors": authors,
                        "venue": venue_clean,
                        "year": year,
                        "page_id": p_id
                    })

            update_status(p_id, "Published")

        # 파일 저장
        sorted_pubs = dict(sorted(nested_pubs.items(), key=lambda item: item[0], reverse=True))
        with open(PUBS_YAML_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(sorted_pubs, f, allow_unicode=True, sort_keys=False)
            
        with open(FEATURED_YAML_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(featured_list, f, allow_unicode=True, sort_keys=False)
                
        if count > 0 or unpublish_pubs:
            print(f"   ✅ 신규 {count}건 업데이트, 숨김 {len(unpublish_pubs)}건 처리 완료")



        # ---------------------------------------------------------
    # [3] Website Pages (Professor, Home 등 단일 페이지) 처리
    # ---------------------------------------------------------
    if DATABASE_ID_PAGES:
        print("\n[3] Website Pages 처리 중...")
        
        # Unpublish 처리 (파일 삭제)
        unpublish_pages = get_pages(DATABASE_ID_PAGES, "Unpublish")
        for p in unpublish_pages:
            try:
                page_name = p["properties"]["Page Name"]["title"][0]["plain_text"]
                if page_name == "Professor":
                    if os.path.exists("professor/index.md"): os.remove("professor/index.md")
                elif page_name == "Home":
                    if os.path.exists("_includes/home_intro.md"): os.remove("_includes/home_intro.md")
                update_status(p["id"], "Draft")
            except: pass

        # 신규/수정 페이지 발행 (Ready -> Published)
        pages_to_update = get_pages(DATABASE_ID_PAGES, "Ready")
        print(pages_to_update)
        for p in pages_to_update:
            try:
                p_id = p["id"]
                page_name = p["properties"]["Page Name"]["title"][0]["plain_text"]
                
                # 본문 내용을 마크다운으로 변환 (이미지는 해당 페이지 이름의 폴더에 저장)
                blocks = get_block_children(p_id)
                content = blocks_to_markdown(blocks, f"assets/img/{page_name.lower()}", page_name.lower())
                print(page_name)
                # 페이지 이름에 따라 저장할 경로와 Front Matter 다르게 설정
                if page_name == "Professor":
                    # 섹션별 파싱 후 _data/professor.yml 로 저장
                    blocks = get_block_children(p_id)
                    sections = blocks_to_sections(blocks, "assets/img/professor", "prof")
                    
                    os.makedirs("_data", exist_ok=True)
                    with open("_data/professor.yml", "w", encoding="utf-8") as f:
                        yaml.dump(sections, f, allow_unicode=True, sort_keys=False)
                    
                    update_status(p_id, "Published")
                    print(f"   ✅ 페이지 업데이트 완료: {page_name}")
                    
                elif page_name == "Homeintro":
                    # Home 연구실 소개 부분은 메인 화면의 일부분이므로 _includes에 조각으로 저장
                    filepath = "_includes/home_intro.md"
                    os.makedirs("_includes", exist_ok=True)
                    full_content = content # 조각 파일이므로 Front Matter 생략
                    
                else:
                    continue # 다른 이름의 페이지는 무시
                
                # 파일 저장
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(full_content)
                    
                update_status(p_id, "Published")
                print(f"   ✅ 페이지 업데이트 완료: {page_name}")
            except Exception as e:
                print(f"   ⚠️ 페이지 업데이트 실패 ({page_name}): {e}")
                continue
        

        # ---------------------------------------------------------
    # [4] Members 처리
    # ---------------------------------------------------------
    if DATABASE_ID_MEMBERS:
        print("\n[4] Members 처리 중...")
        MEMBERS_YAML_PATH = "_data/members.yml"
        IMG_DIR_MEMBERS = "assets/img/members"
        os.makedirs(IMG_DIR_MEMBERS, exist_ok=True)
        
        # 기존 yml 데이터 읽기
        existing_members = []
        if os.path.exists(MEMBERS_YAML_PATH):
            with open(MEMBERS_YAML_PATH, 'r', encoding='utf-8') as f:
                existing_members = yaml.safe_load(f) or []

        # Unpublish 처리
        unpublish_members = get_pages(DATABASE_ID_MEMBERS, "Unpublish")
        for p in unpublish_members:
            existing_members = [m for m in existing_members if m.get("page_id") != p["id"]]
            update_status(p["id"], "Draft")
            
        # 신규/수정 페이지 (Ready -> Published)
        ready_members = get_pages(DATABASE_ID_MEMBERS, "Ready")
        print(ready_members)
        for p in ready_members:
            try:
                p_id = p["id"]
                props = p["properties"]
                
                name = props["이름"]["title"][0]["plain_text"]
                role = props["Role"]["select"]["name"] if props.get("Role", {}).get("select") else ""
                email = props["Email"]["email"] if props.get("Email", {}).get("email") else ""
                affiliation = "".join([t["plain_text"] for t in props.get("Affiliation", {}).get("rich_text", [])])
                year = props["Year"]["number"] if props.get("Year", {}).get("number") else None
                
                safe_name = re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_")
                
                # 프로필 이미지 다운로드
                profile_img_path = "/assets/img/default-avatar.png" # 사진이 없을 때 기본 이미지
                files = props["Profile"]["files"]
                if files:
                    f_url = files[0].get("file", {}).get("url") or files[0].get("external", {}).get("url")
                    if f_url:
                        downloaded = download_image(f_url, IMG_DIR_MEMBERS, f"profile_{safe_name}")
                        if downloaded: profile_img_path = downloaded
                        
                # 회사 로고 다운로드
                logo_img_path = None
                logo_files = props["Company_Logo"]["files"]
                if logo_files:
                    l_url = logo_files[0].get("file", {}).get("url") or logo_files[0].get("external", {}).get("url")
                    if l_url:
                        downloaded = download_image(l_url, IMG_DIR_MEMBERS, f"logo_{safe_name}")
                        if downloaded: logo_img_path = downloaded

                # 명단 갱신
                existing_members = [m for m in existing_members if m.get("page_id") != p_id]
                existing_members.append({
                    "name": name, "role": role, "email": email, "affiliation": affiliation,
                    "year": year, "image": profile_img_path, "company_logo": logo_img_path, "page_id": p_id
                })
                update_status(p_id, "Published")
                print(f"   ✅ 멤버 업데이트 완료: {name}")
            except Exception as e:
                print('Error',e)
                continue

        with open(MEMBERS_YAML_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(existing_members, f, allow_unicode=True, sort_keys=False)
    print("\n=== ✨ 모든 업데이트 완료 ===")

if __name__ == "__main__":
    main()