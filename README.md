# 🐍 Django Project: sitewomen

A blog platform built with Django and Django REST.
Users can read posts, put likes or dislikes, and write comments under the post.
For convenience, the posts are divided into categories and subcategories, tags, and there is a search bar.
Users can also create and delete posts.
The website supports translation into 3 languages: English, Russian and Belarusian.
There are group chats where users can chat in real time.
Users have profiles that can be edited, and you can also view profiles of other users.
Users can subscribe to the RSS feed.

## 🚀 Features

- User authentication (login, registration, logout)
- Social authentication
- Email confirmation after registration
- Password change
- Password reset
- Profile editing
- View Profiles
- User presence status
- Multilingual support
- Contact form
- Browse posts by categories, subcategories and tags
- Post search functionality
- Create, edit, delete blog posts
- Comment system
- Like & dislike system
- Real-Time group chats
- Blog API with schema documentation
- Asynchronous & periodic tasks with Celery
- reCAPTCHA protection
- Page caching
- Custom error handlers
- Sitemap support
- RSS feed subscription
- Admin panel for content moderation
- Responsive design with Bootstrap

## 🛠️ Technologies

- Python 3.10+
- Django 4.x
- Django REST framework 3.x
- Django Channels 4.x
- Modeltranslation
- social_django (OAuth2 authentication)
- django-mptt
- django-rosetta
- PostgreSQL 17.x
- Bootstrap 5
- HTML/CSS/JavaScript
- ImageKit
- CKEditor
- Google reCAPTCHA
- Celery + django-celery-beat
- Redis (as Celery broker)
- Memcached
- HTMX
- Docker 

## 📦 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/leshakovalevskiy2002/siteblog.git
cd siteblog
```

2. **Download the `lid.176.bin` language identification model from FastText**:

You can find it on the [FastText language identification page](https://fasttext.cc/docs/en/language-identification.html).

3. **Create a folder named `fasttext_models` inside the `sitewomen` directory
and place the downloaded `lid.176.bin` file there.**

 ```bash
cd sitewomen
mkdir fasttext_models
mv /path/to/lid.176.bin fasttext_models/
```

4. **Create `.env` and `.env.prod` files:**

```bash
cd ..
touch .env .env.prod
```

Example `.env` content (adjust to your environment):

```env
SECRET_KEY =
DEBUG = True
DJANGO_ALLOWED_HOSTS ="127.0.0.1 localhost"
INTERNAL_IPS = '127.0.0.1'
CSRF_TRUSTED_ORIGINS='http://127.0.0.1'
   
GITHUB_KEY =
GITHUB_SECRET =
   
VK_KEY =
VK_SECRET =
   
RECAPTCHA_PUBLIC_KEY =
RECAPTCHA_PRIVATE_KEY =
   
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=
SQL_USER=
SQL_PASSWORD=
SQL_HOST=db
SQL_PORT=5432
   
CACHES_BACKEND = 'django.core.cache.backends.memcached.PyMemcacheCache'
CACHES_LOCATION = 'memcached:11211'
   
CHANNEL_LAYERS_BACKEND = "channels_redis.core.RedisChannelLayer"
CHANNEL_LAYERS_HOSTS = "redis://redis:6379/0"
   
EMAIL_HOST_USER =
EMAIL_HOST_PASSWORD =
   
CELERY_REDIS_HOST = 'redis'
CELERY_REDIS_PORT = '6379'
```

Example `.env.prod` content (adjust to your environment):

```env
SECRET_KEY =
DEBUG = False
DJANGO_ALLOWED_HOSTS =
INTERNAL_IPS =
CSRF_TRUSTED_ORIGINS=
   
GITHUB_KEY =
GITHUB_SECRET =
   
VK_KEY =
VK_SECRET =
   
RECAPTCHA_PUBLIC_KEY =
RECAPTCHA_PRIVATE_KEY =
   
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=
SQL_USER=
SQL_PASSWORD=
SQL_HOST=db
SQL_PORT=5432
DATABASE=postgres
   
CACHES_BACKEND = 'django.core.cache.backends.memcached.PyMemcacheCache'
CACHES_LOCATION = 'memcached:11211'
   
CHANNEL_LAYERS_BACKEND = "channels_redis.core.RedisChannelLayer"
CHANNEL_LAYERS_HOSTS = "redis://redis:6379/0"
   
EMAIL_HOST_USER =
EMAIL_HOST_PASSWORD =
   
CELERY_REDIS_HOST = 'redis'
CELERY_REDIS_PORT = '6379'
```

5. **Run the project using Docker**

For testing or local development:

```bash
docker compose up -d --build
```

For production:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

6. **Apply migrations and collect static files**

For testing or local development:

```bash
docker-compose exec web python manage.py migrate --noinput
docker-compose exec web python manage.py collectstatic --noinput
```

For production:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker compose --env-file .env.prod -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

7. **Compile translation files:**

For testing or local development:

```bash
docker-compose exec web python manage.py compilemessages
```

For production:

```bash
docker-compose --env-file .env.prod -f docker-compose.prod.yml exec web python manage.py compilemessages
```

8. **Enable trigram search extension:**

For testing or local development:

```bash
docker compose exec db psql --username=sitewomen --dbname=sitewomen
```
   
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
\q
```

For production:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec web python manage.py createsuperuser
```
   
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
\q
```

9. **Create a superuser:**

For testing or local development:

```bash
docker compose exec web python manage.py createsuperuser
```

For production:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec db psql --username=sitewomen --dbname=sitewomen
```

Once logged into the Django admin panel, you can:

 - Add categories and tags
 - Create group chats
 - Start using the blog functionality

## 🧪 Testing

To run the test suite and verify that everything is working correctly:

```bash
docker compose exec web python manage.py test
```

## 🗂️ Project Structure

```code
   siteblog/
   ├── nginx/                      # Nginx server configuration
   ├── sitewomen/                  # Main Django project directory
   │   ├── blog_api/               # Blog API logic (views, serializers, routers)
   │   ├── chat/                   # Real-time group chat functionality (Django Channels)
   │   ├── locale/                 # Translation files (.po/.mo) for i18n
   │   ├── services/               # Shared utilities, services, and mixins
   │   ├── sitewomen/              # Django core config: settings, asgi.py, wsgi.py, urls.py
   │   ├── templates/
   │   ├── users/                  # User app: profiles, auth, social login
   │   ├── women/                  # Blog app: posts, categories, tags, comments
   │   ├── Dockerfile              # Dockerfile for development
   │   ├── Dockerfile.prod         # Dockerfile for production
   │   ├── entrypoint.prod.sh      # Entrypoint script for production container
   │   ├── manage.py               
   │   ├── requirements.txt   
   │   └── schema.yml
   ├── docker-compose.yml          # Docker Compose config for development
   ├── docker-compose.prod.yml     # Docker Compose config for production
   ├── .env                        # Environment variables for development
   └── .env.prod                   # Environment variables for production
```

## 📚 API Documentation

The blog API is documented using Swagger.  
Visit `/api/schema/swagger-ui/` for interactive documentation.

## 🧑‍💻 Author

Developed by [Lesha Kovalevskiy](https://github.com/leshakovalevskiy2002)  
Email: lesha_programmer02_gt@mail.ru

## 🧵 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Make sure to update tests as appropriate.
