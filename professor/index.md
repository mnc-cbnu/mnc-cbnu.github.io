---
layout: default
title: Professor
permalink: /professor/
---


<style>
  /* 1. 상단 프로필 영역 (사진과 텍스트를 양옆으로 배치) */
  
  .profile-header {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 30px;
    margin-bottom: 30px;
    flex-wrap: wrap;
  }

  .profile-photo {

    width: 100vw;
    max-width: 400px;
    /* width: 500px; */
    border-radius: 8px;
  }

  .profile-info h1 {
    margin-bottom: 5px;
  }
  /* 2. 하단 다단(Grid) 레이아웃 */
  .two-col {
    display: grid;
    /* 화면 크기에 따라 1줄에 1~2개씩 유동적으로 배치 */
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
    /* margin-top: 30px; */
  }
  
  /* 첨부하신 사진처럼 카드 안의 제목(h2)에 검은 밑줄 추가 */
  .two-col .card h2 {
    color: #111;
    font-size: 20px;
    border-bottom: 2px solid #222; /* 검은색 밑줄 */
    padding-bottom: 10px;
    margin-top: 0;
    margin-bottom: 15px;
  }

  /* 모바일 화면(768px 이하)일 때는 사진과 글이 위아래로 나오도록 처리 */
  @media (max-width: 768px) {
    .profile-header { flex-direction: column; }
    .profile-photo { width: 100%; max-width: 100%; }
  }
</style>
<div class="profile-header">
  <img src="{{ site.data.professor.Profile_Image | relative_url }}" class="profile-photo">
  <div class="profile-info">
    {{ site.data.professor.Profile | markdownify }}
  </div>
</div>

<hr>

<div class="two-col">
  {% for section in site.data.professor %}
    {% comment %} Profile과 사진 데이터는 위에서 썼으니 제외하고 반복 {% endcomment %}
    {% if section[0] != 'Profile' and section[0] != 'Profile_Image' %}
      <div class="card">
        <h2>{{ section[0] }}</h2>
        {{ section[1] | markdownify }}
      </div>
    {% endif %}
  {% endfor %}
</div>


