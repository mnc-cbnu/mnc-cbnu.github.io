---
layout: default
title: Research
---

# Research

{% for r in site.data.research %}
## {{ r.title }}
{{ r.desc }}

{% endfor %}
