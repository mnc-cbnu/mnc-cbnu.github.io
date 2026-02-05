---
layout: default
title: Home
---


<div class="home-grid-container">
  
  <div class="box area-intro">
    <h2>👋 연구실 소개</h2>
    <p>
      충북대학교 모바일 네트워크 컴퓨팅 연구실(MNC Lab)입니다.<br>
      테두리가 제거되어 훨씬 깔끔하고 현대적인 느낌을 줍니다.
      내용에 집중할 수 있는 디자인입니다.
    </p>
  </div>

  <div class="box area-papers">
    <h2>📝 주요 연구 및 논문</h2>
    <p>최신 연구 성과를 이곳에 작성합니다.</p>
    <ul style="color: #555; padding-left: 20px; line-height: 1.6;">
      <li>2024, IEEE Access, "Advanced Mobile Computing Architectures..."</li>
      <li>2023, Sensors, "Efficient IoT Network Protocols..."</li>
    </ul>
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