---
layout: default
title: Members
---

<h1>Members</h1>

{% assign current = site.data.members.current %}
{% assign alumni = site.data.members.alumni %}

<h2>Current Members</h2>

{% if current.phd %}
<h3>Ph.D. Students</h3>
<div class="member-grid">
  {% for m in current.phd %}
    {% include member-card.html member=m %}
  {% endfor %}
</div>
{% endif %}

{% if current.ms %}
<h3>M.S. Students</h3>
<div class="member-grid">
  {% for m in current.ms %}
    {% include member-card.html member=m %}
  {% endfor %}
</div>
{% endif %}

<hr>

<h2>Alumni</h2>

{% if alumni %}
<div class="member-grid">
  {% for m in alumni %}
    {% include member-card.html member=m %}
  {% endfor %}
</div>
{% endif %}
