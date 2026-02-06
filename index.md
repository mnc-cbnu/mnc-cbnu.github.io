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

  <div class="box area-papers">
    <h2>🏆 Selected Research</h2>
    <p style="color:#666; margin-bottom: 20px;">
      Recent selected publications from our lab.
    </p>

    {% if site.data.featured %}
      <ul class="paper-list">
        {% for paper in site.data.featured limit:5 %}
          <li class="paper-item">
            <div class="paper-title">{{ paper.title }}</div>

            <div class="paper-meta">
              {{ paper.venue }}, {{ paper.year }}
            </div>
            
            <div class="paper-authors">{{ paper.authors }}</div>
          </li>
        {% endfor %}
      </ul>
      
      <a href="/publications/" class="more-link">View all publications &rarr;</a>
      
    {% else %}
      <p style="color: #999; padding: 20px 0;">
        업데이트 된 주요 논문이 없습니다.<br>
        (Notion에서 Selected 체크 후 업데이트 해주세요.)
      </p>
    {% endif %}
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

</div>

<!-- <h1>Welcome to MNC Lab</h1>
<p>Our lab focuses on wireless communications and networks...</p>
<div class="home-video">
  <video autoplay muted loop playsinline
         style="width:100%; max-height:500px; object-fit: contain;">
    <source src="/assets/videos/home_4x.mp4" type="video/mp4">
  </video>
</div> -->