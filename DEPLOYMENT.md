# KloudCart AWS EC2 Deployment Guide

Simple guide to deploy KloudCart on AWS EC2 Free Tier.

## Prerequisites

- AWS Account
- EC2 key pair (.pem file)
- GitHub repository URL

---

## Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2 → Launch Instance
2. Settings:
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance**: t3.micro (Free Tier) - or t2.micro in older regions
   - **Key pair**: Create/download `.pem` file
   - **Security Group**: Allow HTTP (port 80) and SSH (port 22)
3. Launch and note your **Public IP**

---

## Step 2: Connect to EC2

**Windows (PowerShell):**
```powershell
ssh -i "key-name.pem" ubuntu@<YOUR_EC2_IP>
```

**Linux/Mac:**
```bash
chmod 400 key-name.pem
ssh -i key-name.pem ubuntu@<YOUR_EC2_IP>
```

---

## Step 3: Install Docker

Run these commands on your EC2 instance:

```bash
# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
exit
```

**Reconnect** and verify:
```bash
ssh -i key-name.pem ubuntu@<YOUR_EC2_IP>
docker --version
```

---

## Step 4: Setup Project

```bash
# Install Git
sudo apt-get install -y git

# Clone your repo
git clone https://github.com/yourusername/kloudcart.git
cd kloudcart

# Create .env file
cp env_example.txt .env
nano .env
```

**Fill in your `.env` file:**
```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/kloudcart
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

## Step 5: Deploy

```bash
# Build and start
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f
```

If you see "MongoDB connection initialized successfully!" - you're done! 🎉

---

## Step 6: Access Your App

Open in browser: `http://<YOUR_EC2_IP>/`

---

## Common Commands

```bash
# View logs
docker compose logs -f

# Restart
docker compose restart

# Stop
docker compose down

# Rebuild after code changes
docker compose up -d --build
```

---

## Troubleshooting

**Container won't start?**
```bash
docker compose logs
```

**Can't access from browser?**
- Check Security Group allows port 80
- Verify container is running: `docker ps`

**MongoDB connection fails?**
- Check `.env` file has correct `MONGO_URI`
- Add EC2 IP to MongoDB Atlas Network Access

---

## Security Tips

- Never commit `.env` file (already in `.gitignore`)
- Generate strong SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
- Restrict SSH to your IP only in Security Group

---

**That's it! Your app should be live. 🚀**
