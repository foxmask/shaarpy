# ShaarPy

<img src="https://github.com/foxmask/shaarpy/blob/main/docs/shaarpy.png" height="179" width="200"/>

Share Thoughts, Ideas, Links, Notes.

a 'Shaarli cloned' in Python made with Django

![Main page](https://github.com/foxmask/shaarpy/blob/main/docs/shaarpy_home.png)

## Features

* bookmarking
* microblogging

### Notes

- Create *notes* in **Markdown**

### Links

- Drop a URL and ShaarPy will grab the article page with **image** and **video** if the source website provides ones
<a href="https://github.com/foxmask/shaarpy/blob/main/docs/shaarpy_article.png"><img src="https://github.com/foxmask/shaarpy/blob/main/docs/shaarpy_article.png" alt="article with image" width="400"/></a>

### Tags

- Manage tags
- Tag Cloud

<a href="https://github.com/foxmask/shaarpy/blob/main/docs/tags_list.png"><img src="https://github.com/foxmask/shaarpy/blob/main/docs/tags_list.png" alt="tag cloud" width="400"/></a>

### Daily links history

- See the links of the day and navigate throw the calendar to go back to your old links

<a href="https://github.com/foxmask/shaarpy/blob/main/docs/daily.png"><img src="https://github.com/foxmask/shaarpy/blob/main/docs/daily.png" alt="daily links" width="400"/></a>

### Tools

- for each link added, a markdown file can be create in a folder that will be sync on your mobile with the help of "[syncthing](https://syncthing.net/)"
- Import of  **Shaarli** exported bookmark, or even **FireFox** bookmarks
- you can export/import your data in **json**
- Import your Pelican blog markdown files

**export**

```bash
python manage.py dumpdata --format json --indent 2 > fixtures/my_shaarpy_dump.json
```

**import**

```bash
python manage.py loaddata --format json  fixtures/my_shaarpy_dump.json
```

### Bookmarklet

Drag the link you'll find under your profile, to the bookmark of the browser

![Bookmarklet](https://github.com/foxmask/shaarpy/blob/main/docs/bookmarklet.png)

Now you'are able to post a new link just be clicking this bookmarklet wherever you are on the web

## Links sync on mobile

If you don't host ShaarPy on a dedicated server, you can run it locally and sync the links in markdown file and sync them on mobile.

Then files are generated, you may found them on your mobile (thanks to syncthing for managing that task)


### original webpage

![Link of the website](https://github.com/foxmask/shaarpy/blob/main/docs/shaarpy_article_website.png)

### shaarpy grabbed link

![Link in shaarpy](https://github.com/foxmask/shaarpy/blob/main/docs/shaarpy_article.png)

### shaarpy link on mobile

![Shaarpy link on mobile](https://github.com/foxmask/shaarpy/blob/main/docs/article_mobile.png)

(I use "Epsilon Notes" for that)


## Installation

## :package: Installation

### Requirements

* Python from 3.11 3.12 3.13
* Django from 5.1+

### Installation

create a virtualenv

```bash
python3 -m venv shaarpy
cd shaarpy
source bin/activate
```

install the project

```bash
git clone https://github.com/foxmask/shaarpy.git
cd shaarpy
```

##  :wrench: Settings

copy the sample config file

```bash
cp env.sample .env
```

and set the following values, for examples

```ini
# for meta
SHAARPY_NAME=Shaarpy
SHAARPY_DESCRIPTION=Share thoughts, links ideas, notes
SHAARPY_AUTHOR=FoxMaSk
SHAARPY_ROBOT=index, follow
# for MD generation, set a path eg /home/foxmask/MesNotes/links or leave it empty to not use this feature
SHAARPY_LOCALSTORAGE_MD=
SHAARPY_STYLE=blue

SECRET=!DONTFORGETTOCHANGETHISVALUE!

# for production environment, set it to the URL of your 'ShaarPy'
# 1 set it to False
DEBUG=False
# 2 set it to the URL of your 'ShaarPy'
ALLOWED_HOSTS='127.0.0.1,localhost'
# 3 set it to your own domain hosting shaarpy
CSRF_TRUSTED_ORIGINS=https://*.mydomain.com

# for database
DB_ENGINE='django.db.backends.sqlite3'
DB_NAME='db.sqlite3'
DB_USER=''
DB_PASSWORD=''
DB_HOST=''
DB_PORT=''

# i18n/l10n
TIME_ZONE='Europe/Paris'
LANGUAGE_CODE='en-en'
USE_I18N=True
USE_TZ=True
```

## :dvd: Database

setup the database

```bash
cd shaarpy
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata shaarpy/fixtures/my_shaarpy_data.json
```

## :mega: Running the Server

### start the project

```bash
python manage.py runserver localhost:8001
```

then, access the project with your browser http://127.0.0.1:8001/

### Test

```bash
python manage.py test
```

or

```bash
pytest
```
or

```bash
coverage run --source='.' -m pytest
coverage report -m
```


## DOCKER

build the image and run the container

```bash
sudo docker compose up --build -d
```

then, the first installation, do:

```bash
sudo docker compose exec web python manage.py migrate --noinput
sudo docker compose exec web python manage.py createsuperuser
```


## Logo

(logo, thanks to [https://pixabay.com/fr/users/clker-free-vector-images-3736/](https://pixabay.com/fr/vectors/serpent-python-vert-reptile-faune-312561/) )
