---
layout: default
title: People
---

# People

## Faculty
{% for m in site.data.members.faculty %}
<div class="member">
  <img src="{{ m.image | relative_url }}" />
  <div>
    <b>{{ m.name }}</b><br/>
    {{ m.role }}<br/>
    <a href="mailto:{{ m.email }}">{{ m.email }}</a>
  </div>
</div>
{% endfor %}

## Ph.D. Students
{% for m in site.data.members.phd %}
<div class="member">
  <img src="{{ m.image | relative_url }}" />
  <div>
    <b>{{ m.name }}</b><br/>
    {{ m.role }}<br/>
    Research: {{ m.topic }}
  </div>
</div>
{% endfor %}

## M.S. Students
{% for m in site.data.members.ms %}
<div class="member">
  <img src="{{ m.image | relative_url }}" />
  <div>
    <b>{{ m.name }}</b><br/>
    {{ m.role }}<br/>
    Research: {{ m.topic }}
  </div>
</div>
{% endfor %}

## Alumni
{% for m in site.data.members.alumni %}
<p><b>{{ m.name }}</b> — {{ m.role }}</p>
{% endfor %}
