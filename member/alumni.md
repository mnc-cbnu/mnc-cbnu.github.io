---
layout: default
title: Alumni
---

<h1>Alumni</h1>


{% if site.data.members.alumni.phd %}
  <h2>Ph.D. Students</h2>
  <div class="member-grid">
    {% for member in site.data.members.alumni.phd %}
      {% include member-card.html member=member %}
    {% endfor %}
  </div>
{% endif %}

{% if site.data.members.alumni.ms %}
  <h2>M.S. Students</h2>
  <div class="member-grid">
    {% for member in site.data.members.alumni.ms %}
      {% include member-card.html member=member %}
    {% endfor %}
  </div>
{% endif %}