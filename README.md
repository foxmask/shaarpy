# ShaarPy 

The very nice Shaarli (https://sebsauvage.net/wiki/doku.php?id=php:shaarli) 'cloned' in Python

Save your notes and links to share ... or not ;) 

![Main page](https://framagit.org/foxmask/shaarpy/-/raw/main/docs/shaarpy_home.png)

## Installation
## :package: Installation

### Requirements 

* Python from 3.8 to 3.10
* Django 4.0
* pandoc

### Installation

pandoc

```bash
sudo apt install pandoc
```

create a virtualenv

```bash
python3 -m venv shaarpy
cd shaarpy
source bin/activate
```

install the project

```bash
git clone https://framagit.org/foxmask/shaarpy
cd shaarpy
```

##  :wrench: Settings

copy the sample config file

```bash
cp env.sample .env
```

and set the following values

```ini
SHAARPY_NAME=Home Sweet Links
SHAARPY_DESCRIPTION=Links, tech links, life links

SECRET=!DONTFORGETTOCHANGETHISVALUE!

DEBUG=True   # or False in prod
DB_ENGINE='django.db.backends.sqlite3'
DB_NAME='db.sqlite3'
DB_USER=''
DB_PASSWORD=''
DB_HOST=''
DB_PORT=''

TIME_ZONE='Europe/Paris'
LANGUAGE_CODE='en-en'
USE_I18N=True
USE_L10N=True
USE_TZ=True

SECRET_KEY=!TOBEDEFINED!
```

## :dvd: Database

setup the database

```bash
cd shaarpy
python manage.py createsuperuser
python manage.py migrate
```

## :mega: Running the Server
### start the project

```bash
python manage.py runserver localhost:8001
```

then, access the project with your browser http://127.0.0.1:8001/

## Usage

### Add a new link

![New links](https://framagit.org/foxmask/shaarpy/-/raw/main/docs/new_link.png)

### Tags list 

![Tags list](https://framagit.org/foxmask/shaarpy/-/raw/main/docs/tags_list.png)

to easily find links by tags

### Daily links

![Daily links](https://framagit.org/foxmask/shaarpy/-/raw/main/docs/daily.png)
