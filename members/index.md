---
layout: default
title: Member
permalink: /members/
---


<h1>Members</h1>

{% assign current = site.data.members.Current %}
{% assign alumni = site.data.members.Alumni %}

<h2>Current</h2>

{% if current %}
<div class="member-grid">
  {% for member in current %}

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
