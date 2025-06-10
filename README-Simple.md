# TB-AMR Simple Docker Deployment

A minimal Docker setup for the TB-AMR (Tuberculosis Antimicrobial Resistance) application.

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Ports 80 and 443 available

### Deploy

1. **Clone and setup:**

   ```bash
   git clone <your-repo>
   cd tb-amr
   cp env.example .env
   ```

2. **Edit `.env` file:**

   ```bash
   # For localhost development
   DOMAIN=localhost
   ACME_EMAIL=admin@localhost

   # For production with your domain
   DOMAIN=yourdomain.com
   ACME_EMAIL=admin@yourdomain.com

   # Set a secure password
   POSTGRES_PASSWORD=your_secure_password_here
   ```

3. **Start services:**

   ```bash
   docker-compose up -d
   ```

4. **Seed database (optional):**

   ```bash
   docker-compose exec tb-amr-app python seed_demo_data.py
   ```

### Access

- **Application:** <https://localhost> (or <https://yourdomain.com>)
- **Traefik Dashboard:** <https://traefik.localhost> (or <https://traefik.yourdomain.com>)

### Management

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update and restart
docker-compose down
docker-compose pull
docker-compose up -d --build
```

## Services

- **tb-amr-app:** Main Streamlit application
- **postgres:** PostgreSQL database
- **traefik:** Reverse proxy with automatic HTTPS

## Notes

- SSL certificates are automatically generated via Let's Encrypt
- For localhost development, you may need to accept self-signed certificates
- Default login: admin / admin123
