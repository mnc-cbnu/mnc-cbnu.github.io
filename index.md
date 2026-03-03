---
layout: default
title: Home
---

<div class="home-grid-container">
  
  <div class="box area-intro">
    <h2>👋 연구실 소개</h2>
    <p>
      충북대학교 모바일 네트워크 컴퓨팅 연구실(MNC Lab)입니다.<br>
    </p>
  </div>

  <div class="box area-notice">
    <h3>📢 공지사항</h3>
    <div class="content-body">
      {% if site.data.notice.issue %}
        {% for notice in site.data.notice.issue reversed limit:5 %}
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
    <h3>📰 NEWS</h3>
    <div class="content-body">
      {% if site.data.news.issue %}
        {% for new in site.data.news.issue reversed limit:5 %}
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
