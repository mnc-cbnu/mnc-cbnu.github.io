---
layout: default
title: Home
---
<style>
  .slider-viewport {
    overflow: hidden; /* 영역 밖으로 삐져나온 카드들 숨기기 */
    width: 100%;
    position: relative;
    padding-bottom: 10px;
  }
  
  .slider-track {
    display: flex;
    gap: 20px;
    width: max-content; /* 내용물 길이만큼 무한히 늘어남 */
    /* 30초 동안 일정한 속도(linear)로 무한(infinite) 반복 이동 */
    animation: scrolling 30s linear infinite;
  }
  
  /* 마우스를 올리면 슬라이드가 멈추도록 설정 (논문 읽기 편하게) */
  .slider-track:hover {
    animation-play-state: paused;
  }
  
  /* 절반(원본 데이터 길이)만큼 이동하고 다시 처음으로 훅 돌아오는 애니메이션 */
  @keyframes scrolling {
    0% { transform: translateX(0); }
    100% { transform: translateX(calc(-50% - 10px)); }
  }
  
  .paper-card {
    width: 300px; /* 카드 1개의 고정 너비 */
    border: 1px solid #eee;
    padding: 20px;
    border-radius: 8px;
    background: #fafafa;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    white-space: normal; /* 글씨가 길면 줄바꿈 되도록 설정 */
  }
  
  .pc-title { font-weight: bold; font-size: 15px; margin-bottom: 12px; color: #222; line-height: 1.4; }
  .pc-venue { color: #0056b3; font-weight: bold; font-size: 13px; margin-bottom: 4px; }
  .pc-authors { font-size: 13px; color: #666; }
</style>
<section style="margin-bottom: 50px; padding: 20px 10px; text-align: center;">
  
  {% for section in site.data.home_intro %}
    <h1 style="color: #0056b3; font-size: 32px; margin-bottom: 20px; border: none; padding: 0;">
      {{ section[0] }}
    </h1>
    <div style="font-size: 17px; color: #444; line-height: 1.8; max-width: 850px; margin: 0 auto;">
      {{ section[1] | newline_to_br }}
    </div>
  {% endfor %}

</section>

<div class="card-row" style="display: flex; gap: 30px; margin-bottom: 30px;">
  
  <section class="card" style="flex: 1; min-width: 0;">
    <div class="section-title">
      <span>📢 Notice</span>
      <a href="/notice/" class="view-all">View all →</a>
    </div>
    <div style="display: flex; flex-direction: column; gap: 15px;">

      {% if site.categories.notice.size > 0 %}
        {% for post in site.categories.notice limit:5 %}
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px;">
          <a href="{{ post.url | relative_url }}" style="text-decoration: none; color: #333; font-weight: 500; font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 75%;">
            {{ post.title }}
          </a>
          <span style="color: #888; font-size: 13px;">{{ post.date | date: "%Y.%m.%d" }}</span>
        </div>
        {% endfor %}
      {% else %}
        <p style="color: #999; font-size: 14px;">등록된 공지사항이 없습니다.</p>
      {% endif %}

    </div>
  </section>

  <section class="card" style="flex: 1; min-width: 0;">
    <div class="section-title">
      <span>📰 News</span>
      <a href="/news/" class="view-all">View all →</a>
    </div>
    <div style="display: flex; flex-direction: column; gap: 15px;">

      {% if site.categories.news.size > 0 %}
        {% for post in site.categories.news limit:5 %}
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px;">
          <a href="{{ post.url | relative_url }}" style="text-decoration: none; color: #333; font-weight: 500; font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 75%;">
            {{ post.title }}
          </a>
          <span style="color: #888; font-size: 13px;">{{ post.date | date: "%Y.%m.%d" }}</span>
        </div>
        {% endfor %}
      {% else %}
        <p style="color: #999; font-size: 14px;">등록된 뉴스가 없습니다.</p>
      {% endif %}

    </div>
  </section>

</div>

<section class="card">
  <div class="section-title">
    <span>🏆 Selected Research</span>
    <a href="/publications/" class="view-all">View all publications →</a>
  </div>
  
  <!-- {% assign featured_papers = site.data.publications | where: "selected", true %} -->
  
  {% if site.data.featured %}
    <div class="slider-viewport">
      <div class="slider-track" id="sliderTrack">

        {% for paper in site.data.featured limit:10 %}
        <div class="paper-card">
          <div class="pc-title">
            {% if paper.link != "" %}
              <a href="{{ paper.link }}" target="_blank" style="text-decoration: none; color: inherit;">{{ paper.title }}</a>
            {% else %}
              {{ paper.title }}
            {% endif %}
          </div>
          <div class="pc-meta">
            <div class="pc-venue">{{ paper.venue }}, {{ paper.year }}</div>
            <div class="pc-authors">{{ paper.authors }}</div>
          </div>
        </div>
        {% endfor %}
        
      </div>
    </div>
  {% else %}
    <p style="color:#999; padding:20px;">선택된 논문이 없습니다.</p>
  {% endif %}
  
  <script>
  document.addEventListener("DOMContentLoaded", function() {
    const track = document.getElementById('sliderTrack');
    if (track) {
      // 트랙 안의 내용을 그대로 한 번 더 복사해서 뒤에 붙임
      const originalContent = track.innerHTML;
      track.innerHTML += originalContent;
    }
  });
  </script>
</section>
