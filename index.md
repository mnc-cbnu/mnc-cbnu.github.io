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

  <style>
  /* 1. 헤더 영역 */
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 20px;
    border-bottom: 2px solid #eee;
    padding-bottom: 10px;
  }
  .section-header h2 { margin: 0; font-size: 1.5rem; color: #333; }
  .view-all-link {
    font-size: 0.9rem; color: #666; text-decoration: none; font-weight: 500;
  }
  .view-all-link:hover { color: #0056b3; text-decoration: underline; }

  /* 2. 슬라이더 컨테이너 (창문) */
  .slider-viewport {
    width: 100%;
    overflow: hidden; /* 넘치는 것 숨김 */
    position: relative;
    padding: 10px 0;
    mask-image: linear-gradient(to right, transparent, black 5%, black 95%, transparent); /* 양끝을 흐릿하게 */
    -webkit-mask-image: linear-gradient(to right, transparent, black 5%, black 95%, transparent);
  }

  /* 3. 슬라이더 트랙 (움직이는 기차) */
  .slider-track {
    display: flex;
    gap: 20px;
    width: max-content; /* 내용물 길이만큼 늘어남 */
    /* 애니메이션 설정: 이름, 시간(속도), 가속도(일정하게), 반복 */
    animation: scroll-left 40s linear infinite;
  }

  /* 마우스 올리면 멈춤 */
  .slider-track:hover {
    animation-play-state: paused;
  }

  /* 4. 애니메이션 정의 (0%에서 -50%까지 이동) */
  @keyframes scroll-left {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
    /* 중요: JS로 내용을 2배로 불렸기 때문에 -50%가 되면 처음과 똑같은 위치가 됩니다. */
  }

  /* 5. 카드 디자인 */
  .paper-card {
    background: white;
    width: 320px;
    flex-shrink: 0;
    border: 1px solid #eee;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 220px;
    white-space: normal;
  }
  .paper-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
  }

  /* 텍스트 스타일 */
  .pc-title {
    font-size: 1.05rem; font-weight: bold; color: #222; margin-bottom: 10px;
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.4;
  }
  .pc-meta { margin-top: auto; }
  .pc-venue { color: #0056b3; font-weight: 600; font-size: 0.9rem; margin-bottom: 4px; }
  .pc-authors { font-size: 0.85rem; color: #777; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>

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