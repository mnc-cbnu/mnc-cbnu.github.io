---
layout: default
title: Notice
permalink: /notice/
---

<div class="page-content">
  <div class="box">
    <h2 style="border-bottom: 2px solid #eee; padding-bottom: 15px; margin-bottom: 20px;">📢 Notice 전체 목록</h2>

    <div class="content-body">
      {% if site.categories.notice.size > 0 %}
        {% for post in site.categories.notice %}
          <a href="{{ post.url | relative_url }}" class="list-item">
            <span class="title">{{ post.title }}</span>
            <span class="date">{{ post.date | date: "%Y-%m-%d" }}</span>
          </a>
        {% endfor %}
      {% else %}
        <p style="padding: 10px 0; color: #888;">등록된 공지사항이 없습니다.</p>
      {% endif %}
    </div>
  </div>
</div>
