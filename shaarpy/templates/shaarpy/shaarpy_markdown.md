Title: {{ data['title'] }}
Date: {{ data['date'] }}
Author: {{ data['author'] }} 
{% if data['tags'] %}
tags: {{ data['tags'] }}
{% endif %}
Status: published


{% if data['image'] %}![{{ data['image'] }}]({{ data['image'] }}){% endif %}
{% if data['video'] %}{{ data['video'] }}{% endif %}

# {{ data['title'] }}

[{{ data['title'] }}]({{ data['url'] }})

{{ data['text'] }}
