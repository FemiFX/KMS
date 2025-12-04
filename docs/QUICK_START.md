# Quick Start Guide - UN-Dekade KMS

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL
- Redis

## Initial Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd backend/app/static
npm install
```

### 3. Build CSS

```bash
npm run css:build
```

For development with auto-rebuild:
```bash
npm run css:watch
```

## Running the Application

### Development Mode

```bash
cd backend
flask run
```

Or with auto-reload:
```bash
FLASK_ENV=development flask run
```

### Access the Application

- **Public Site**: http://localhost:5000
- **Admin Login**: http://localhost:5000/login
- **Admin Dashboard**: http://localhost:5000/admin

### Default Credentials

(If you have seeded data, otherwise create a user via CLI)

```bash
flask create-user admin@example.com --password yourpassword
```

## Available Routes

### Public Routes
- `/` - Landing page with search
- `/contents/<id>` - View individual content

### Admin Routes (requires authentication)
- `/login` - Login page
- `/logout` - Logout
- `/admin/` - Dashboard
- `/admin/contents` - Browse all content
- `/admin/contents/new` - Create new article
- `/admin/media` - Media library
- `/admin/media/upload` - Upload media
- `/admin/search` - Search content
- `/admin/tags` - Manage tags
- `/admin/translations` - Manage translations

## Language Support

Default language: **German (de)**

Change language by adding `?lang=<code>` to any URL:
- German: `?lang=de`
- English: `?lang=en`
- French: `?lang=fr`
- Portuguese: `?lang=pt`

## Dark Mode

Dark mode is toggled via the moon/sun icon in the top navigation bar. The preference is saved in localStorage and persists across sessions.

## Development Workflow

### Making UI Changes

1. Edit HTML templates in `backend/app/templates/`
2. Edit CSS in `backend/app/static/src/css/main.css`
3. Rebuild CSS: `npm run css:build` or use `npm run css:watch`
4. Refresh browser

### Adding New Colors

Edit `backend/app/static/tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      // Add your colors here
    }
  }
}
```

Then rebuild CSS.

## Common Tasks

### Create a New User

```bash
flask create-user email@example.com --password yourpassword
```

### Run Database Migrations

```bash
flask db upgrade
```

### Create a New Migration

```bash
flask db migrate -m "Description of changes"
```

### Seed Test Data

```bash
python seed_data.py
```

## Troubleshooting

### CSS Not Loading
- Make sure you've run `npm install` in `backend/app/static`
- Build CSS: `npm run css:build`
- Check that `dist/css/main.css` exists

### Dark Mode Not Working
- Clear browser localStorage
- Check browser console for JavaScript errors
- Ensure `theme.js` is loading correctly

### Language Not Changing
- Verify the `?lang=` parameter in URL
- Check that routes are passing `current_language` to templates

### Templates Not Found
- Verify template names match route handlers
- Check Flask template folder configuration
- Restart Flask development server

## Project Structure

```
kms/
├── backend/
│   ├── app/
│   │   ├── static/
│   │   │   ├── dist/         # Built CSS/JS
│   │   │   └── src/          # Source CSS/JS
│   │   ├── templates/        # Jinja2 templates
│   │   ├── models/           # Database models
│   │   ├── views/            # Route handlers
│   │   └── api/              # API endpoints
│   └── run.py
└── docs/
    ├── UI_IMPLEMENTATION.md  # Detailed UI docs
    └── QUICK_START.md        # This file
```

## Next Steps

1. ✅ UI is complete and ready
2. ⏳ Test all routes with backend
3. ⏳ Implement file upload functionality
4. ⏳ Set up semantic search
5. ⏳ Configure production deployment

## Getting Help

- Check [UI_IMPLEMENTATION.md](UI_IMPLEMENTATION.md) for detailed documentation
- Review backend API documentation
- Check Flask logs for errors

---

**Happy coding!** 🎉
