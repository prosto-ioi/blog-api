#!/bin/bash
set -e  


echo "[1/8] Checking environment variables..."
ENV_FILE="settings/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: $ENV_FILE not found. Copy settings/.env.example to settings/.env and fill in values."
    exit 1
fi

REQUIRED_VARS=("BLOG_SECRET_KEY" "BLOG_ENV_ID" "BLOG_DEBUG" "BLOG_ALLOWED_HOSTS" "BLOG_REDIS_URL")

for VAR in "${REQUIRED_VARS[@]}"; do
    VALUE=$(grep "^${VAR}=" "$ENV_FILE" | cut -d '=' -f2-)
    if [ -z "$VALUE" ]; then
        echo "ERROR: Required variable '$VAR' is missing or empty in $ENV_FILE"
        exit 1
    fi
done
echo "  All required variables are set."

echo "[2/8] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements/dev.txt
echo "  Dependencies installed."

mkdir -p logs

echo "[3/8] Running migrations..."
python manage.py migrate --run-syncdb
echo "  Migrations done."

echo "[4/8] Collecting static files..."
python manage.py collectstatic --noinput -v 0
echo "  Static files collected."

echo "[5/8] Compiling translations..."
python manage.py compilemessages -v 0 2>/dev/null || echo "  (skipped — no .po files yet)"

echo "[6/8] Creating superuser..."
python manage.py shell -c "
from apps.users.models import User
if not User.objects.filter(email='admin@blog.com').exists():
    User.objects.create_superuser(
        email='admin@blog.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('  Superuser created.')
else:
    print('  Superuser already exists, skipping.')
"
echo "[7/8] Seeding test data..."
python manage.py shell -c "
from apps.users.models import User
from apps.blog.models import Category, Tag, Post, Comment

# Пользователи
users = []
for i in range(1, 4):
    email = f'user{i}@blog.com'
    if not User.objects.filter(email=email).exists():
        u = User.objects.create_user(email=email, password='pass1234', first_name=f'User', last_name=str(i))
        users.append(u)
    else:
        users.append(User.objects.get(email=email))

# Категории
cats = []
for name, slug, name_ru, name_kk in [
    ('Technology', 'technology', 'Технологии', 'Технология'),
    ('Science', 'science', 'Наука', 'Ғылым'),
    ('Travel', 'travel', 'Путешествия', 'Саяхат'),
]:
    c, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'name_ru': name_ru, 'name_kk': name_kk})
    cats.append(c)

# Теги
tags = []
for name, slug in [('python', 'python'), ('django', 'django'), ('api', 'api'), ('redis', 'redis')]:
    t, _ = Tag.objects.get_or_create(slug=slug, defaults={'name': name})
    tags.append(t)

# Посты
admin = User.objects.get(email='admin@blog.com')
for i in range(1, 6):
    slug = f'test-post-{i}'
    if not Post.objects.filter(slug=slug).exists():
        p = Post.objects.create(
            author=admin,
            title=f'Test Post {i}',
            slug=slug,
            body=f'Body of test post {i}. ' * 10,
            category=cats[i % len(cats)],
            status='published' if i % 2 == 0 else 'draft',
        )
        p.tags.set(tags[:2])
        Comment.objects.create(post=p, author=users[0], body=f'Comment on post {i}')
        Comment.objects.create(post=p, author=users[1], body=f'Another comment on post {i}')

print('  Test data seeded.')
"

echo "[8/8] Starting development server..."
echo ""
echo "========================================"
echo "  READY! Here is your summary:"
echo "----------------------------------------"
echo "  API:        http://127.0.0.1:8000/api/"
echo "  Swagger:    http://127.0.0.1:8000/api/docs/"
echo "  ReDoc:      http://127.0.0.1:8000/api/redoc/"
echo "  Admin:      http://127.0.0.1:8000/admin/"
echo "----------------------------------------"
echo "  Superuser:  admin@blog.com / admin123"
echo "========================================"
echo ""
python manage.py runserver