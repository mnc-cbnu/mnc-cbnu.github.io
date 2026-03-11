---
layout: default
title: Professor
permalink: /professor/
---

<div class="profile-header">
  <img src="{{ site.data.professor.Profile_Image | relative_url }}" class="profile-photo">
  <div class="profile-info">
    {{ site.data.professor.Profile | markdownify }}
  </div>
</div>

<hr>

<div class="two-col">
  {% for section in site.data.professor %}
    {% comment %} Profile과 사진 데이터는 위에서 썼으니 제외하고 반복 {% endcomment %}
    {% if section[0] != 'Profile' and section[0] != 'Profile_Image' %}
      <div class="card">
        <h2>{{ section[0] }}</h2>
        {{ section[1] | markdownify }}
      </div>
    {% endif %}
  {% endfor %}
</div>
