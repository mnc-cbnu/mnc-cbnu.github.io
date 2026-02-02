---
layout: default
title: Alumni
---

<h1>Alumni</h1>

<div class="member-grid">
  {% for m in site.data.members.alumni %}
    {% include member-card.html member=m %}
  {% endfor %}
</div>