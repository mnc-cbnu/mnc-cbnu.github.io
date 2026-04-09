---
layout: default
title: Research
permalink: /research/
---

<style>
.research-container {
display: flex;
flex-direction: column;
gap: 40px;
margin-top: 20px;
}

.card {
background: #f9f9fc;
padding: 40px;
border-radius: 12px;
box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.card h2 {
color: #111;
font-size: 24px;
border-bottom: 2px solid #222;
padding-bottom: 10px;
margin-top: 0;
margin-bottom: 25px;

text-align: center;
}



/* 💡 1. 사진 디자인 (아래쪽 여백 30px 자동 추가!) /
.card img {
max-width: 100%;
height: auto;
border-radius: 8px;
display: block;
margin: 0 auto 30px auto; / 👈 여기서 사진 아래 여백을 넉넉히 줍니다 /
box-shadow: 0 4px 10px rgba(0,0,0,0.06); / 사진에 살짝 입체감 추가 */
}

/* 💡 2. 텍스트 디자인 (너비 제한 및 양쪽 정렬로 논문처럼 깔끔하게!) /
.card-content {
max-width: 850px; / 텍스트가 사진 끝까지 꽉 차지 않도록 제한 /
margin: 0 auto;   / 텍스트 박스를 가운데 정렬 /
font-size: 16.5px;
color: #444;
line-height: 1.8;
word-break: keep-all;
text-align: justify; / 양쪽 끝을 가지런하게 맞춤 */
}

/* 노션에서 친 엔터(문단 바꿈) 사이의 여백 설정 */
.card-content p {
margin-bottom: 15px;
}

@media (max-width: 768px) {
.card { padding: 20px; }
.card h2 { font-size: 20px; }
.card-content { text-align: left; } /* 모바일은 좌측 정렬이 읽기 편함 */
}
</style>

<div class="page-content" style="max-width: 1000px; margin: 0 auto; padding: 20px;">

<h1 style="color: #0056b3; font-size: 32px; margin-bottom: 40px; text-align: center;">
Research Areas
</h1>

<div class="research-container">
{% for section in site.data.research %}
<div class="card">
<h2>{{ section[0] }}</h2>
<div class="card-content">
{{ section[1] | markdownify }}
</div>
</div>
{% endfor %}
</div>

</div>

