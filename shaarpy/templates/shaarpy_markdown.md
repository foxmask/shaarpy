title: ({{ title }})[{{ url }}]
url: {{ url }}
date: {{ date_create }}
private: {{ private }}
tags: {{ tags }}
status: published

{% if image %}<img src="{{ image }}"/>{% endif %}


{% if video %}{{ video }}{% endif %}


{{ text }}

by {{ author }}
