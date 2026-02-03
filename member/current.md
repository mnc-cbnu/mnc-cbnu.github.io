---
layout: default
title: Current Members
---

<h1>Current Members</h1>

{% if site.data.members.current.phd %}
  <h2>Ph.D. Students</h2>
  <div class="member-grid">
    {% for member in site.data.members.current.phd %}
      {% include member-card.html member=member %}
    {% endfor %}
  </div>
{% endif %}

{% if site.data.members.current.ms %}
  <h2>M.S. Students</h2>
  <div class="member-grid">
    {% for member in site.data.members.current.ms %}
      {% include member-card.html member=member %}
    {% endfor %}
  </div>
{% endif %}
