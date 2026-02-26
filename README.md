# 🕌 Dubai Iftar Finder

A mosque Iftar meal finder for Dubai/UAE, built with Python Flask + SQLite.

## Quick Setup (3 steps)

```bash
# 1. Install Flask
pip install flask

# 2. Run the app
python app.py

# 3. Open in browser
http://localhost:5000
```

## Features
- 🔍 Search mosques by name or area
- 🕌 15+ Dubai mosques pre-loaded
- ➕ Add new mosques via form
- 📍 Google Maps integration
- 📱 Mobile-friendly design
- 🌙 Beautiful Islamic-themed UI

## Project Structure
```
dubai-iftar/
├── app.py              ← Main Flask app (all routes + DB logic)
├── requirements.txt    ← Just Flask
├── mosques.db          ← Auto-created SQLite database
└── templates/
    ├── index.html      ← Homepage with search
    ├── search.html     ← Search results
    ├── detail.html     ← Mosque detail page
    └── add.html        ← Add mosque form
```

## How to Add More Mosques

### Option 1: Via the web form
Go to http://localhost:5000/add

### Option 2: Edit the seed data in app.py
Find the `mosques = [...]` list in the `init_db()` function and add rows:
```python
("Mosque Name", "Arabic Name", "Area", "Address", lat, lng, "Maghrib", capacity, "contact", "notes", 1),
```

### Option 3: Direct SQLite
```bash
sqlite3 mosques.db
INSERT INTO mosques (name, area, address) VALUES ('New Mosque', 'Downtown', 'Sheikh Zayed Rd');
```

## API Endpoint
All mosques as JSON: `GET /api/mosques`

## Deploy to Internet (Free)
1. Push to GitHub
2. Go to railway.app → Deploy from GitHub
3. Done! Live in 5 minutes.

## Next Steps to Improve
- [ ] Add Google Maps embed on detail page
- [ ] Add photo upload for mosques  
- [ ] Add admin panel to verify submissions
- [ ] Add Abu Dhabi, Sharjah mosques
- [ ] Add prayer time API integration
- [ ] WhatsApp share button

Ramadan Kareem 🌙
