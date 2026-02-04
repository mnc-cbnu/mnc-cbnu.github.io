---
layout: default
title: Members
---


<h1>Members</h1>

{% assign current = site.data.members.current %}
{% assign alumni = site.data.members.alumni %}

<h2>Current</h2>

{% if current %}
<div class="member-grid">
  {% for member in site.data.members.current %}

    {% include member-card.html member=member %}
  {% endfor %}
</div>
{% endif %}

<hr>

<h2>Alumni</h2>

{% if alumni and alumni.size > 0 %}
<div class="member-grid">
  {% for member in alumni %}
    {% include member-card.html member=member %}
  {% endfor %}
</div>
{% endif %}
