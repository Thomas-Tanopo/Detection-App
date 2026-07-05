import os, sys, bcrypt, json
sys.path.insert(0, os.path.dirname(__file__))
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/detect_app'

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.category import Category
from app.models.item import Item

Base.metadata.create_all(bind=engine)
db = SessionLocal()

admin = db.query(User).filter(User.username == 'admin').first()
if not admin:
    pwd = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode('utf-8')
    db.add(User(username='admin', email='admin@test.com', password_hash=pwd, full_name='Administrator'))

categories_data = [
    {"name": "Kendaraan", "description": "Mobil, motor, bus, truk dan kendaraan lainnya"},
    {"name": "Elektronik", "description": "Laptop, HP, TV, dan perangkat elektronik"},
    {"name": "Hewan", "description": "Kucing, anjing, burung, kuda dan hewan lainnya"},
    {"name": "Manusia", "description": "Orang, manusia secara umum"},
    {"name": "Perabotan", "description": "Meja, kursi, sofa, lemari dan furnitur"},
    {"name": "Makanan & Minuman", "description": "Botol, gelas, piring, buah dan makanan"},
    {"name": "Perlengkapan Olahraga", "description": "Bola, raket, stick, glove olahraga"},
    {"name": "Alat Tulis", "description": "Buku, pensil, gunting, dan alat tulis kantor"},
    {"name": "Aksesoris", "description": "Tas, kacamata, jam tangan, payung"},
    {"name": "Lainnya", "description": "Objek umum lainnya"},
]

items_data = [
    # Kendaraan
    ("Kendaraan", ["Mobil", "Motor", "Bus", "Truk", "Sepeda", "Pesawat", "Kapal", "Kereta"]),
    # Elektronik
    ("Elektronik", ["Laptop", "Handphone", "TV", "Monitor", "Keyboard", "Mouse", "Kamera", "Speaker"]),
    # Hewan
    ("Hewan", ["Kucing", "Anjing", "Burung", "Kuda", "Sapi", "Kambing", "Ayam", "Ikan"]),
    # Manusia
    ("Manusia", ["Orang", "Pria", "Wanita", "Anak-anak"]),
    # Perabotan
    ("Perabotan", ["Meja", "Kursi", "Sofa", "Lemari", "Ranjang", "Rak", "Lampu"]),
    # Makanan & Minuman
    ("Makanan & Minuman", ["Botol", "Gelas", "Piring", "Mangkuk", "Apel", "Jeruk", "Pisang", "Roti"]),
    # Perlengkapan Olahraga
    ("Perlengkapan Olahraga", ["Bola", "Raket", "Glove", "Stik Baseball", "Skateboard", "Surfboard"]),
    # Alat Tulis
    ("Alat Tulis", ["Buku", "Pensil", "Pulpen", "Gunting", "Penggaris", "Kertas"]),
    # Aksesoris
    ("Aksesoris", ["Tas", "Kacamata", "Jam Tangan", "Payung", "Topi", "Sepatu"]),
    # Lainnya
    ("Lainnya", ["Tanda Jalan", "Ramadhu", "Pohon", "Bunga", "Batu"]),
]

cat_map = {}
for cd in categories_data:
    existing = db.query(Category).filter(Category.name == cd["name"]).first()
    if existing:
        cat_map[cd["name"]] = existing
    else:
        c = Category(**cd)
        db.add(c)
        db.flush()
        cat_map[cd["name"]] = c

for cat_name, i_names in items_data:
    cat = cat_map.get(cat_name)
    for iname in i_names:
        exists = db.query(Item).filter(Item.name == iname, Item.category_id == cat.id).first()
        if not exists:
            db.add(Item(name=iname, category_id=cat.id))

db.commit()
db.close()

print("Seed data berhasil dimasukkan!")
print(f"  - {db.query(Category).count()} kategori")
print(f"  - {db.query(Item).count()} barang")
print(f"  - User admin: admin / admin123")
