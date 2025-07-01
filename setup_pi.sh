#!/bin/bash
# Traffic Management System Setup Script for Raspberry Pi
# Run with: bash setup_pi.sh

set -e  # Exit on any error

echo "🚦 Traffic Management System Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✓ System check passed${NC}"

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
echo "📦 Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    mysql-server \
    git \
    nginx \
    supervisor

# Enable GPIO and camera
echo "🔧 Enabling Pi hardware interfaces..."
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0

# Create project directory
PROJECT_DIR="/home/pi/traffic-system"
echo "📁 Setting up project directory: $PROJECT_DIR"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Set up Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📦 Installing Python dependencies..."
cd btrafficProjectv2
pip install -r requirements.txt
cd ../pitrafficProjectv2
pip install -r requirements.txt
cd ..

# Set up MySQL database
echo "🗄️  Setting up MySQL database..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS traffic_dbP;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'traffic_user'@'localhost' IDENTIFIED BY 'secure_traffic_pass';"
sudo mysql -e "GRANT ALL PRIVILEGES ON traffic_dbP.* TO 'traffic_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Create systemd services
echo "⚙️  Installing system services..."
sudo cp traffic-api.service /etc/systemd/system/
sudo cp traffic-pi.service /etc/systemd/system/

# Update service file paths
sudo sed -i "s|/home/pi/traffic-system|$PROJECT_DIR|g" /etc/systemd/system/traffic-api.service
sudo sed -i "s|/home/pi/traffic-system|$PROJECT_DIR|g" /etc/systemd/system/traffic-pi.service

# Reload systemd and enable services
sudo systemctl daemon-reload
sudo systemctl enable traffic-api.service
sudo systemctl enable traffic-pi.service

# Create startup script
echo "🚀 Creating startup commands..."
echo "# Traffic System Management" >> ~/.bashrc
echo "alias traffic-start='sudo systemctl start traffic-api && sudo systemctl start traffic-pi'" >> ~/.bashrc
echo "alias traffic-stop='sudo systemctl stop traffic-pi && sudo systemctl stop traffic-api'" >> ~/.bashrc
echo "alias traffic-status='sudo systemctl status traffic-api traffic-pi'" >> ~/.bashrc
echo "alias traffic-logs='sudo journalctl -f -u traffic-api -u traffic-pi'" >> ~/.bashrc

echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Update database credentials in /etc/systemd/system/traffic-api.service"
echo "2. Configure your React app to connect to: http://$(hostname -I | awk '{print $1}'):8000"
echo "3. Start the services: sudo systemctl start traffic-api traffic-pi"
echo "4. Check logs: sudo journalctl -f -u traffic-api -u traffic-pi"
echo ""
echo "🔧 Useful commands:"
echo "• traffic-start    - Start both services"
echo "• traffic-stop     - Stop both services"  
echo "• traffic-status   - Check service status"
echo "• traffic-logs     - View live logs"
echo ""
echo -e "${YELLOW}⚠️  Remember to reboot after setup: sudo reboot${NC}" 