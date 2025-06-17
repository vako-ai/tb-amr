# Installation Guide

## System Requirements

### Hardware Requirements

- **CPU**: 2+ cores, 2.4 GHz minimum
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 10 GB free disk space
- **Network**: Reliable internet connection

### Software Requirements

- **Operating System**:
  - Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
  - macOS 10.15+
  - Windows 10/11 with WSL2
- **Python**: 3.11 or higher
- **PostgreSQL**: 13.0 or higher
- **Git**: Latest version

### Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Installation Methods

### Method 1: Local Development Setup

#### Step 1: Install Prerequisites

**Ubuntu/Debian:**

```bash
# Update package lists
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Install Git
sudo apt install git

# Install system dependencies
sudo apt install build-essential libpq-dev python3.11-dev
```

**macOS:**

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Install PostgreSQL
brew install postgresql@13

# Install Git
brew install git

# Start PostgreSQL service
brew services start postgresql@13
```

**Windows (WSL2):**

```bash
# Install Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Install Git
sudo apt install git

# Install build dependencies
sudo apt install build-essential libpq-dev python3.11-dev
```

#### Step 2: Database Setup

**Create Database User:**

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE tb_resistance_hub;
CREATE USER tb_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE tb_resistance_hub TO tb_user;
ALTER USER tb_user CREATEDB;
\q
```

**Configure PostgreSQL (if needed):**

```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/13/main/postgresql.conf

# Ensure these settings:
listen_addresses = 'localhost'
port = 5432

# Edit pg_hba.conf for local connections
sudo nano /etc/postgresql/13/main/pg_hba.conf

# Add line for local connections:
local   all             tb_user                                 md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### Step 3: Application Installation

**Clone Repository:**

```bash
# Clone the repository
git clone https://github.com/vako-ai/tb-amr
cd tb-resistance-hub

# Verify Python version
python3.11 --version
```

**Create Virtual Environment:**

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows (WSL):
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

**Install Dependencies:**

```bash
# Install Python packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### Step 4: Configuration

**Environment Variables:**

```bash
# Create .env file
cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://tb_user:secure_password@localhost:5432/tb_resistance_hub
PGHOST=localhost
PGPORT=5432
PGUSER=tb_user
PGPASSWORD=secure_password
PGDATABASE=tb_resistance_hub

# Application Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
STREAMLIT_SERVER_HEADLESS=false
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_PORT=5000

# Optional: External API Keys
# OPENAI_API_KEY=your-openai-key
# GOOGLE_MAPS_API_KEY=your-maps-key
EOF
```

**Generate Secret Key:**

```python
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### Step 5: Database Initialization

**Initialize Database Schema:**

```bash
# Run database initialization
python3 -c "import db_manager; db_manager.initialize_database()"

# Verify tables were created
python3 -c "
import db_manager
conn = db_manager.get_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema='public'\")
    tables = cursor.fetchall()
    print('Created tables:', [table[0] for table in tables])
    conn.close()
"
```

**Seed Demo Data:**

```bash
# Load demonstration data
python3 seed_demo_data.py

# Verify data was loaded
python3 -c "
import db_manager
conn = db_manager.get_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM tb_cases')
    count = cursor.fetchone()[0]
    print(f'Loaded {count} TB cases')
    conn.close()
"
```

#### Step 6: Run Application

**Start the Application:**

```bash
# Activate virtual environment
source venv/bin/activate

# Start Streamlit server
streamlit run app.py --server.port 5000

# Application will be available at: http://localhost:5000
```

**Verify Installation:**

1. Open web browser to <http://localhost:5000>
2. Log in with default credentials:
   - Username: `admin`
   - Password: `admin123`
3. Navigate through all tabs to verify functionality
4. Test medical search feature
5. Generate a treatment recommendation

### Method 2: Docker Installation

#### Step 1: Install Docker

**Ubuntu:**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**macOS:**

```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Or use Homebrew:
brew install --cask docker
```

#### Step 2: Docker Compose Setup

**Create Docker Compose File:**

```yaml
# docker-compose.yml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://tb_user:tb_password@db:5432/tb_resistance_hub
      - PGHOST=db
      - PGPORT=5432
      - PGUSER=tb_user
      - PGPASSWORD=tb_password
      - PGDATABASE=tb_resistance_hub
      - SECRET_KEY=docker-secret-key-change-in-production
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=tb_resistance_hub
      - POSTGRES_USER=tb_user
      - POSTGRES_PASSWORD=tb_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  postgres_data:
```

**Create Dockerfile:**

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"]
```

#### Step 3: Build and Run

**Start Services:**

```bash
# Clone repository
git clone https://github.com/vako-ai/tb-amr
cd tb-resistance-hub

# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Initialize database (first time only)
docker-compose exec app python -c "import db_manager; db_manager.initialize_database()"

# Seed demo data
docker-compose exec app python seed_demo_data.py
```

**Verify Installation:**

```bash
# Check service status
docker-compose ps

# Access application
curl http://localhost:5000

# View application logs
docker-compose logs app

# Check database
docker-compose exec db psql -U tb_user -d tb_resistance_hub -c "SELECT COUNT(*) FROM tb_cases;"
```

### Method 3: Production Deployment

#### Step 1: Server Preparation

**Ubuntu Server Setup:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-pip python3.11-venv postgresql nginx certbot

# Create application user
sudo adduser tbapp
sudo usermod -aG sudo tbapp

# Switch to application user
sudo su - tbapp
```

#### Step 2: Application Deployment

**Clone and Setup:**

```bash
# Clone repository
git clone https://github.com/vako-ai/tb-amr /home/tbapp/tb-resistance-hub
cd /home/tbapp/tb-resistance-hub

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn supervisor
```

**Production Configuration:**

```bash
# Create production environment file
cat > .env.production << EOF
DATABASE_URL=postgresql://tb_user:secure_password@localhost:5432/tb_resistance_hub
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DEBUG=False
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ADDRESS=127.0.0.1
STREAMLIT_SERVER_PORT=8501
EOF
```

#### Step 3: Database Production Setup

**PostgreSQL Configuration:**

```bash
# Create production database
sudo -u postgres createdb tb_resistance_hub_prod
sudo -u postgres createuser -P tb_user_prod

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tb_resistance_hub_prod TO tb_user_prod;"

# Configure PostgreSQL for production
sudo nano /etc/postgresql/13/main/postgresql.conf
# Set: shared_buffers = 256MB, effective_cache_size = 1GB

sudo nano /etc/postgresql/13/main/pg_hba.conf
# Add: local tb_resistance_hub_prod tb_user_prod md5

sudo systemctl restart postgresql
```

#### Step 4: Process Management

**Supervisor Configuration:**

```ini
# /etc/supervisor/conf.d/tb-resistance-hub.conf
[program:tb-resistance-hub]
command=/home/tbapp/tb-resistance-hub/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1
directory=/home/tbapp/tb-resistance-hub
user=tbapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/tb-resistance-hub.log
environment=PATH="/home/tbapp/tb-resistance-hub/venv/bin"
```

**Start Services:**

```bash
# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start application
sudo supervisorctl start tb-resistance-hub

# Check status
sudo supervisorctl status
```

#### Step 5: Web Server Configuration

**Nginx Configuration:**

```nginx
# /etc/nginx/sites-available/tb-resistance-hub
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_buffering off;
    }

    # Static files
    location /static/ {
        alias /home/tbapp/tb-resistance-hub/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable Site:**

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/tb-resistance-hub /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

#### Step 6: SSL Certificate

**Let's Encrypt SSL:**

```bash
# Install SSL certificate
sudo certbot --nginx -d your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Setup auto-renewal cron job
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## Post-Installation Configuration

### Security Hardening

**Firewall Configuration:**

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

**Database Security:**

```bash
# Secure PostgreSQL
sudo nano /etc/postgresql/13/main/postgresql.conf
# Set: ssl = on, log_connections = on, log_disconnections = on

# Create backup user
sudo -u postgres createuser --no-createdb --no-createrole backup_user
sudo -u postgres psql -c "GRANT CONNECT ON DATABASE tb_resistance_hub TO backup_user;"
```

### Backup Configuration

**Database Backup Script:**

```bash
#!/bin/bash
# /home/tbapp/scripts/backup_db.sh

DB_NAME="tb_resistance_hub"
DB_USER="tb_user"
BACKUP_DIR="/home/tbapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/tb_backup_$DATE.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "tb_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: tb_backup_$DATE.sql.gz"
```

**Cron Job for Automated Backups:**

```bash
# Add to crontab
crontab -e

# Add line for daily backups at 2 AM
0 2 * * * /home/tbapp/scripts/backup_db.sh >> /home/tbapp/logs/backup.log 2>&1
```

### Monitoring Setup

**System Monitoring:**

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Setup log rotation
sudo nano /etc/logrotate.d/tb-resistance-hub
```

**Application Monitoring:**

```python
# health_check.py
import requests
import sys

def check_health():
    try:
        response = requests.get('http://localhost:8501/_stcore/health', timeout=10)
        if response.status_code == 200:
            print("Application is healthy")
            return 0
        else:
            print(f"Health check failed: {response.status_code}")
            return 1
    except Exception as e:
        print(f"Health check error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_health())
```

## Troubleshooting

### Common Installation Issues

#### Python Version Conflicts

```bash
# If python3.11 command not found
sudo apt install python3.11-distutils
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Verify version
python3 --version
```

#### PostgreSQL Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Reset password if needed
sudo -u postgres psql -c "ALTER USER tb_user PASSWORD 'new_password';"
```

#### Permission Issues

```bash
# Fix file permissions
sudo chown -R tbapp:tbapp /home/tbapp/tb-resistance-hub
sudo chmod +x /home/tbapp/tb-resistance-hub/app.py
```

#### Port Conflicts

```bash
# Check what's using port 5000
sudo lsof -i :5000

# Kill process if needed
sudo kill -9 <PID>

# Use alternative port
streamlit run app.py --server.port 8501
```

### Performance Optimization

**Database Optimization:**

```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_tb_cases_diagnosis_date ON tb_cases(diagnosis_date);
CREATE INDEX CONCURRENTLY idx_tb_cases_location ON tb_cases(location);
CREATE INDEX CONCURRENTLY idx_tb_cases_tb_type ON tb_cases(tb_type);

-- Update table statistics
ANALYZE tb_cases;
```

**Application Optimization:**

```python
# Enable Streamlit caching in config
# .streamlit/config.toml
[server]
maxUploadSize = 100
enableCORS = false
enableXsrfProtection = false

[global]
developmentMode = false
```

This installation guide provides comprehensive instructions for setting up the TB Resistance Hub in various environments, from local development to production deployment.
