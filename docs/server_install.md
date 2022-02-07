# ShaarPy :: 🐍 share thoughts, ideas, links, notes.

## server configuration

### NGINX

the nginx HTTP config file could look like that

```ini
server {
    server_name shaarpy.yourdomain.com;
    listen 443 ssl;
    # LetsEncrypt certificats added by 'certbot'
    listen [::]:443 ssl;                                                      # managed by Certbot
    ssl_certificate     /etc/letsencrypt/live/shaarpy.yourdomain.com/fullchain.pem;   # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/shaarpy.yourdomain.com/privkey.pem;     # managed by Certbot
    include             /etc/letsencrypt/options-ssl-nginx.conf;              # managed by Certbot
    ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;                    # managed by Certbot

    server_tokens off;

    root /home/foxmask/Projects/shaarpy/shaarpy/shaarpy/static;

    location /static/ {
        gzip  on;
        alias /home/foxmask/Projects/shaarpy/shaarpy/shaarpy/static/;
        #cache
        expires 1y;
    }

    location = /favicon.ico {
        log_not_found off;
        access_log off;
    }

    error_page 502 @maintenance;
    location @maintenance {
        rewrite ^(.*)$ /502.html break;
    }

    location / {
        proxy_set_header X-Real-IP $remote_addr; # get real Client IP
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Host $http_host;
        proxy_pass       http://127.0.0.1:8888;

        proxy_http_version 1.1;

        proxy_connect_timeout       900;
        proxy_send_timeout          900;
        proxy_read_timeout          900;
        send_timeout                900;

    }

    # if you'd like to drop robots :P
    location /robots.txt {
        return 200 "User-Agent: *\nDisallow: /";
    }

    access_log /var/log/nginx/shaarpy.log;
    error_log /var/log/nginx/shaarpy-error.log;

}

```

### Supervisor

[supervisor](http://supervisord.org/running.html) allow us to start our python project when the system is booting

a config file for supervisor could look like this

create a logs folder (/home/foxmask/Projects/shaarpy/logs/) before starting the project with supervisord

```commandline
[program:shaarpy]
user=foxmask

environment=LANG="fr_FR.UTF-8",LC_ALL="fr_FR.UTF-8",LC_LANG="fr_FR.UTF-8",LOGNAME="foxmask",USER="foxmask",HOME="/home/foxmask",VIRTUAL_ENV="/home/foxmask/Projects/shaarpy"
directory=/home/foxmask/Projects/shaarpy/shaarpy/
command=/home/foxmask/Projects/shaarpy/bin/gunicorn shaarpy.wsgi:application --name shaarpy --workers=2 --user=foxmask --group=foxmask --bind=127.0.0.1:8888 -k eventlet --max-requests 500 --pid /home/foxmask/Projects/shaarpy/gunicorn_shaarpy.pid

autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/foxmask/Projects/shaarpy/logs/gunicorn-start.log ; Where to write log messages
stderr_logfile=/home/foxmask/Projects/shaarpy/logs/gunicorn-start-err.log ; Where to write log messages
startretries=2

startsecs=10
stopwaitsecs=600

```

### Gunicorn
install gunicorn or any other WSGI server 

```commandline
pip install gunicorn
```

here I used eventlet but in 0.30.02, any other earlier version failed to start 
