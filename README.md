# 🚦 Intelligent Traffic Management System

A complete traffic management solution with Raspberry Pi hardware control, computer vision-based vehicle detection, and a REST API backend for React SPA integration.

## 📋 System Overview

- **Backend API**: FastAPI server providing REST endpoints for React frontend
- **Pi Controller**: Real-time traffic light control with camera-based vehicle detection  
- **Computer Vision**: YOLO-based vehicle counting for intelligent traffic decisions
- **Database**: MySQL storage for traffic logs, analytics, and system monitoring
- **Web Interface**: REST API endpoints for React SPA dashboard

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React SPA     │───▶│   FastAPI        │───▶│   MySQL         │
│   Dashboard     │    │   Backend        │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Raspberry Pi   │
                       │   Controller     │
                       │   • GPIO LEDs    │
                       │   • Camera       │
                       │   • YOLO Vision  │
                       └──────────────────┘
```

## 🔧 Hardware Requirements

### Raspberry Pi Setup
- **Raspberry Pi 4** (recommended) or Pi 3B+
- **8GB+ SD Card** with Raspberry Pi OS
- **USB Camera** or Pi Camera module
- **GPIO-connected LEDs** for traffic light simulation:
  - 12 LEDs total (3 colors × 4 lanes)
  - Resistors (220-330Ω)
  - Breadboard and jumper wires

### LED Wiring (GPIO Pins)
```
Lane 1: Red=2,  Yellow=3,  Green=4
Lane 2: Red=17, Yellow=27, Green=22  
Lane 3: Red=10, Yellow=9,  Green=11
Lane 4: Red=5,  Yellow=6,  Green=13
```

## 🚀 Quick Setup

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd FYP2025Backend-pi-full-
```

### 2. Run Setup Script
```bash
chmod +x setup_pi.sh
bash setup_pi.sh
```

### 3. Configure Database Credentials
```bash
sudo nano /etc/systemd/system/traffic-api.service
# Update DB_PASSWORD and other credentials
```

### 4. Start Services
```bash
sudo systemctl start traffic-api traffic-pi
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login` - Admin login

### Traffic Management  
- `POST /api/decision` - Process vehicle count and get traffic decision
- `GET /api/status` - Get current system status
- `POST /api/manual` - Send manual traffic control commands
- `GET /api/manual` - Get manual command history

### Analytics & Reporting
- `GET /api/analytics` - Get traffic analytics summary
- `GET /api/reports` - Get all traffic logs
- `POST /api/reports/filter` - Get filtered traffic reports

### Monitoring
- `GET /api/monitoring` - Get system monitoring data

## 🔧 Configuration

### Environment Variables

**API Server** (`traffic-api.service`):
```bash
DB_HOST=localhost
DB_PORT=3306  
DB_USER=traffic_user
DB_PASSWORD=your_secure_password
DB_NAME=traffic_dbP
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://192.168.1.164:3000
```

**Pi Controller** (`traffic-pi.service`):
```bash
BACKEND_HOST=localhost
BACKEND_PORT=8000
```

### React Frontend Configuration
Update your React app to connect to:
```javascript
const API_BASE_URL = 'http://YOUR_PI_IP:8000/api';
```

## 📊 Database Schema

### Key Tables
- `admin_users` - Admin authentication
- `traffic_logs` - Traffic decisions and events  
- `captured_images` - Camera snapshots
- `yolo_boxed_images` - Processed detection images
- `manual_control_commands` - Manual override commands

## 🔍 System Monitoring

### Service Management
```bash
# Start services
traffic-start

# Stop services  
traffic-stop

# Check status
traffic-status

# View logs
traffic-logs
```

### Manual Service Control
```bash
# Individual service control
sudo systemctl start/stop/restart traffic-api
sudo systemctl start/stop/restart traffic-pi

# View specific logs
sudo journalctl -u traffic-api -f
sudo journalctl -u traffic-pi -f
```

## 🐛 Troubleshooting

### Common Issues

**1. Backend Connection Failed**
```bash
# Check if API is running
curl http://localhost:8000/api/status

# Check service status
sudo systemctl status traffic-api
```

**2. Camera Not Working**
```bash
# Test camera
vcgencmd get_camera

# Enable camera interface  
sudo raspi-config
```

**3. GPIO Permission Errors**
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi
```

**4. Database Connection Issues**
```bash
# Check MySQL status
sudo systemctl status mysql

# Test database connection
mysql -u traffic_user -p traffic_dbP
```

### Log Analysis
```bash
# API logs
sudo journalctl -u traffic-api --since "1 hour ago"

# Pi controller logs  
sudo journalctl -u traffic-pi --since "1 hour ago"

# System logs
dmesg | grep -i error
```

## 🔒 Security Considerations

### Production Checklist
- [ ] Change default database passwords
- [ ] Update CORS origins to specific domains
- [ ] Enable HTTPS with SSL certificates
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Monitor system logs

### Firewall Setup
```bash
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 8000  # API
sudo ufw allow from 192.168.1.0/24 to any port 8000  # Local network only
```

## 📈 Performance Optimization

### For Raspberry Pi 4
- Ensure adequate cooling
- Use high-speed SD card (Class 10+)
- Monitor CPU/memory usage: `htop`

### Database Optimization
- Regular cleanup of old logs
- Index optimization for large datasets
- Connection pooling configuration

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review system logs
3. Create an issue on GitHub
4. Contact the development team

---

**Status**: ✅ Production Ready for Local Deployment 