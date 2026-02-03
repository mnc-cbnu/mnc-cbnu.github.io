---
layout: default
title: Current Members
---
<h1>Current Members</h1>
<div class="member-grid">
  {% for m in site.data.members.current %}
    {% include member-card.html member=m %}
  {% endfor %}
</div>
