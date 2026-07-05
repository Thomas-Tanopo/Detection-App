import os, bcrypt
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings, STATIC_DIR
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.category import Category
from app.models.item import Item
from app.routers import auth, categories, items, detection, dashboard, reports
from app.jinja_setup import templates

Base.metadata.create_all(bind=engine)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

db = SessionLocal()
if not db.query(User).filter(User.username == 'admin').first():
    pwd = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode('utf-8')
    db.add(User(username='admin', email='admin@test.com', password_hash=pwd, full_name='Administrator'))

    cats = [
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
        ("Kendaraan", ["Mobil", "Motor", "Bus", "Truk", "Sepeda", "Pesawat", "Kapal", "Kereta"]),
        ("Elektronik", ["Laptop", "Handphone", "TV", "Monitor", "Keyboard", "Mouse", "Kamera", "Speaker"]),
        ("Hewan", ["Kucing", "Anjing", "Burung", "Kuda", "Sapi", "Kambing", "Ayam", "Ikan"]),
        ("Manusia", ["Orang", "Pria", "Wanita", "Anak-anak"]),
        ("Perabotan", ["Meja", "Kursi", "Sofa", "Lemari", "Ranjang", "Rak", "Lampu"]),
        ("Makanan & Minuman", ["Botol", "Gelas", "Piring", "Mangkuk", "Apel", "Jeruk", "Pisang", "Roti"]),
        ("Perlengkapan Olahraga", ["Bola", "Raket", "Glove", "Stik Baseball", "Skateboard", "Surfboard"]),
        ("Alat Tulis", ["Buku", "Pensil", "Pulpen", "Gunting", "Penggaris", "Kertas"]),
        ("Aksesoris", ["Tas", "Kacamata", "Jam Tangan", "Payung", "Topi", "Sepatu"]),
        ("Lainnya", ["Tanda Jalan", "Pohon", "Bunga", "Batu"]),
    ]
    cat_map = {}
    for cd in cats:
        c = Category(**cd)
        db.add(c)
        db.flush()
        cat_map[cd["name"]] = c
    for cat_name, i_names in items_data:
        cat = cat_map[cat_name]
        for iname in i_names:
            db.add(Item(name=iname, category_id=cat.id))
    db.commit()
db.close()

app = FastAPI(title="Detect App")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(items.router)
app.include_router(detection.router)
app.include_router(dashboard.router)
app.include_router(reports.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")
