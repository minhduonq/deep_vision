# Deployment Guide - Deep Vision

Hướng dẫn triển khai ứng dụng Deep Vision lên môi trường production.

## 1. Yêu cầu Production

### Hệ thống
- Ubuntu 20.04+ hoặc CentOS 8+
- Python 3.8+
- Nginx (khuyến nghị)
- Gunicorn hoặc uWSGI

### Bảo mật
- SSL/TLS certificate (Let's Encrypt)
- Firewall configuration
- Rate limiting

## 2. Cài đặt trên Server

### Bước 1: Clone repository

```bash
cd /var/www
git clone https://github.com/minhduonq/deep_vision.git
cd deep_vision
```

### Bước 2: Tạo virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies

```bash
pip install -r requirements.txt
pip install gunicorn
```

### Bước 4: Tạo file cấu hình Gunicorn

Tạo file `gunicorn_config.py`:

```python
# Gunicorn configuration file
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/deep_vision/access.log"
errorlog = "/var/log/deep_vision/error.log"
loglevel = "info"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
```

### Bước 5: Tạo systemd service

Tạo file `/etc/systemd/system/deep_vision.service`:

```ini
[Unit]
Description=Deep Vision Image Editing Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/deep_vision
Environment="PATH=/var/www/deep_vision/venv/bin"
Environment="FLASK_DEBUG=false"
ExecStart=/var/www/deep_vision/venv/bin/gunicorn \
    --config gunicorn_config.py \
    server:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Bước 6: Khởi động service

```bash
# Tạo thư mục log
sudo mkdir -p /var/log/deep_vision
sudo chown www-data:www-data /var/log/deep_vision

# Reload systemd và khởi động service
sudo systemctl daemon-reload
sudo systemctl start deep_vision
sudo systemctl enable deep_vision
sudo systemctl status deep_vision
```

## 3. Cấu hình Nginx

Tạo file `/etc/nginx/sites-available/deep_vision`:

```nginx
upstream deep_vision {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Client upload size limit
    client_max_body_size 20M;

    # Static files
    location /static/ {
        alias /var/www/deep_vision/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://deep_vision;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Rate limiting for upload endpoint
    location /api/upload {
        limit_req zone=upload_limit burst=5;
        proxy_pass http://deep_vision;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}

# Rate limiting configuration
limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=10r/m;
```

Kích hoạt site:

```bash
sudo ln -s /etc/nginx/sites-available/deep_vision /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 4. Cấu hình SSL với Let's Encrypt

```bash
# Cài đặt certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Lấy certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl status certbot.timer
```

## 5. Cấu hình Firewall

```bash
# UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Hoặc iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

## 6. Monitoring và Logging

### Log rotation

Tạo file `/etc/logrotate.d/deep_vision`:

```
/var/log/deep_vision/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload deep_vision > /dev/null 2>&1 || true
    endscript
}
```

### Monitoring với systemd

```bash
# Check status
sudo systemctl status deep_vision

# View logs
sudo journalctl -u deep_vision -f

# Check Gunicorn logs
tail -f /var/log/deep_vision/access.log
tail -f /var/log/deep_vision/error.log
```

## 7. Performance Optimization

### Caching với Redis (Optional)

```bash
pip install redis flask-caching
```

Thêm vào `server.py`:

```python
from flask_caching import Cache

cache_config = {
    "CACHE_TYPE": "redis",
    "CACHE_REDIS_HOST": "localhost",
    "CACHE_REDIS_PORT": 6379,
    "CACHE_REDIS_DB": 0,
    "CACHE_DEFAULT_TIMEOUT": 300
}
app.config.from_mapping(cache_config)
cache = Cache(app)

@app.route('/api/operations', methods=['GET'])
@cache.cached(timeout=3600)
def get_operations():
    # ...
```

### Database cho metadata (Optional)

Nếu cần lưu trữ metadata của ảnh:

```bash
pip install flask-sqlalchemy
```

## 8. Backup Strategy

```bash
# Tạo script backup
cat > /usr/local/bin/backup_deep_vision.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/deep_vision"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/deep_vision/uploads

# Keep only last 7 days
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup_deep_vision.sh

# Add to crontab
echo "0 2 * * * /usr/local/bin/backup_deep_vision.sh" | sudo crontab -
```

## 9. Scaling

### Horizontal Scaling với Load Balancer

```nginx
upstream deep_vision_cluster {
    least_conn;
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
}

server {
    # ...
    location / {
        proxy_pass http://deep_vision_cluster;
        # ...
    }
}
```

### Vertical Scaling

Điều chỉnh số workers trong `gunicorn_config.py`:

```python
workers = 8  # Tăng số workers
worker_class = "gevent"  # Sử dụng gevent cho I/O bound
```

## 10. Health Check

Thêm endpoint health check vào `server.py`:

```python
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200
```

Cấu hình monitoring với Nginx:

```nginx
location /health {
    access_log off;
    proxy_pass http://deep_vision;
}
```

## 11. Troubleshooting

### Service không khởi động

```bash
sudo systemctl status deep_vision
sudo journalctl -u deep_vision -n 50
```

### Port đã được sử dụng

```bash
sudo lsof -i :8000
sudo netstat -tulpn | grep 8000
```

### Memory issues

```bash
# Check memory usage
free -h
htop

# Restart service
sudo systemctl restart deep_vision
```

## 12. Security Checklist

- [ ] SSL/TLS enabled
- [ ] Firewall configured
- [ ] Rate limiting enabled
- [ ] Debug mode disabled
- [ ] File upload size limited
- [ ] Secure file handling
- [ ] Regular security updates
- [ ] Log monitoring
- [ ] Backup strategy
- [ ] Access control

## Tài liệu tham khảo

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Let's Encrypt](https://letsencrypt.org/)
