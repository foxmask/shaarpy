---
title: {{ data['title'] }}
date: {{ data['date'] }}
{% if data['tags'] %}
tags: {{ data['tags'] }}
{% endif %}
private: {{ data['private'] }}
toc: Contents
Style: {{ data['style'] }} 
...

# {{ data['title'] }}

[{{ data['title'] }}]({{ data['url'] }})

{% if data['image'] %}![{{ data['image'] }}]({{ data['image'] }}){% endif %}
{% if data['video'] %}{{ data['video'] }}{% endif %}

{{ data['text'] }}
