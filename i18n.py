# Internationalization (i18n) Guide for MyPress

## Overview

MyPress supports internationalization using Django's built-in i18n system. The system currently uses **English (en)** as the default language with **Simplified Chinese (zh-Hans)** as a secondary language.

## Features

- ✅ Multi-language template support
- ✅ Language switching via URL prefix (`/en/` or `/zh/`)
- ✅ Browser language detection
- ✅ Persistent language preference via cookies/session

## Configuration

### Languages

Currently supported languages in `settings/base.py`:

```python
LANGUAGES = [
    ('en', 'English'),
    ('zh-hans', 'Simplified Chinese'),
]
```

### Adding a New Language

1. Add the language to `LANGUAGES` in `settings/base.py`
2. Create locale directory: `locale/<lang_code>/LC_MESSAGES/`
3. Create `.po` file: `locale/<lang_code>/LC_MESSAGES/django.po`
4. Run `python manage.py compilemessages`

## Translation Workflow

### 1. Mark Strings for Translation

In Python code:
```python
from django.utils.translation import gettext_lazy as _

# For dynamic strings (models, forms)
verbose_name = _("Article Title")
help_text = _("Enter the article title")

# For static strings in views
messages.success(request, _("Article created successfully"))
```

In templates:
```html
{% load i18n %}

<title>{% trans "My Blog" %}</title>
<h1>{% trans "Welcome" %}</h1>
```

### 2. Extract Translations

```bash
# Extract all translation strings
python manage.py makemessages -l zh_Hans

# Extract for all languages
python manage.py makemessages --all
```

### 3. Edit Translation Files

Edit `locale/<lang>/LC_MESSAGES/django.po`:

```po
#: home/models.py:15
msgid "Article Title"
msgstr "文章标题"
```

### 4. Compile Translations

```bash
python manage.py compilemessages
```

## URL Configuration for i18n

To enable language prefix in URLs, add to `urls.py`:

```python
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

urlpatterns += i18n_patterns(
    path('', home_views.index, name='index'),
    # ... your other URLs
)
```

This enables URLs like:
- `/en/blog/` - English
- `/zh/blog/` - Chinese

## Language Switching in Templates

```html
{% load i18n %}

<form action="{% url 'set_language' %}" method="post">
    {% csrf_token %}
    <input name="next" type="hidden" value="{{ request.path }}">
    <select name="language">
        {% get_current_language as LANGUAGE_CODE %}
        {% get_available_languages as LANGUAGES %}
        {% for code, name in LANGUAGES %}
            <option value="{{ code }}" {% if code == LANGUAGE_CODE %}selected{% endif %}>
                {{ name }}
            </option>
        {% endfor %}
    </select>
    <button type="submit">Switch</button>
</form>
```

## Notes

- Translation files are in `locale/` directory
- Use `gettext_lazy` (not `gettext`) in model definitions to avoid import issues
- Always run `compilemessages` after modifying `.po` files
- In production, restart the server after compiling messages

## Quick Reference

| Command | Description |
|---------|-------------|
| `python manage.py makemessages -l <lang>` | Extract strings for language |
| `python manage.py compilemessages` | Compile `.po` to `.mo` files |
| `python manage.py check --trans` | Check for translation issues |
