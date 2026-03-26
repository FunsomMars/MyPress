# MyPress - Lightweight Blog System

[中文](./README.md) | English

A lightweight blog system built with Django + Wagtail CMS, supporting seamless WordPress data import.

## Features

- 📝 Article publishing/editing (WordPress shortcode support)
- 🎵 Audio/video playback
- 💬 Comment system (with moderation)
- 👥 User group permission system (Editor/Moderator/Administrator)
- 📂 Custom page management
- 🔍 Full-text search
- 🖼️ Media file management
- 🐳 Docker one-click deployment
- 📦 PostgreSQL database (high concurrency support)

## Quick Start

### 1. Docker One-Click Deployment (Recommended)

```bash
# Clone the project
git clone https://github.com/FunsomMars/MyPress.git
cd MyPress

# Copy environment config
cp .env.example .env

# Edit .env file
vim .env

# One-click deployment
chmod +x deploy.sh
./deploy.sh
```

### 2. Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

Access:
- Frontend: `http://localhost:8000`
- Admin: `http://localhost:8000/admin/`

## User Permission System

| User Group | Permissions |
|------------|-------------|
| Regular User | Browse, Comment |
| Editor | Create/Edit articles |
| Moderator | Comment management |
| Administrator | Page management, User approval |
| Super Admin | All permissions |

### Permission Application
Users can apply for user groups in their profile, requires admin approval.

## WordPress Data Import

### Import Articles and Pages

```bash
# Import articles
python manage.py import_wordpress wordpress.xml

# Import custom pages
python import_pages_json.py
```

### Supported Shortcodes

- `[audio mp3="..."]` - Audio player
- `[video...]` - Video player

## Configuration

### Environment Variables (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,www.mspace.top

# PostgreSQL
DB_NAME=mypress
DB_USER=mypress
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# Email (optional)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
```

### Backup (Production)

```bash
# Manual backup
/opt/mypress/backup_db.sh

# Auto backup (Every Sunday 3 AM)
# Backups retained for 4 weeks
```

## Common Commands

```bash
# Enter container
docker exec -it mypress_web bash

# View logs
docker logs -f mypress_web

# Restart service
docker restart mypress_web

# Rebuild containers
docker-compose up -d --build
```

## Tech Stack

- **Backend**: Django 5.x + Wagtail CMS 6.x
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Frontend**: Bootstrap 5 + Custom CSS
- **Deployment**: Docker + Docker Compose + Nginx

## Project Structure

```
MyPress/
├── docker-compose.yml    # Docker orchestration
├── Dockerfile           # Docker image
├── requirements.txt     # Python dependencies
├── manage.py           # Django management script
├── deploy.sh          # Deployment script
├── my_press/          # Django project settings
│   ├── settings/      # Settings directory
│   ├── urls.py
│   └── wsgi.py
├── home/              # Blog app
│   ├── models.py      # Data models
│   ├── views.py       # Views
│   ├── templates/     # Templates
│   └── templatetags/  # Template tags
├── search/            # Search app
├── data/              # Import data (JSON)
└── media/            # Media files
```

## License

GNU General Public License v3.0 - For learning and sharing only.
