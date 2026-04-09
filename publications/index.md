---
layout: default
title: Publications
permalink: /publications/
---


<style>
.publication-list {
  list-style: disc;
  /* marker 표시 */
  padding-left: 1.5em;
  /* marker와 글자 간격 */
  margin-bottom: 1em;
}

.publication-list li {
  margin-bottom: 0.5em;
}
hr {
  margin: 15px 0 !important; /* default.html의 40px 여백을 무시하고 15px로 확 줄입니다 */
  border-top: 1px solid #ddd;
}

details {
  margin-bottom: 5px; /* 연도 묶음 아래쪽 여백 줄이기 */
}

summary {
  cursor: pointer;
  padding: 5px 0; /* 연도 글씨 위아래 여백 조절 */
  font-size: 18px; /* 연도 글씨를 살짝 키워서 더 보기 좋게 만듭니다 */
}

/* 마우스를 올렸을 때 클릭할 수 있다는 느낌 주기 */
summary:hover {
  color: #0056b3;
}
</style>

<h1>Publications</h1>

{% assign years = site.data.publications %}

{% for year in years %}
<details {% if forloop.first %}open{% endif %}>
  <summary><strong>{{ year[0] }}</strong></summary>

  {% assign types = year[1] %}

  {% if types.journal %}
  <h3>Journal</h3>
  <ul class="publication-list">
    {% for paper in types.journal %}
    <li>
      <strong>{{ paper.title }}</strong><br>
      {{ paper.authors }}
    </li>
    {% endfor %}
  </ul>
  {% endif %}

  {% if types.conference %}
  <h3>Conference</h3>
  <ul class="publication-list">
    {% for paper in types.conference %}
    <li>
      <strong>{{ paper.title }}</strong><br>
      {{ paper.authors }}
    </li>
    {% endfor %}
  </ul>
  {% endif %}
</details>
<hr>
{% endfor %}


