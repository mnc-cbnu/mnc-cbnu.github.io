import os
import requests
import json
import yaml
import re
import traceback
import glob  # 추가된 모듈: 파일 검색용


NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID_NAV = os.environ.get("DATABASE_ID_NAV")
DATABASE_ID_MEMBERS = os.environ.get("DATABASE_ID_MEMBERS")
DATABASE_ID_BOARD = os.environ.get("DATABASE_ID_BOARD")
DATABASE_ID_PAGES = os.environ.get("DATABASE_ID_PAGES")
DATABASE_ID_PUB = os.environ.get("DATABASE_ID_PUB")



headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_pages(database_id, status):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {"filter": {"property": "Status", "status": {"equals": status}}}
    res = requests.post(url, json=payload, headers=headers)
    if res.status_code == 200:
        return res.json().get("results", [])
    return []

def update_status(page_id, new_status):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": {"Status": {"status": {"name": new_status}}}}
    requests.patch(url, json=payload, headers=headers)

def download_image(img_url, save_dir, filename):
    try:
        res = requests.get(img_url)
        if res.status_code == 200:
            content_type = res.headers.get('Content-Type', '')
            ext = '.png' if 'png' in content_type else '.jpg'
            if not filename.endswith(('.png', '.jpg', '.jpeg')):
                filename += ext
            filepath = os.path.join(save_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(res.content)
            return filepath
    except:
        pass
    return None

def blocks_to_markdown(blocks, save_dir="assets/img", prefix=""):
    md_content = ""
    for b in blocks:
        try:
            b_type = b["type"]
            if b_type == "paragraph":
                rich_text = b["paragraph"].get("rich_text", [])
                text = "".join([t["plain_text"] for t in rich_text])
                md_content += f"{text}\n\n"
            elif b_type == "heading_1":
                text = "".join([t["plain_text"] for t in b["heading_1"].get("rich_text", [])])
                md_content += f"# {text}\n\n"
            elif b_type == "heading_2":
                text = "".join([t["plain_text"] for t in b["heading_2"].get("rich_text", [])])
                md_content += f"## {text}\n\n"
            elif b_type == "heading_3":
                text = "".join([t["plain_text"] for t in b["heading_3"].get("rich_text", [])])
                md_content += f"### {text}\n\n"
            elif b_type == "bulleted_list_item":
                text = "".join([t["plain_text"] for t in b["bulleted_list_item"].get("rich_text", [])])
                md_content += f"* {text}\n"
            elif b_type == "image":
                img_url = b["image"].get("file", {}).get("url") or b["image"].get("external", {}).get("url")
                if img_url:
                    img_filename = f"{prefix}_img_{b['id'][:8]}" if prefix else f"img_{b['id'][:8]}"
                    local_img_path = download_image(img_url, save_dir, img_filename)
                    if local_img_path:
                        md_content += f"![image](/{local_img_path})\n\n"
        except Exception as e:
            continue
    return md_content

def parse_rich_text(rich_text_array):
    if not rich_text_array: return ""
    result = ""
    for t in rich_text_array:
        text = t.get("plain_text", "")
        anns = t.get("annotations", {})
        if anns.get("bold"): text = f"**{text}**"
        if anns.get("italic"): text = f"*{text}*"
        if anns.get("code"): text = f"`{text}`"
        
        color = anns.get("color", "default")
        if color != "default" and "background" not in color:
            text = f'<span style="color:{color}">{text}</span>'
            
        href = t.get("href")
        if href: text = f"[{text}]({href})"
        
        result += text
    return result


if __name__ == "__main__":
    os.makedirs("_data", exist_ok=True)

    # ---------------------------------------------------------
    # [1] 메뉴(Navigation) 처리
    # ---------------------------------------------------------
    if DATABASE_ID_NAV:
        print("\n[1] 메뉴(Navigation) 처리 중...")
        nav_items = []
        nav_yaml_path = "_data/navigation.yml"
        
        if os.path.exists(nav_yaml_path):
            with open(nav_yaml_path, 'r', encoding='utf-8') as f:
                loaded = yaml.safe_load(f)
                if loaded: nav_items = loaded

        # --- 1-A. Unpublish 처리 ---
        unpublish_navs = get_pages(DATABASE_ID_NAV, "Unpublish")
        for p in unpublish_navs:
            try:
                nav_items = [item for item in nav_items if item.get("id") != p["id"]]
                update_status(p["id"], "Unpublished")
                print(f"   🗑️ 메뉴 숨김 처리 완료: {p['id']}")
            except Exception: continue

        # --- 1-B. Ready 처리 ---
        for p in get_pages(DATABASE_ID_NAV, "Ready"):
            try:
                props = p["properties"]
                name = props["Menu Name"]["title"][0]["plain_text"]
                link = props.get("Link", {}).get("rich_text", [{"plain_text": ""}])[0]["plain_text"]
                order = props.get("Order", {}).get("number") or 999
                show_in_menu = props.get("Show in Menu", {}).get("checkbox", True)
                
                nav_items = [item for item in nav_items if item.get("id") != p["id"]]
                nav_items.append({
                    "name": name, "link": link, "order": order, "id": p["id"], "show_in_menu": show_in_menu
                })

                if link.startswith("/") and len(link) > 1:
                    folder_name = link.strip("/")
                    os.makedirs(folder_name, exist_ok=True)
                    file_path = f"{folder_name}/index.md"
                    blocks_url = f"https://api.notion.com/v1/blocks/{p['id']}/children"
                    blocks = requests.get(blocks_url, headers=headers).json().get("results", [])
                    content = blocks_to_markdown(blocks, save_dir="assets/img")
                    front_matter = f"---\nlayout: default\ntitle: {name}\npermalink: {link}\n---\n\n"

                    if content.strip():
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(front_matter + content)
                    elif not os.path.exists(file_path):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(front_matter + "\n")
                        
                update_status(p["id"], "Published")
                print(f"   ✅ 메뉴 등록 완료: {name}")
            except Exception as e:
                print(f"   ⚠️ 메뉴 업데이트 실패: {e}")
                continue
            
        nav_items.sort(key=lambda x: x["order"])
        with open(nav_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(nav_items, f, allow_unicode=True, sort_keys=False)


    # ---------------------------------------------------------
    # [2] 단일 페이지(Pages DB - Home, Professor 등) 처리
    # ---------------------------------------------------------
    if DATABASE_ID_PAGES:
        print("\n[2] 단일 페이지(Pages) 처리 중...")

        # --- 2-A. Unpublish 처리 ---
        unpublish_pages = get_pages(DATABASE_ID_PAGES, "Unpublish")
        for p in unpublish_pages:
            try:
                props = p["properties"]
                page_name = props["Page Name"]["title"][0]["plain_text"].lower().replace(" ", "_")
                file_path = f"_data/{page_name}.yml"
                if os.path.exists(file_path):
                    os.remove(file_path) # YAML 파일 삭제
                update_status(p["id"], "Unpublished")
                print(f"   🗑️ 페이지 숨김 처리 완료: {page_name}")
            except Exception: continue

        # --- 2-B. Ready 처리 ---
        for p in get_pages(DATABASE_ID_PAGES, "Ready"):
            try:
                props = p["properties"]
                page_name = props["Page Name"]["title"][0]["plain_text"]
                safe_name = page_name.lower().replace(" ", "_")
                yaml_path = f"_data/{safe_name}.yml"

                blocks_url = f"https://api.notion.com/v1/blocks/{p['id']}/children"
                blocks = requests.get(blocks_url, headers=headers).json().get("results", [])
                
                sections = []
                current_heading = "Intro"
                current_content = ""
                
                for b in blocks:
                    b_type = b["type"]
                    if b_type.startswith("heading"):
                        if current_content.strip():
                            sections.append([current_heading, current_content.strip()])
                        current_heading = "".join([t["plain_text"] for t in b[b_type].get("rich_text", [])])
                        current_content = ""
                    else:
                        current_content += blocks_to_markdown([b], save_dir="assets/img")
                if current_content.strip():
                    sections.append([current_heading, current_content.strip()])

                with open(yaml_path, 'w', encoding='utf-8') as f:
                    yaml.dump(sections, f, allow_unicode=True, sort_keys=False)

                update_status(p["id"], "Published")
                print(f"   ✅ 페이지 업데이트 완료: {page_name}")
            except Exception as e:
                print(f"   ⚠️ 페이지 업데이트 실패: {e}")
                continue


    # ---------------------------------------------------------
    # [3] Members (구성원) 처리
    # ---------------------------------------------------------
    if DATABASE_ID_MEMBERS:
        print("\n[3] 구성원(Members) 처리 중...")
        members_dict = {}
        members_yaml_path = "_data/members.yml"
        
        # 1. 기존 데이터 불러오기 (Dict 형태 보장)
        if os.path.exists(members_yaml_path):
            with open(members_yaml_path, 'r', encoding='utf-8') as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    members_dict = loaded

        # 보조 함수: 특정 id를 가진 멤버를 모든 카테고리에서 안전하게 제거
        def remove_member_by_id(m_id, m_dict):
            for cat in list(m_dict.keys()):
                m_dict[cat] = [m for m in m_dict[cat] if m.get("id") != m_id]
                if not m_dict[cat]: # 멤버가 한 명도 안 남은 카테고리는 삭제
                    del m_dict[cat]

        # --- 3-A. Unpublish 처리 ---
        unpublish_members = get_pages(DATABASE_ID_MEMBERS, "Unpublish")
        for p in unpublish_members:
            try:
                remove_member_by_id(p["id"], members_dict)
                update_status(p["id"], "Unpublished")
                print(f"   🗑️ 멤버 숨김 처리 완료: {p['id']}")
            except Exception: continue

        # --- 3-B. Ready 처리 ---
        for p in get_pages(DATABASE_ID_MEMBERS, "Ready"):
            try:
                props = p["properties"]
                
                # 노션 속성값 안전하게 추출 (올려주신 사진 기준)
                name_prop = props.get("Name", {}).get("title", [])
                name = name_prop[0].get("plain_text", "Unknown") if name_prop else "Unknown"
                
                role = props.get("Role", {}).get("select", {}).get("name", "")
                email = props.get("Email", {}).get("email") or ""
                year = props.get("Year", {}).get("number")
                order = props.get("Order", {}).get("number") or 999
                
                affiliation_prop = props.get("Affiliation", {}).get("rich_text", [])
                affiliation = affiliation_prop[0].get("plain_text", "") if affiliation_prop else ""

                # 💡 사진 처리 (Profile Image)
                image_url = ""
                # 속성 이름이 "Profile Image" 또는 "Photo" 일 경우 모두 대비
                img_key = "Profile Image" if "Profile Image" in props else "Photo"
                if img_key in props and props[img_key].get("files"):
                    file_info = props[img_key]["files"][0]
                    img_url_raw = file_info.get("file", {}).get("url") or file_info.get("external", {}).get("url")
                    if img_url_raw:
                        img_filename = f"profile_{name}.jpg"
                        local_path = download_image(img_url_raw, "assets/img/members", img_filename)
                        if local_path: image_url = f"/{local_path}"

                # 💡 회사 로고 처리 (Company Logo)
                company_logo = ""
                if "Company Logo" in props and props["Company Logo"].get("files"):
                    file_info = props["Company Logo"]["files"][0]
                    img_url_raw = file_info.get("file", {}).get("url") or file_info.get("external", {}).get("url")
                    if img_url_raw:
                        img_filename = f"logo_{name.replace(' ','_')}.png" # 로고는 보통 png 유지
                        local_path = download_image(img_url_raw, "assets/img/members", img_filename)
                        if local_path: company_logo = f"/{local_path}"

                # 💡 [핵심] 그룹화(Category) 로직
                # Year(연도)가 입력되어 있으면 'Alumni', 없으면 Role(예: Ph.D. Student)을 그룹명으로 사용!
                
                category = "Alumni" if year else "Current"

                # 기존 카테고리에서 멤버 삭제 후 새 위치에 추가
                remove_member_by_id(p["id"], members_dict)
                if category not in members_dict:
                    members_dict[category] = []
                    
                members_dict[category].append({
                    "id": p["id"], 
                    "name": name, 
                    "role": role,
                    "email": email, 
                    "image": image_url,
                    "year": year,
                    "affiliation": affiliation,
                    "company_logo": company_logo,
                    "order": order
                })

                update_status(p["id"], "Published")
                print(f"   ✅ 멤버 업데이트: [{category}] {name}")
            except Exception as e:
                print(f"   ⚠️ 멤버 업데이트 실패: {e}")
                traceback.print_exc() # 에러 상세 원인 출력
                continue

        # 각 그룹 내에서 Order 순으로 정렬
        for cat in members_dict:
            members_dict[cat].sort(key=lambda x: x.get("order", 999))
            
        with open(members_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(members_dict, f, allow_unicode=True, sort_keys=False)


    # ---------------------------------------------------------
    # [4] Lab Board (News, Notice) 처리 -> Markdown 파일 방식
    # ---------------------------------------------------------
    if DATABASE_ID_BOARD:
        print("\n[4] 통합 게시판(Lab Board) 처리 중...")
        os.makedirs("_posts", exist_ok=True)
        os.makedirs("assets/img/board", exist_ok=True)

        # --- 4-A. Unpublish 처리 ---
        unpublish_board = get_pages(DATABASE_ID_BOARD, "Unpublish")
        for p in unpublish_board:
            try:
                p_id = p["id"].replace("-", "")
                # _posts 폴더 하위의 모든 폴더(news, notice 등)에서 해당 고유 ID를 가진 md 파일 검색 및 삭제
                files_to_delete = glob.glob(f"_posts/*/*_{p_id}.md")
                for f_path in files_to_delete:
                    if os.path.exists(f_path):
                        os.remove(f_path)
                update_status(p["id"], "Unpublished")
                print(f"   🗑️ 게시물 숨김 처리 완료: {p_id}")
            except Exception: continue

        # --- 4-B. Ready 처리 ---
        for p in get_pages(DATABASE_ID_BOARD, "Ready"):
            try:
                props = p["properties"]
                title = props["Title"]["title"][0]["plain_text"]
                category = props.get("Category", {}).get("select", {}).get("name", "News").lower()
                
                category_dir = f"_posts/{category}"
                os.makedirs(category_dir, exist_ok=True)
                
                date_str = props.get("Date", {}).get("date", {}).get("start", "")
                if not date_str:
                    date_str = p.get("created_time", "")
                
                file_date = date_str[:10]
                safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "-")
                p_id = p["id"].replace("-", "")
                file_name = f"{category_dir}/{file_date}-{safe_title}_{p_id}.md"
                
                blocks_url = f"https://api.notion.com/v1/blocks/{p['id']}/children"
                blocks = requests.get(blocks_url, headers=headers).json().get("results", [])
                
                content = blocks_to_markdown(blocks, save_dir="assets/img/board", prefix=p_id)
                front_matter = f"---\nlayout: post\ntitle: \"{title}\"\ndate: {date_str}\ncategory: {category}\n---\n\n"
                
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(front_matter + content)
                    
                update_status(p["id"], "Published")
                print(f"   ✅ 게시물 업데이트: [{category}] {title}")
            except Exception as e:
                print(f"   ⚠️ 게시물 업데이트 실패: {e}")
                continue


    # ---------------------------------------------------------
    # [5] Publications (논문) 처리
    # ---------------------------------------------------------
    if DATABASE_ID_PUB:
        print("\n[5] 논문(Publications) 처리 중...")
        PUBS_YAML_PATH = "_data/publications.yml"
        FEATURED_YAML_PATH = "_data/featured.yml"
        
        nested_pubs = {}
        featured_list = []

        if os.path.exists(PUBS_YAML_PATH):
            with open(PUBS_YAML_PATH, 'r', encoding='utf-8') as f:
                nested_pubs = yaml.safe_load(f) or {}
        if os.path.exists(FEATURED_YAML_PATH):
            with open(FEATURED_YAML_PATH, 'r', encoding='utf-8') as f:
                featured_list = yaml.safe_load(f) or []

        # --- 5-A. Unpublish 처리 ---
        unpublish_pubs = get_pages(DATABASE_ID_PUB, "Unpublish")
        for p in unpublish_pubs:
            try:
                p_id = p["id"]
                for year in list(nested_pubs.keys()):
                    for cat_key in ["journal", "conference"]:
                        if cat_key in nested_pubs[year] and nested_pubs[year][cat_key]:
                            nested_pubs[year][cat_key] = [x for x in nested_pubs[year][cat_key] if x.get('page_id') != p_id]
                    if not nested_pubs[year].get("journal") and not nested_pubs[year].get("conference"):
                        del nested_pubs[year]
                
                featured_list = [x for x in featured_list if x.get('page_id') != p_id]
                update_status(p_id, "Unpublished")
                print(f"   🗑️ 논문 숨김 처리 완료: {p_id}")
            except Exception as e: continue

        # --- 5-B. Ready 처리 ---
        pubs = get_pages(DATABASE_ID_PUB, "Ready")
        count = 0
        for p in pubs:
            try:
                import copy
                props = p["properties"]
                title_prop = props.get("Title") or props.get("이름")
                title_text = parse_rich_text(title_prop["title"]) if title_prop else "제목 없음"
                authors = parse_rich_text(props.get("Authors", {}).get("rich_text", []))
                
                year_data = props.get("Year", {}).get("number")
                year = str(int(year_data)) if year_data else "9999"

                venue_data = copy.deepcopy(props.get("Venue", {}).get("rich_text", []))
                if venue_data:
                    last_text = venue_data[-1]["plain_text"]
                    venue_data[-1]["plain_text"] = re.sub(rf'[,\s]+{year}\s*$', '', last_text)
                venue_clean = parse_rich_text(venue_data).strip()

                category_raw = props.get("Category", {}).get("select", {}).get("name", "Journal")
                
                sel_prop = props.get("Selected", {})
                if "checkbox" in sel_prop:
                    selected = sel_prop["checkbox"]
                else:
                    selected = sel_prop.get("select", {}).get("name", "").lower() == "yes"

                p_id = p["id"]
                cat_key = "conference" if "Conference" in category_raw else "journal"
                formatted_title = f"{title_text}. {venue_clean}, {year}"

                if year not in nested_pubs: nested_pubs[year] = {"journal": [], "conference": []}
                if cat_key not in nested_pubs[year]: nested_pubs[year][cat_key] = []
                if nested_pubs[year][cat_key] is None: nested_pubs[year][cat_key] = []

                nested_pubs[year][cat_key] = [x for x in nested_pubs[year][cat_key] if x.get('page_id') != p_id]
                nested_pubs[year][cat_key].append({"title": formatted_title, "authors": authors, "page_id": p_id})
                count += 1
            
                featured_list = [x for x in featured_list if x.get('page_id') != p_id]
                if selected:
                    featured_list.insert(0, {
                        "title": title_text,
                        "authors": authors,
                        "venue": venue_clean,
                        "year": year,
                        "page_id": p_id
                    })

                update_status(p_id, "Published")
                print(f"   ✅ 논문 업데이트: {title_text}")
            except Exception as e:
                print(f"   ⚠️ 논문 업데이트 실패: {e}")
                continue

        sorted_pubs = dict(sorted(nested_pubs.items(), key=lambda item: str(item[0]), reverse=True))
        with open(PUBS_YAML_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(sorted_pubs, f, allow_unicode=True, sort_keys=False)
            
        with open(FEATURED_YAML_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(featured_list, f, allow_unicode=True, sort_keys=False)