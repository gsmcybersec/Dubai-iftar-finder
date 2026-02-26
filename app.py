from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB = "mosques.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS mosques (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            arabic_name TEXT,
            area TEXT NOT NULL,
            city TEXT DEFAULT 'Dubai',
            country TEXT DEFAULT 'UAE',
            address TEXT,
            lat REAL,
            lng REAL,
            iftar_time TEXT DEFAULT 'Maghrib',
            capacity INTEGER,
            contact TEXT,
            notes TEXT,
            verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Seed data - Dubai mosques offering Iftar
    mosques = [
        ("Jumeirah Mosque", "مسجد جميرا", "Jumeirah", "Dubai Beach Rd, Jumeirah", 25.2285, 55.2590, "Maghrib", 2000, "+971-4-353-6666", "Famous landmark mosque, open to non-Muslims", 1),
        ("Grand Mosque (Al Fahidi)", "المسجد الكبير", "Al Fahidi", "Al Fahidi St, Bur Dubai", 25.2637, 55.2972, "Maghrib", 1200, "+971-4-353-0480", "Historic area mosque", 1),
        ("Al Safa Mosque", "مسجد الصفا", "Al Safa", "Al Safa Park area", 25.1985, 55.2350, "Maghrib", 800, None, "Iftar meals open to all", 1),
        ("Masjid Al Noor", "مسجد النور", "Deira", "Al Rigga Rd, Deira", 25.2710, 55.3190, "Maghrib", 1000, "+971-4-222-5100", "Central Deira location", 1),
        ("Al Ras Mosque", "مسجد الرأس", "Al Ras", "Al Ras, Deira", 25.2790, 55.3100, "Maghrib", 600, None, "Traditional Iftar meals", 1),
        ("Masjid Al Tawbah", "مسجد التوبة", "Al Barsha", "Al Barsha 1", 25.1123, 55.1990, "Maghrib", 900, None, "Community Iftar every night", 1),
        ("Ibn Battuta Mosque", "مسجد ابن بطوطة", "Jebel Ali", "Near Ibn Battuta Mall", 25.0435, 55.1170, "Maghrib", 700, None, "Free Iftar for workers", 1),
        ("Al Mankhool Mosque", "مسجد المنخول", "Al Mankhool", "Al Mankhool Rd, Bur Dubai", 25.2490, 55.2930, "Maghrib", 500, None, "Open community Iftar", 1),
        ("Masjid Hind", "مسجد هند", "Karama", "Al Karama", 25.2370, 55.3040, "Maghrib", 600, None, "South Asian community mosque", 1),
        ("Al Quds Mosque", "مسجد القدس", "Al Qusais", "Al Qusais Industrial Area", 25.2900, 55.3800, "Maghrib", 800, None, "Large Iftar spread nightly", 1),
        ("Masjid Al Farooq", "مسجد الفاروق", "Satwa", "Al Satwa", 25.2290, 55.2740, "Maghrib", 750, None, "Omar Ibn Al Khattab Mosque", 1),
        ("Dubai Islamic Affairs Mosque", "مسجد الشؤون الإسلامية", "Bur Dubai", "Bur Dubai", 25.2560, 55.2963, "Maghrib", 1500, "+971-4-203-0330", "IACAD managed mosque", 1),
        ("Al Muraqqabat Mosque", "مسجد المراقبات", "Al Muraqqabat", "Al Muraqqabat, Deira", 25.2640, 55.3255, "Maghrib", 650, None, "Nightly community Iftar", 1),
        ("Masjid Al Rahman", "مسجد الرحمن", "Muhaisnah", "Muhaisnah 4", 25.3050, 55.3900, "Maghrib", 700, None, "Workers area mosque", 1),
        ("Al Garhoud Mosque", "مسجد القرهود", "Al Garhoud", "Al Garhoud", 25.2460, 55.3540, "Maghrib", 800, None, "Near Airport area", 1),
    ]
    
    existing = conn.execute("SELECT COUNT(*) FROM mosques").fetchone()[0]
    if existing == 0:
        conn.executemany('''
            INSERT INTO mosques (name, arabic_name, area, address, lat, lng, iftar_time, capacity, contact, notes, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', mosques)
        conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    areas = conn.execute("SELECT DISTINCT area FROM mosques ORDER BY area").fetchall()
    total = conn.execute("SELECT COUNT(*) FROM mosques").fetchone()[0]
    conn.close()
    return render_template('index.html', areas=areas, total=total)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    area = request.args.get('area', '').strip()
    
    conn = get_db()
    sql = "SELECT * FROM mosques WHERE 1=1"
    params = []
    
    if query:
        sql += " AND (name LIKE ? OR area LIKE ? OR address LIKE ? OR notes LIKE ?)"
        params.extend([f'%{query}%'] * 4)
    if area:
        sql += " AND area = ?"
        params.append(area)
    
    sql += " ORDER BY verified DESC, name ASC"
    mosques = conn.execute(sql, params).fetchall()
    areas = conn.execute("SELECT DISTINCT area FROM mosques ORDER BY area").fetchall()
    conn.close()
    
    if request.headers.get('Accept') == 'application/json':
        return jsonify([dict(m) for m in mosques])
    
    return render_template('search.html', mosques=mosques, areas=areas, query=query, area=area)

@app.route('/mosque/<int:id>')
def mosque_detail(id):
    conn = get_db()
    mosque = conn.execute("SELECT * FROM mosques WHERE id=?", (id,)).fetchone()
    conn.close()
    if not mosque:
        return redirect(url_for('index'))
    return render_template('detail.html', mosque=mosque)

@app.route('/add', methods=['GET', 'POST'])
def add_mosque():
    if request.method == 'POST':
        data = request.form
        conn = get_db()
        conn.execute('''
            INSERT INTO mosques (name, arabic_name, area, address, lat, lng, iftar_time, capacity, contact, notes, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (
            data.get('name'), data.get('arabic_name'), data.get('area'),
            data.get('address'), data.get('lat') or None, data.get('lng') or None,
            data.get('iftar_time', 'Maghrib'), data.get('capacity') or None,
            data.get('contact'), data.get('notes')
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('index') + '?added=1')
    return render_template('add.html')

@app.route('/api/mosques')
def api_mosques():
    conn = get_db()
    mosques = conn.execute("SELECT * FROM mosques ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(m) for m in mosques])

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
