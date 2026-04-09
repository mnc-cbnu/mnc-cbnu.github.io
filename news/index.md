---
layout: default
title: News
permalink: /news
---

<div class="page-content">
  <div class="box">
    <h2 style="border-bottom: 2px solid #eee; padding-bottom: 15px; margin-bottom: 20px;">📰 News 전체 목록</h2>

    <div class="content-body">
      {% if site.categories.news.size > 0 %}
        {% for post in site.categories.news %}
          <a href="{{ post.url | relative_url }}" class="list-item">
            <span class="title">{{ post.title }}</span>
            <span class="date">{{ post.date | date: "%Y-%m-%d" }}</span>
          </a>
        {% endfor %}
      {% else %}
        <p style="padding: 10px 0; color: #888;">등록된 뉴스가 없습니다.</p>
      {% endif %}
    </div>
  </div>
</div>
