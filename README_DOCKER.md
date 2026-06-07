# Docker Deployment Guide (Django + MySQL)

This guide provides step-by-step instructions on deploying the **Goldmine** Django application and its MySQL database using Docker and Docker Compose on your **KVM2 VPS** server.

---

## 🚀 Setup & Prerequisites

Before you start, make sure that **Docker** and **Docker Compose** are installed on your VPS.

### 1. Install Docker & Docker Compose (on your Ubuntu/Debian VPS)
Run these commands on your VPS terminal:
```bash
# Update package list
sudo apt update

# Install Docker
sudo apt install -y docker.io

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose (V2)
sudo apt install -y docker-compose-v2
```

---

## 📂 Project Structure for Deployment

Make sure your deployment directory on the VPS has the following structure:
```
/your-deployment-dir/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── ohwqiijn_gold_mine.sql   <-- Put your SQL dump file here
├── manage.py
├── ornament/                <-- Django project folder
└── ... (other app folders)
```

---

## 🛠️ Configuration Overview

### 1. Database Configuration
The database parameters in `ornament/settings.py` are configured to load from environment variables defined in `docker-compose.yml` (with fallback to local `127.0.0.1` settings for local running):
- **DB_HOST**: `db` (the database service name inside the Docker network)
- **DB_NAME**: `ohwqiijn_gold_mine`
- **DB_USER**: `root`
- **DB_PASSWORD**: `goldmine_secure_pass_123` (defined securely in `docker-compose.yml`)

### 2. Automatic SQL Database Import
In `docker-compose.yml`, the SQL dump file is mounted to the MySQL container's initialization directory:
```yaml
volumes:
  - ./ohwqiijn_gold_mine.sql:/docker-entrypoint-initdb.d/ohwqiijn_gold_mine.sql
```
- **How it works**: The official MySQL image automatically executes any `.sql` files placed in `/docker-entrypoint-initdb.d/` when the container is started **for the first time**. It will automatically import your dump into the `ohwqiijn_gold_mine` database!

---

## 🚀 Deployment Instructions

### Step 1: Transfer Files to VPS
Compress your project folder and transfer it to your VPS (using SCP, SFTP, or Git), ensuring `ohwqiijn_gold_mine.sql`, `docker-compose.yml`, and `Dockerfile` are all in the root deployment directory.

### Step 2: Build and Run Containers
SSH into your VPS, navigate to your project directory, and run:
```bash
sudo docker compose up -d --build
```
*This command will build the Django image, download the MySQL 8.0 image, set up the network, spin up the containers, and trigger the database initialization/import.*

### Step 3: Monitor Database Import Progress
Importing a 32MB database dump may take a few seconds to a minute depending on your VPS disk speed. Check the logs to verify the initialization is complete:
```bash
sudo docker compose logs -f db
```
Look for a message like: `ready for connections. Version: '8.0.x'`.

### Step 4: Verify Django Status & Logs
Ensure the Django application is running without any errors:
```bash
sudo docker compose logs -f web
```

---

## 🛠️ Post-Deployment Django Tasks

Run these commands inside your project folder on the VPS to finish setting up Django:

### 1. Create Django Superuser (Admin Account)
To create a new administrator account:
```bash
sudo docker compose exec web python manage.py createsuperuser
```

### 2. Collect Static Files
Serve static assets correctly by collecting them:
```bash
sudo docker compose exec web python manage.py collectstatic --noinput
```

---

## 🔄 How to Manually Re-Import or Restore SQL Database

If your database container has already been initialized and you want to **re-import** or **overwrite** it with a newer version of the SQL file, run this command:

```bash
sudo docker compose exec -T db mysql -u root -pgoldmine_secure_pass_123 ohwqiijn_gold_mine < ohwqiijn_gold_mine.sql
```

To verify the database tables are correctly imported, run:
```bash
sudo docker compose exec db mysql -u root -pgoldmine_secure_pass_123 -e "SHOW TABLES IN ohwqiijn_gold_mine;"
```

---

## 🛑 Management Commands

- **Stop the services**: `sudo docker compose down`
- **Stop services and remove volumes (WIPES DB DATA)**: `sudo docker compose down -v`
- **Restart services**: `sudo docker compose restart`
