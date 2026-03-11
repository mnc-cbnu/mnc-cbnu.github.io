---
layout: default
title: Home
---

<div class="home-grid-container">
  
<div class="box area-intro">
    {% capture home_intro_content %}{% include home_intro.md %}{% endcapture %}
    {{ home_intro_content | markdownify }}
  </div>

  <div class="box area-notice">
    <div class="section-header" style="border-bottom: none; margin-bottom: 10px; padding-bottom: 0;">
      <h3 style="margin: 0;">📢 공지사항</h3>
      <a href="/notice/" class="view-all-link">View all &rarr;</a>
    </div>
    <div class="content-body">
      {% if site.data.notice.issue %}
        {% for notice in site.data.notice.issue limit:5 %}
          <a href="{{ notice.url | default: '#' | relative_url }}" class="list-item">
            <span>{{ notice.text }}</span>
            <span class="date">{{ notice.date }}</span>
          </a>
        {% endfor %}
      {% else %}
        <p style="padding: 10px 0; color: #888;">등록된 공지사항이 없습니다.</p>
      {% endif %}
    </div>
  </div>

  <div class="box area-news">
    <div class="section-header" style="border-bottom: none; margin-bottom: 10px; padding-bottom: 0;">
      <h3>📰 NEWS</h3>
      <a href="/news/" class="view-all-link">View all &rarr;</a>
    </div>
    <div class="content-body">
      {% if site.data.news.issue %}
        {% for new in site.data.news.issue limit:5 %}
          <a href="{{ new.url | default: '#' | relative_url }}" class="list-item">
            <span>{{ new.text }}</span>
            <span class="date">{{ new.date }}</span>
          </a>
        {% endfor %}
      {% else %}
        <p style="padding: 10px 0; color: #888;">등록된 뉴스가 없습니다.</p>
      {% endif %}
    </div>
  </div>

  <div class="box area-papers">
    <div class="section-header">
      <h2>🏆 Selected Research</h2>
      <a href="/publications/" class="view-all-link">View all publications &rarr;</a>
    </div>

    {% if site.data.featured %}
    <div class="slider-viewport">
      <div class="slider-track" id="sliderTrack">
        {% for paper in site.data.featured limit:10 %}
        <div class="paper-card">
          <div class="pc-title">{{ paper.title }}</div>
          <div class="pc-meta">
            <div class="pc-venue">{{ paper.venue }}, {{ paper.year }}</div>
            <div class="pc-authors">{{ paper.authors }}</div>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
    {% else %}
      <p style="color:#999; padding:20px;">업데이트된 논문이 없습니다.</p>
    {% endif %}
  </div>

  <script>
  document.addEventListener("DOMContentLoaded", function() {
    const track = document.getElementById('sliderTrack');
    if (track) {
      // 트랙 안의 내용을 그대로 한 번 더 복사해서 뒤에 붙임 (무한 루프 구현용)
      const originalContent = track.innerHTML;
      track.innerHTML += originalContent;
    }
  });
  </script>

</div>
