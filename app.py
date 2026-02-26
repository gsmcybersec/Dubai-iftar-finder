from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB = "/tmp/mosques.db"

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
            food_type TEXT,
            verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    mosques = [
        # DUBAI
        ("Jumeirah Mosque","مسجد جميرا","Jumeirah","Dubai","Dubai Beach Road, Jumeirah",25.2285,55.2590,"Maghrib",2000,"+971-4-353-6666","Iconic landmark mosque. Open to Muslims and non-Muslims. Large community Iftar every night during Ramadan.","Rice, Biryani, Mixed",1),
        ("Grand Mosque Al Fahidi","المسجد الكبير","Al Fahidi","Dubai","Al Fahidi Street, Bur Dubai",25.2637,55.2972,"Maghrib",1200,"+971-4-353-0480","Historic Bur Dubai mosque near the heritage area. Traditional Iftar meals served nightly.","Rice, Mixed",1),
        ("Al Safa Mosque","مسجد الصفا","Al Safa","Dubai","Al Safa Park area, Al Safa",25.1985,55.2350,"Maghrib",800,None,"Community mosque near Al Safa Park. Iftar meals open to all.","Mixed",1),
        ("Masjid Al Noor Deira","مسجد النور","Deira","Dubai","Al Rigga Road, Deira",25.2710,55.3190,"Maghrib",1000,"+971-4-222-5100","Central Deira location. Well-organised Iftar program every Ramadan night.","Rice, Mixed",1),
        ("Masjid Al Tawbah","مسجد التوبة","Al Barsha","Dubai","Al Barsha 1, Dubai",25.1123,55.1990,"Maghrib",900,None,"Community Iftar every night. Popular with Al Barsha residents.","Mixed",1),
        ("Ibn Battuta Mosque","مسجد ابن بطوطة","Jebel Ali","Dubai","Near Ibn Battuta Mall, Jebel Ali",25.0435,55.1170,"Maghrib",700,None,"Free Iftar for workers and community. Near Ibn Battuta Mall.","Rice, Mixed",1),
        ("Al Mankhool Mosque","مسجد المنخول","Al Mankhool","Dubai","Al Mankhool Road, Bur Dubai",25.2490,55.2930,"Maghrib",500,None,"Open community Iftar in Bur Dubai area.","Mixed",1),
        ("Masjid Hind","مسجد هند","Karama","Dubai","Al Karama, Dubai",25.2370,55.3040,"Maghrib",600,None,"South Asian community mosque. Traditional Iftar meals daily.","Rice, Biryani",1),
        ("Al Quds Mosque","مسجد القدس","Al Qusais","Dubai","Al Qusais Industrial Area, Dubai",25.2900,55.3800,"Maghrib",800,None,"Large Iftar spread nightly. Workers and residents welcome.","Rice, Mixed",1),
        ("Masjid Al Farooq Omar Ibn Al Khattab","مسجد الفاروق عمر بن الخطاب","Al Satwa","Dubai","Al Satwa, Dubai",25.2290,55.2740,"Maghrib",750,None,"Famous Omar Ibn Al Khattab Mosque in Satwa. Large beautiful mosque with community Iftar.","Mixed",1),
        ("Dubai Islamic Affairs Mosque","مسجد الشؤون الإسلامية","Bur Dubai","Dubai","Bur Dubai",25.2560,55.2963,"Maghrib",1500,"+971-4-203-0330","IACAD managed mosque. Well-organised Ramadan Iftar program.","Mixed",1),
        ("Al Muraqqabat Mosque","مسجد المراقبات","Al Muraqqabat","Dubai","Al Muraqqabat, Deira",25.2640,55.3255,"Maghrib",650,None,"Nightly community Iftar in Deira area.","Mixed",1),
        ("Masjid Al Rahman Muhaisnah","مسجد الرحمن","Muhaisnah","Dubai","Muhaisnah 4, Dubai",25.3050,55.3900,"Maghrib",700,None,"Workers area mosque. Free Iftar for residents and laborers.","Rice, Mixed",1),
        ("Al Garhoud Mosque","مسجد القرهود","Al Garhoud","Dubai","Al Garhoud, near Dubai Airport",25.2460,55.3540,"Maghrib",800,None,"Near Dubai Airport area. Community Iftar nightly.","Mixed",1),
        ("Masjid Al Ittihad","مسجد الاتحاد","Deira","Dubai","Al Ittihad Road, Deira",25.2785,55.3240,"Maghrib",900,None,"Large Deira community mosque. Open Iftar every night.","Mixed",1),
        ("Masjid Al Ghazali","مسجد الغزالي","Dubai","Dubai","Dubai, UAE",25.2048,55.2708,"Maghrib",None,None,"Community reported Iftar location. Verified by local residents.","Mixed",1),
        ("KMCC Iftar Center","مركز إفطار كيرلا","Karama","Dubai","Al Karama, Dubai",25.2354,55.3010,"Maghrib",None,None,"Kerala Muslim Cultural Centre Iftar program. Popular with South Asian expat community.","Rice, Biryani, Mixed",1),
        ("Islamic Information Centre Satwa","مركز المعلومات الإسلامية","Al Satwa","Dubai","AL Gurair Branch, Near Nesto Supermarket, Al Satwa",25.2285,55.2820,"After Asr",None,None,"Food distribution starts after Asr prayer. Come early to get a spot.","Mixed, Snacks",1),
        ("Al Salam Masjid Deira","مسجد السلام","Deira","Dubai","Opposite Emirates NBD Bank, Deira",25.2680,55.3150,"Maghrib",None,None,"Open community Iftar opposite Emirates NBD.","Mixed",1),
        ("Markaz Iftar Dubai","مركز إفطار المركز","Bur Dubai","Dubai","Markazu Sakafathi Sunniyya, Dubai",25.2530,55.2990,"Maghrib",None,None,"Markaz cultural centre Iftar program. Well-organised with good food variety.","Rice, Mixed",1),
        ("Alhuwaidi Mosque Karama","مسجد حمد الهويدي","Karama","Dubai","Near Karama Bus Station, Al Karama",25.2380,55.3020,"Maghrib",None,None,"Famous for Nadan (traditional Kerala-style) Biryani. Very popular — arrive before Maghrib!","Biryani",1),
        ("Abdullah Al Zahri Masjid","مسجد عبدالله الزهري","Karama","Dubai","Near Karama Post Office, Al Karama",25.2360,55.3040,"Maghrib",None,None,"Open Iftar in the heart of Karama. Good for South Asian expats.","Mixed",1),
        ("Abuhail Mosque","مسجد أبوهيل","Abuhail","Dubai","Near Abuhail Park, Dubai",25.2750,55.3310,"Maghrib",None,None,"Iftar kit with Biryani or Mandi. Well-organised distribution. Very popular during Ramadan.","Biryani, Mandi",1),
        # ABU DHABI
        ("Sheikh Zayed Grand Mosque","مسجد الشيخ زايد الكبير","Sheikh Zayed","Abu Dhabi","Sheikh Rashid Bin Saeed Street, Abu Dhabi",24.4128,54.4750,"Maghrib",40000,"+971-2-419-1919","LARGEST mosque in UAE! Iftar for thousands every night. Open to everyone.","Rice, Biryani, Mandi, Mixed",1),
        ("Al Musalla Mosque Abu Dhabi","مسجد المصلى","Downtown","Abu Dhabi","Corniche Road, Abu Dhabi",24.4860,54.3705,"Maghrib",2000,None,"Central Abu Dhabi mosque on the Corniche. Community Iftar open to all.","Rice, Mixed",1),
        ("Al Bateen Mosque","مسجد البطين","Al Bateen","Abu Dhabi","Al Bateen District, Abu Dhabi",24.4595,54.3525,"Maghrib",1200,None,"Traditional Iftar meals in upscale Al Bateen area.","Mixed",1),
        ("Al Rahma Mosque","مسجد الرحمة","Khalidiyah","Abu Dhabi","Khalidiyah District, Abu Dhabi",24.4750,54.3590,"Maghrib",1000,None,"Community Iftar nightly in Khalidiyah. Open to all.","Rice, Mixed",1),
        ("Masjid Al Zahraa","مسجد الزهراء","Al Zahraa","Abu Dhabi","Al Zahraa District, Abu Dhabi",24.4200,54.4900,"Maghrib",800,None,"Iftar for workers and residents in Al Zahraa area.","Rice, Mixed",1),
        ("Al Maqtaa Mosque","مسجد المقطع","Al Maqtaa","Abu Dhabi","Al Maqtaa, near historic fort, Abu Dhabi",24.3985,54.4980,"Maghrib",900,None,"Beautiful mosque near the heritage fort area. Community Iftar nightly.","Mixed",1),
        # AL AIN
        ("Al Ain Grand Mosque","مسجد العين الكبير","Al Ain City","Al Ain","Khalifa Street, Al Ain",24.2271,55.7416,"Maghrib",7000,"+971-3-763-2366","Main city mosque in Al Ain. Large organised Iftar event every night. Open to all.","Rice, Biryani, Mandi, Mixed",1),
        ("Al Jimi Mosque","مسجد الجيمي","Al Jimi","Al Ain","Al Jimi District, Al Ain",24.2350,55.7250,"Maghrib",800,None,"Community Iftar for residents of Al Jimi area.","Mixed",1),
        ("Masjid Al Maqam","مسجد المقام","Al Maqam","Al Ain","Al Maqam District, Al Ain",24.2500,55.8100,"Maghrib",600,None,"Traditional Iftar meals in Al Maqam area.","Rice, Mixed",1),
        ("Al Muwaiji Mosque","مسجد المويجعي","Al Muwaiji","Al Ain","Al Muwaiji District, Al Ain",24.2180,55.7700,"Maghrib",500,None,"Open Iftar to all during Ramadan in Al Muwaiji area.","Mixed",1),
        # SHARJAH
        ("King Faisal Mosque Sharjah","مسجد الملك فيصل","Al Nud","Sharjah","King Faisal Road, Sharjah",25.3463,55.4209,"Maghrib",3000,"+971-6-568-0000","One of Sharjah's largest mosques. Big organised Iftar every night.","Rice, Biryani, Mixed",1),
        ("Al Qasimiah Mosque","مسجد القاسمية","Al Qasimiah","Sharjah","Al Qasimiah District, Sharjah",25.3650,55.3900,"Maghrib",1500,None,"Central Sharjah community Iftar. Open to all.","Mixed",1),
        ("Al Noor Mosque Al Majaz","مسجد النور المجاز","Al Majaz","Sharjah","Buhaira Corniche, Al Majaz, Sharjah",25.3320,55.3840,"Maghrib",1200,None,"Beautiful waterfront mosque on Buhaira Corniche. Community Iftar open to all.","Mixed",1),
        ("Grand Mosque Sharjah","المسجد الكبير","Al Riqaibah","Sharjah","Siyouh Suburb, Al Riqaibah, Sharjah",25.3560,55.4250,"Maghrib",2000,None,"Major Sharjah landmark mosque. Community Iftar program during Ramadan.","Rice, Mixed",1),
        ("Bani Shaibah Mosque","مسجد بني شيبة","Sharjah City","Sharjah","Sharjah City, Sharjah",25.3350,55.4150,"Maghrib",800,None,"Community Iftar open to all residents.","Mixed",1),
        ("Muweilah Masjid","مسجد مويلح","Muweilah","Sharjah","Muweilah District, Sharjah",25.3290,55.5120,"Maghrib",600,None,"Limited Mandi meal Iftar. Arrive early as food runs out fast!","Mandi",1),
        ("Sameer Al Mahmood Mosque","مسجد سمير المحمود","Sharjah City","Sharjah","Sharjah, UAE",25.3400,55.4200,"Maghrib",700,None,"Verified community mosque. Iftar open to all.","Mixed",1),
        ("Saudi Mosque Al Soor Sharjah","مسجد الملك فيصل السور","Al Soor","Sharjah","Near OMA Emirates, Al Soor, Sharjah",25.3600,55.3900,"After Asr",2000,None,"Food after Asr prayer. Chicken Biryani kit with dates, water, juice. Finishes by 5:30pm — come early!","Biryani, Dates, Juice",1),
        # AJMAN
        ("Ajman Grand Mosque","مسجد عجمان الكبير","Ajman City","Ajman","Sheikh Humaid Street, Ajman",25.4110,55.4354,"Maghrib",2500,"+971-6-742-2222","Main mosque in Ajman. Large Iftar gathering every Ramadan night.","Rice, Biryani, Mixed",1),
        ("Al Rashidiya Mosque Ajman","مسجد الراشدية","Al Rashidiya","Ajman","Al Rashidiya District, Ajman",25.3900,55.4700,"Maghrib",700,None,"Workers area mosque. Free Iftar for laborers and residents.","Rice, Mixed",1),
        # RAS AL KHAIMAH
        ("RAK Grand Mosque","مسجد رأس الخيمة الكبير","RAK City","Ras Al Khaimah","Al Hamra District, Ras Al Khaimah",25.6741,55.9804,"Maghrib",4000,"+971-7-222-7777","Largest mosque in RAK. Massive organised Ramadan Iftar. Open to all.","Rice, Biryani, Mandi, Mixed",1),
        ("Al Qawasim Mosque RAK","مسجد القواسم","Al Nakheel","Ras Al Khaimah","Al Nakheel District, RAK",25.7800,55.9450,"Maghrib",900,None,"Community Iftar open to all in Al Nakheel area.","Mixed",1),
        # FUJAIRAH
        ("Fujairah Grand Mosque","مسجد الفجيرة الكبير","Fujairah City","Fujairah","Hamad Bin Abdullah Road, Fujairah",25.1219,56.3264,"Maghrib",3000,"+971-9-222-2222","Main mosque in Fujairah city. Iftar open to everyone during Ramadan.","Rice, Mandi, Mixed",1),
        # UMM AL QUWAIN
        ("UAQ Grand Mosque","مسجد أم القيوين الكبير","UAQ City","Umm Al Quwain","King Faisal Road, Umm Al Quwain",25.5647,55.5552,"Maghrib",1500,None,"Iftar meals for the community. Open to all residents.","Rice, Mixed",1),
    ]

    existing = conn.execute("SELECT COUNT(*) FROM mosques").fetchone()[0]
    if existing == 0:
        conn.executemany('''
            INSERT INTO mosques
                (name, arabic_name, area, city, address, lat, lng,
                 iftar_time, capacity, contact, notes, food_type, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', mosques)
        conn.commit()
    conn.close()


@app.route('/')
def index():
    try:
        conn = get_db()
        cities = conn.execute(
            "SELECT city, COUNT(*) as cnt FROM mosques GROUP BY city ORDER BY city"
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM mosques").fetchone()[0]
        food_types = _get_food_types(conn)
        conn.close()
        return render_template('index.html', cities=cities, total=total, food_types=food_types)
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1><p>Please try again</p>", 500


@app.route('/search')
def search():
    query      = request.args.get('q', '').strip()
    city       = request.args.get('city', '').strip()
    food       = request.args.get('food', '').strip()
    iftar_time = request.args.get('iftar_time', '').strip()

    conn = get_db()
    sql    = "SELECT * FROM mosques WHERE 1=1"
    params = []

    if query:
        sql += " AND (name LIKE ? OR area LIKE ? OR address LIKE ? OR notes LIKE ? OR city LIKE ?)"
        params.extend([f'%{query}%'] * 5)
    if city:
        sql += " AND city = ?"
        params.append(city)
    if food:
        sql += " AND food_type LIKE ?"
        params.append(f'%{food}%')
    if iftar_time:
        sql += " AND iftar_time = ?"
        params.append(iftar_time)

    sql += " ORDER BY verified DESC, city ASC, name ASC"
    mosques    = conn.execute(sql, params).fetchall()
    cities     = conn.execute("SELECT DISTINCT city FROM mosques ORDER BY city").fetchall()
    food_types = _get_food_types(conn)
    conn.close()

    return render_template('search.html',
        mosques=mosques, cities=cities, food_types=food_types,
        query=query, city=city, food=food, iftar_time=iftar_time)


@app.route('/mosque/<int:id>')
def mosque_detail(id):
    conn   = get_db()
    mosque = conn.execute("SELECT * FROM mosques WHERE id=?", (id,)).fetchone()
    conn.close()
    if not mosque:
        return redirect(url_for('index'))
    return render_template('detail.html', mosque=mosque)


@app.route('/add', methods=['GET', 'POST'])
def add_mosque():
    all_cities = ["Dubai","Abu Dhabi","Sharjah","Ajman",
                  "Ras Al Khaimah","Fujairah","Umm Al Quwain","Al Ain"]
    if request.method == 'POST':
        data = request.form
        conn = get_db()
        conn.execute('''
            INSERT INTO mosques
                (name, arabic_name, area, city, address, lat, lng,
                 iftar_time, capacity, contact, notes, food_type, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (
            data.get('name'), data.get('arabic_name'),
            data.get('area'), data.get('city', 'Dubai'),
            data.get('address'),
            data.get('lat') or None, data.get('lng') or None,
            data.get('iftar_time', 'Maghrib'),
            data.get('capacity') or None,
            data.get('contact'),
            data.get('notes'),
            data.get('food_type'),
        ))
        conn.commit()
        conn.close()
        return redirect('/?added=1')
    return render_template('add.html', cities=all_cities)


@app.route('/api/mosques')
def api_mosques():
    conn    = get_db()
    mosques = conn.execute("SELECT * FROM mosques ORDER BY city, name").fetchall()
    conn.close()
    return jsonify([dict(m) for m in mosques])


def _get_food_types(conn):
    rows  = conn.execute("SELECT DISTINCT food_type FROM mosques WHERE food_type IS NOT NULL").fetchall()
    types = set()
    for row in rows:
        for t in row[0].split(','):
            types.add(t.strip())
    return sorted(types)


# Initialize database — runs on startup with both Flask dev server and Gunicorn
init_db()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
