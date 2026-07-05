import os, bcrypt, sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.category import Category
from app.models.item import Item
from app.routers import auth, categories, items, detection, dashboard, reports

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    try:
        Base.metadata.create_all(bind=engine)
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
        print("Startup OK: DB initialized and seeded", flush=True)
    except Exception as e:
        print(f"Startup WARNING (non-fatal): {e}", flush=True)
    yield

app = FastAPI(title="Detect App API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(detection.router, prefix="/api/detection", tags=["Detection"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

@app.get("/health")
def health():
    return {"status": "ok"}
