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

.card-content ul, .card-content ol {
margin-top: 5px;
margin-bottom: 20px;
padding-left: 25px; /* 글머리 기호 안쪽 여백 */
}

.card-content li {
margin-bottom: 10px; /* 리스트 항목들 사이의 넉넉한 여백 */
line-height: 1.8;
}

@media (max-width: 768px) {

/* 1. 💡 핵심: 홈페이지 전체의 80% 너비 제한을 풀고 100% 꽉 채우기 */  

  .container {

max-width: 100% !important;

padding: 0 10px !important; /* 모바일 화면 양끝 여백 최소화 */

}
    /* 2. 카드 안쪽 여백 대폭 축소 (내용물이 들어갈 공간 확보) */

.card {

padding: 20px 15px; /* 위아래 20px, 좌우 15px로 확 줄임 */

     border-radius: 8px;  

  }
    /* 3. 카드 사이의 간격 줄이기 */

 .research-container {

  gap: 20px;

 margin-top: 10px;

 }
    /* 4. 제목 크기 모바일에 맞게 축소 */

.card h2 {

       font-size: 19px;

      margin-bottom: 15px;

     padding-bottom: 8px;

 }
    /* 5. 이미지 아래 여백 축소 */

.card img {

     margin-bottom: 15px;

 }
    /* 6. 텍스트 좌측 정렬 (모바일에서는 양쪽 정렬 시 글씨 사이가 벌어져 어색함) */

 .card-content {

      font-size: 15px; /* 모바일 전용으로 글씨 크기 약간 축소 */  

    line-height: 1.6;      text-align: left !important; /* 무조건 좌측 정렬 */

 }
    /* 7. 리스트(-) 들여쓰기 여백 최적화 */

    .card-content ul, .card-content ol {

     padding-left: 20px;

      margin-bottom: 15px;

    }

        .card-content li {

      margin-bottom: 8px;

    }

  }

</style>

<div class="page-content" style="max-width: 1000px; margin: 0 auto; padding: 20px;">

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
