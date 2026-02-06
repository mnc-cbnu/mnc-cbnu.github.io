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
  /* 1. 헤더 영역 (제목 + 전체보기 링크) */
  .section-header {
    display: flex;
    justify-content: space-between; /* 양 끝 정렬 */
    align-items: flex-end; /* 글자 바닥 라인 맞춤 */
    margin-bottom: 20px;
    border-bottom: 2px solid #eee;
    padding-bottom: 10px;
  }
  .section-header h2 {
    margin: 0;
    font-size: 1.5rem;
    color: #333;
  }
  .view-all-link {
    font-size: 0.9rem;
    color: #666;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
  }
  .view-all-link:hover {
    color: #0056b3;
    text-decoration: underline;
  }

  /* 2. 슬라이더 컨테이너 (창문 역할) */
  .slider-viewport {
    width: 100%;
    overflow: hidden; /* 넘치는 것 숨김 */
    position: relative;
    padding: 10px 5px; /* 그림자 잘림 방지 여백 */
  }

  /* 3. 슬라이더 트랙 (기차 역할) */
  .slider-track {
    display: flex;
    gap: 20px; /* 카드 사이 간격 */
    transition: transform 0.5s ease-in-out; /* 부드러운 움직임 */
    width: max-content; /* 내용물만큼 길어짐 */
  }

  /* 4. 개별 카드 디자인 */
  .paper-card {
    background: white;
    width: 320px; /* 카드 고정 너비 (조절 가능) */
    flex-shrink: 0; /* 찌그러짐 방지 */
    border: 1px solid #eee;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 220px; /* 카드 고정 높이 */
    white-space: normal; /* 텍스트 줄바꿈 허용 */
  }

  .paper-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
  }

  /* 카드 내부 텍스트 */
  .pc-title {
    font-size: 1.05rem;
    font-weight: bold;
    color: #222;
    margin-bottom: 10px;

    /* 긴 제목 3줄까지만 보이고 ... 처리 */
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.4;
  }
  
  .pc-meta {
    margin-top: auto; /* 하단 고정 */
  }
  
  .pc-venue {
    color: #0056b3;
    font-weight: 600;
    font-size: 0.9rem;
    margin-bottom: 4px;
  }
  
  .pc-authors {
    font-size: 0.85rem;
    color: #777;

    /* 저자 1줄만 보이고 ... 처리 */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>

<div class="box area-papers">
  
  <div class="section-header">
    <h2>🏆 Selected Research</h2>
    <a href="/publications/" class="view-all-link">View all publications &rarr;</a>
  </div>

  {% if site.data.featured %}
  <div class="slider-viewport" id="paperSlider">
    <div class="slider-track" id="sliderTrack">

      {% for paper in site.data.featured limit:8 %}
      <div class="paper-card">
        <div class="pc-title">{{ paper.title }}</div>
        <div class="pc-meta">
          <div class="pc-venue">{{ paper.venue }}, {{ paper.year }}</div>
          <div class="pc-authors">{{ paper.authors }}</div>
        </div>
      </div>
      {% endfor %}

      {% for paper in site.data.featured limit:3 %}
      <div class="paper-card clone" aria-hidden="true">
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
  if (!track) return;

  const cardWidth = 340; // 카드너비(320) + 간격(20)
  const intervalTime = 3000; // 3초마다 이동
  let currentIndex = 0;
  
  // 실제 카드 개수 (복제된 것 제외)
  const totalSlides = track.querySelectorAll('.paper-card:not(.clone)').length;

  function moveSlider() {
    currentIndex++;
    track.style.transition = 'transform 0.5s ease-in-out';
    track.style.transform = `translateX(-${currentIndex * cardWidth}px)`;

    // 마지막에 도달하면 순식간에 처음으로 리셋 (무한 스크롤 효과)
    if (currentIndex >= totalSlides) {
      setTimeout(() => {
        track.style.transition = 'none'; // 애니메이션 끄고
        currentIndex = 0; // 0번으로 이동
        track.style.transform = `translateX(0px)`;
      }, 500); // 0.5s 애니메이션이 끝난 직후 실행
    }
  }

  // 자동 실행 시작
  let sliderInterval = setInterval(moveSlider, intervalTime);

  // 마우스 올리면 멈춤 / 떼면 다시 시작
  const sliderArea = document.getElementById('paperSlider');
  sliderArea.addEventListener('mouseenter', () => clearInterval(sliderInterval));
  sliderArea.addEventListener('mouseleave', () => sliderInterval = setInterval(moveSlider, intervalTime));
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