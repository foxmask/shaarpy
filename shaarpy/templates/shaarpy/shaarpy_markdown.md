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

[{{ data['url'] }}]({{ data['url'] }})

{{ data['text'] }}
