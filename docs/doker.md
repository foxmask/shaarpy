# ShaarPy :: 🐍 share thoughts, ideas, links, notes.

## docker install

### Build the image or grab it


### build

The first time you use the docker image of shaarpy, launch this command to build the image.

This won't be necessary for the next time

```bash
docker-compose build
```

### Grab it by

```bash
docker pull foxmask/shaarpy
```

### Run

This is necessary each time you want to use shaarpy

```bash
docker-compose up
```



### Database update/create

This is necessary the first time, after building the docker image done above.

```bash
docker-compose run web  python manage.py migrate
docker-compose run web  python manage.py createsuperuser
docker-compose run web  python manage.py loaddata my_shaarpy_data
```

This is necessary only when a new release of shaarpy is done

```bash
docker-compose run web  python manage.py migrate
```

### Running tasks


2 tasks are usually in the crontab: one to read the data source, one to publish the grabbed data:

```bash
docker-compose run web  python manage.py export_md
docker-compose run web  python manage.py import
```
