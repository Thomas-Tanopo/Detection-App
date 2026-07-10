#!/bin/bash
set -euo pipefail

# ============================================================
# Deploy Script untuk Detect App — Maximum Security
# Manual Deployment ke VPS Ubuntu/Debian
# Jalankan: sudo bash deploy.sh
# ============================================================

# ---------- Config ----------
APP_DIR="/var/www/detect-app"
DOMAIN="${1:-localhost}"
DB_NAME="detect_app"
DB_USER="detect_user"
DB_PASS="$(openssl rand -hex 16)"
SECRET_KEY="$(openssl rand -hex 32)"

echo "========================================"
echo "  Detect App - Secure Deployment"
echo "========================================"
echo ""

# ---------- 1. System Dependencies ----------
echo "[1/9] Install system dependencies..."
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip \
    nginx postgresql postgresql-contrib \
    libgl1 libglib2.0-0 git openssl curl \
    ufw fail2ban unattended-upgrades

# ---------- 2. Security: Firewall ----------
echo "[2/9] Setup UFW firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable

# ---------- 3. Security: Fail2ban ----------
echo "[3/9] Setup fail2ban..."
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true
logpath = /var/log/nginx/error.log
maxretry = 10
EOF
systemctl restart fail2ban

# ---------- 4. Security: Auto Updates ----------
echo "[4/9] Setup unattended-upgrades..."
cat > /etc/apt/apt.conf.d/20auto-upgrades <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF
systemctl restart unattended-upgrades

# ---------- 5. Clone / Copy Project ----------
echo "[5/9] Copy project files..."
mkdir -p "$APP_DIR"
cp -r "$(dirname "$0")/../" "$APP_DIR/"
cd "$APP_DIR"

# ---------- 6. PostgreSQL ----------
echo "[6/9] Setup PostgreSQL..."
# Pastikan postgres listen di localhost only
sed -i "s/^#listen_addresses =.*/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf
sed -i "s/^listen_addresses =.*/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf || true

sudo -u postgres psql <<SQL
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER DATABASE $DB_NAME OWNER TO $DB_USER;
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
SQL

systemctl restart postgresql

# ---------- 7. Backend Setup ----------
echo "[7/9] Setup backend..."
cd "$APP_DIR/backend"

python3 -m venv venv
source venv/bin/activate

# Install PyTorch CPU + deps
pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install --no-cache-dir -r requirements.txt

cat > .env <<EOF
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
SECRET_KEY=$SECRET_KEY
UPLOAD_DIR=$APP_DIR/backend/uploads
CORS_ORIGINS=$DOMAIN
JWT_EXPIRY_HOURS=24
EOF

# Create uploads directory
mkdir -p "$APP_DIR/backend/uploads"
chown -R www-data:www-data "$APP_DIR/backend/uploads"

# Seed database
python seed.py

deactivate

# ---------- 8. Frontend Config ----------
echo "[8/9] Setup frontend config..."
cat > "$APP_DIR/frontend/config.js" <<EOF
window.API_BASE = "";
EOF

# ---------- 9. Systemd Service ----------
echo "[9/9] Install systemd service + Nginx..."
cp "$APP_DIR/deploy/detect-backend.service" /etc/systemd/system/detect-backend.service
systemctl daemon-reload
systemctl enable detect-backend
systemctl start detect-backend

# Setup Nginx
cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/detect-app

if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
fi

if [ ! -f /etc/nginx/sites-enabled/detect-app ]; then
    ln -s /etc/nginx/sites-available/detect-app /etc/nginx/sites-enabled/
fi

chown -R www-data:www-data "$APP_DIR/frontend"

nginx -t
systemctl restart nginx

# ========== SSL (Opsional) ==========
echo ""
echo "========================================"
echo "  Deploy Selesai!"
echo "========================================"
echo ""
echo "  Frontend: http://$DOMAIN"
echo "  Backend : http://localhost:8000"
echo ""
echo "  Database:"
echo "    DB Name    : $DB_NAME"
echo "    DB User    : $DB_USER"
echo "    DB Password: $DB_PASS"
echo ""
echo "  Secret Key : $SECRET_KEY"
echo ""
echo "  Firewall  : $(ufw status | grep -c active) aktif"
echo "  Fail2ban  : $(systemctl is-active fail2ban)"
echo ""
echo "  🔒 Tidak ada domain — akses via HTTP aja."
echo "  Kalo butuh SSL nanti setelah punya domain:"
echo "    sudo apt install -y certbot python3-certbot-nginx"
echo "    sudo certbot --nginx -d domain-anda.com"
echo ""
echo "  Cek status:"
echo "    sudo systemctl status detect-backend"
echo "    sudo systemctl status nginx"
echo "    sudo journalctl -u detect-backend -f"
echo ""
