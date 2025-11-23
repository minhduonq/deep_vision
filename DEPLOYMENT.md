# Deployment Guide

## 🚀 Hướng dẫn triển khai Deep Vision

Guide này hướng dẫn deploy Deep Vision lên các platform phổ biến.

## Pre-deployment Checklist

- [ ] Code hoàn thiện và tested
- [ ] Environment variables configured
- [ ] API keys secured
- [ ] Dependencies listed in requirements.txt
- [ ] Docker images tested locally
- [ ] Documentation updated

## Option 1: Deploy với Docker (Local hoặc VPS)

### Prerequisites
- Docker và Docker Compose đã cài đặt
- API keys đã có

### Steps

```powershell
# 1. Clone repository
git clone https://github.com/yourusername/deep_vision.git
cd deep_vision

# 2. Setup environment
copy .env.example .env
# Edit .env với API keys của bạn

# 3. Build và run với Docker Compose
docker-compose -f docker/docker-compose.yml up -d

# 4. Check logs
docker-compose -f docker/docker-compose.yml logs -f

# 5. Access application
# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

### Stop và cleanup

```powershell
# Stop containers
docker-compose -f docker/docker-compose.yml down

# Remove volumes
docker-compose -f docker/docker-compose.yml down -v
```

## Option 2: Deploy lên Railway

### Why Railway?
- Free tier generous
- Easy deployment
- Auto-scaling
- Built-in monitoring

### Steps

1. **Tạo account tại railway.app**

2. **Install Railway CLI**
```powershell
npm install -g @railway/cli
railway login
```

3. **Initialize project**
```powershell
railway init
```

4. **Deploy backend**
```powershell
# Tạo service mới
railway up

# Set environment variables
railway variables set OPENAI_API_KEY=your_key
railway variables set REPLICATE_API_TOKEN=your_token
railway variables set DEVICE=cpu
```

5. **Deploy frontend (separate service)**
```powershell
# Tạo service mới cho frontend
railway add

# Link to backend
railway variables set API_BASE_URL=https://your-backend-url.railway.app
```

## Option 3: Deploy lên Render

### Why Render?
- Simple deployment
- Free SSL
- Auto-deploy from Git
- Good for APIs

### Steps

1. **Create account tại render.com**

2. **Create Web Service**
   - Connect GitHub repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`

3. **Configure Environment Variables**
   - Add API keys
   - Set `DEVICE=cpu`
   - Set `PORT=8000`

4. **Deploy Frontend (separate service)**
   - Build Command: `pip install streamlit requests pillow`
   - Start Command: `streamlit run frontend/streamlit_app.py --server.port $PORT`

## Option 4: Deploy lên Google Cloud Run

### Why Cloud Run?
- Serverless
- Pay per use
- Auto-scaling
- Good for variable traffic

### Steps

1. **Install gcloud CLI**
```powershell
# Download từ https://cloud.google.com/sdk/docs/install
```

2. **Build và push Docker image**
```powershell
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/deepvision-backend

# Deploy
gcloud run deploy deepvision-backend \
  --image gcr.io/YOUR_PROJECT_ID/deepvision-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your_key,REPLICATE_API_TOKEN=your_token
```

## Option 5: Deploy lên AWS (EC2 + Docker)

### Prerequisites
- AWS account
- EC2 instance (t2.medium hoặc lớn hơn)

### Steps

1. **Launch EC2 instance**
   - Amazon Linux 2 hoặc Ubuntu
   - Open ports: 22, 8000, 8501

2. **Connect to instance**
```bash
ssh -i your-key.pem ec2-user@your-instance-ip
```

3. **Install Docker**
```bash
# Amazon Linux 2
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

4. **Clone và deploy**
```bash
git clone https://github.com/yourusername/deep_vision.git
cd deep_vision
cp .env.example .env
nano .env  # Edit với API keys

docker-compose -f docker/docker-compose.yml up -d
```

5. **Setup reverse proxy với Nginx (optional)**
```bash
sudo yum install nginx -y

# Configure nginx
sudo nano /etc/nginx/nginx.conf
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## Option 6: Deploy lên Hugging Face Spaces

### Why Hugging Face Spaces?
- Free hosting
- Great for ML demos
- Easy to use
- Built-in Streamlit support

### Steps

1. **Create Space tại huggingface.co/spaces**
   - Choose Streamlit SDK
   - Public hoặc Private

2. **Upload files**
   - Upload `streamlit_app.py`
   - Upload `requirements.txt`
   - Create `README.md` với config:

```yaml
---
title: Deep Vision
emoji: 🎨
colorFrom: purple
colorTo: blue
sdk: streamlit
sdk_version: 1.30.0
app_file: streamlit_app.py
pinned: false
---
```

3. **Add secrets**
   - Go to Settings → Secrets
   - Add API keys

**Note**: Backend cần deploy riêng (vì Spaces chỉ host frontend)

## Environment Variables Checklist

### Required
```bash
OPENAI_API_KEY=sk-...
REPLICATE_API_TOKEN=r8_...
```

### Optional
```bash
ANTHROPIC_API_KEY=sk-ant-...
STABILITY_API_KEY=sk-...
HUGGINGFACE_API_TOKEN=hf_...
```

### Configuration
```bash
DEVICE=cpu  # or cuda
DEBUG=False
MAX_CONCURRENT_TASKS=3
MAX_IMAGE_SIZE=2048
```

## Security Best Practices

1. **Never commit API keys**
   - Use `.gitignore`
   - Use environment variables
   - Use secrets management services

2. **Use HTTPS**
   - Enable SSL/TLS
   - Use reverse proxy
   - Force HTTPS redirect

3. **Rate limiting**
   - Implement per-user limits
   - Use API gateway
   - Monitor usage

4. **Input validation**
   - File size limits
   - File type checking
   - Sanitize inputs

5. **Authentication**
   - Add API key authentication
   - Use JWT tokens
   - Implement OAuth (optional)

## Monitoring & Maintenance

### Logging
- Use structured logging
- Centralize logs (e.g., CloudWatch, Datadog)
- Set up alerts

### Monitoring
- Track API latency
- Monitor error rates
- Check GPU/CPU usage
- Monitor costs

### Backup
- Regular backups of user data
- Version control for code
- Document deployment steps

## Cost Estimation

### API-Only Approach
- **Replicate**: ~$0.001-0.01 per image
- **OpenAI**: ~$0.002 per request (GPT-3.5)
- **Hosting**: $0-20/month (free tiers available)

**Total**: ~$20-50/month for moderate usage (100-500 images/day)

### Hybrid Approach
- **GPU Instance**: $50-200/month (AWS p3.2xlarge, GCP T4)
- **API costs**: Reduced
- **Storage**: $5-20/month

**Total**: ~$60-250/month

### Full Local
- **GPU Server**: $100-500/month (dedicated)
- **Storage**: $10-50/month
- **No API costs**

**Total**: ~$110-550/month + infrastructure costs

## Scaling Strategies

### Vertical Scaling
- Upgrade instance type
- Add more GPUs
- Increase memory

### Horizontal Scaling
- Load balancer
- Multiple workers
- Distributed processing

### Cost Optimization
- Use spot instances
- Auto-scaling based on traffic
- Cache results
- Batch processing

## Troubleshooting

### Common Issues

**1. Out of Memory**
```python
# Solution: Enable optimizations
pipe.enable_attention_slicing()
pipe.enable_model_cpu_offload()
```

**2. Slow API responses**
```python
# Solution: Use caching
# Implement Redis caching for common requests
```

**3. Connection timeout**
```python
# Solution: Increase timeout
requests.post(url, timeout=300)
```

## Support & Resources

- **Documentation**: Check `/docs` folder
- **Issues**: GitHub Issues
- **Community**: Discord/Slack
- **Email**: support@yourdomain.com

## Next Steps After Deployment

1. [ ] Monitor performance metrics
2. [ ] Gather user feedback
3. [ ] Iterate on features
4. [ ] Optimize costs
5. [ ] Scale as needed
6. [ ] Document learnings

---

**Remember**: Start small, monitor closely, scale gradually! 🚀

Good luck with your deployment!
