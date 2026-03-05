---
layout: default
title: News
---

<div class="page-content">
  <div class="box">
    <h2 style="border-bottom: 2px solid #eee; padding-bottom: 15px; margin-bottom: 20px;">📰 News 전체 목록</h2>

    <div class="content-body">
      {% if site.data.news.issue %}
        {% for item in site.data.news.issue %}
          <a href="{{ item.url | default: '#' | relative_url }}" class="list-item" style="padding: 15px 0;">
            <span style="font-size: 1.05rem; font-weight: 500; color: #333;">{{ item.text }}</span>
            <span class="date">{{ item.date }}</span>
          </a>
        {% endfor %}
      {% else %}
        <p style="padding: 10px 0; color: #888;">등록된 뉴스가 없습니다.</p>
      {% endif %}
    </div>
  </div>
</div>
