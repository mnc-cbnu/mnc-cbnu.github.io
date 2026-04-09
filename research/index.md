---
layout: default
title: Research
permalink: /research/
---

<style>
/* 연구 분야를 위에서 아래로 순서대로 배치 /
.research-container {
display: flex;
flex-direction: column;
gap: 40px; / 각 연구 분야 카드 사이의 간격 */
margin-top: 20px;
}

/* 개별 연구 분야 카드 디자인 */
.card {
background: #f9f9fc;
padding: 40px;
border-radius: 12px;
box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

/* 카드 안의 제목 (검은색 밑줄) */
.card h2 {
color: #111;
font-size: 24px;
border-bottom: 2px solid #222;
padding-bottom: 10px;
margin-top: 0;
margin-bottom: 25px;
}

/* 💡 핵심: 노션에서 넣은 이미지가 카드 밖으로 삐져나가지 않게 자동 조절 /
.card img {
max-width: 100%;
height: auto;
border-radius: 8px;
display: block;
margin: 0 auto 20px auto; / 이미지 가운데 정렬 및 아래 여백 */
}

/* 모바일 화면 대응 */
@media (max-width: 768px) {
.card { padding: 20px; }
.card h2 { font-size: 20px; }
}
</style>

<div class="page-content" style="max-width: 1500px; margin: 0 auto; padding: 20px;">

<h1 style="color: #0056b3; font-size: 32px; margin-bottom: 30px; text-align: center;">
Research Areas
</h1>

<div class="research-container">
{% for section in site.data.research %}
<div class="card">
<h2>{{ section[0] }}</h2>
<div style="font-size: 16px; color: #444; line-height: 1.8; word-break: keep-all;">
{{ section[1] | markdownify }}
</div>
</div>
{% endfor %}
</div>

</div>

