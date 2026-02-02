---
layout: default
title: Publications
---

# Publications

{% assign pubs = site.data.publications | sort: "year" | reverse %}
{% for p in pubs %}
<div class="pub">
  <b>{{ p.title }}</b><br/>
  {{ p.authors }}<br/>
  <i>{{ p.venue }}</i>, {{ p.year }}.
  {% if p.link %}<a href="{{ p.link }}">[PDF]</a>{% endif %}
</div>
{% endfor %}
