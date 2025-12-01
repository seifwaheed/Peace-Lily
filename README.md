# Talking Plant Monitor - Python Flask Web Application

A simple, elegant web dashboard to monitor your Peace Lily plant's sensors in real-time using Python Flask.

## Features

- **Real-time Sensor Monitoring**: Display temperature, humidity, and soil moisture
- **Plant Health Status**: Automatic status indicator (Healthy/Fair/Needs Care)
- **24-Hour Statistics**: Track min/max/average values for all sensors
- **Automatic Data Collection**: Fetches data from ESP32 every 30 seconds
- **SQLite Database**: Stores historical data locally
- **Beautiful Dashboard**: Responsive, modern web interface
- **No Node.js Required**: Pure Python with Flask

## System Requirements

- **Python 3.7 or higher** (already installed on most computers)
- **ESP32 running the Talking Plant firmware** (connected to Wi-Fi)
- **Internet connection** (for local network communication)

## Installation & Setup

### Step 1: Install Python (if not already installed)

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT:** Check the box "Add Python to PATH"
4. Click "Install Now"

**Mac:**
```bash
# Using Homebrew (if installed)
brew install python3
```

**Linux:**
```bash
sudo apt-get install python3 python3-pip
```

### Step 2: Download the Flask Application

1. Download the `talking_plant_flask` folder to your computer
2. Extract it to a location you'll remember (e.g., `C:\Users\YourName\talking_plant_flask`)

### Step 3: Install Python Dependencies

Open a terminal/command prompt and navigate to the project folder:

**Windows:**
```bash
cd C:\Users\YourName\talking_plant_flask
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
cd ~/talking_plant_flask
pip3 install -r requirements.txt
```

This will install Flask and requests libraries (only needs to be done once).

### Step 4: Configure ESP32 IP Address

1. Open `app.py` in a text editor (Notepad, VS Code, etc.)
2. Find this line (around line 15):
   ```python
   ESP32_IP = "10.170.1.119"  # Change this to your ESP32's IP address
   ```
3. Replace `10.170.1.119` with your actual ESP32 IP address
4. Save the file

**How to find your ESP32 IP address:**
- Check the Arduino IDE Serial Monitor when your ESP32 boots up
- It will print something like: `IP address: 10.170.1.119`

### Step 5: Run the Application

Open a terminal/command prompt in the project folder and run:

**Windows:**
```bash
python app.py
```

**Mac/Linux:**
```bash
python3 app.py
```

You should see output like:
```
============================================================
Talking Plant Monitor - Flask Web Application
============================================================
ESP32 IP Address: 10.170.1.119
Database: plant_data.db
Poll Interval: 30 seconds

Starting web server...
Open your browser and go to: http://localhost:5000
============================================================
```

### Step 6: Open the Dashboard

1. Open your web browser (Chrome, Firefox, Safari, Edge, etc.)
2. Go to: `http://localhost:5000`
3. You should see the Talking Plant Monitor dashboard!

## How It Works

1. **Data Collection**: The Flask app runs a background thread that fetches data from your ESP32 every 30 seconds
2. **Database Storage**: All readings are stored in a local SQLite database (`plant_data.db`)
3. **Web Dashboard**: The HTML/CSS/JavaScript interface displays:
   - Current sensor readings (temperature, humidity, moisture)
   - Plant health status with warnings
   - 24-hour statistics (min/max/average values)
   - Last update timestamp

4. **Real-time Updates**: The dashboard automatically refreshes every 30 seconds

## API Endpoints

The Flask app provides these API endpoints (useful if you want to integrate with other tools):

- `GET /api/latest` - Get the latest sensor reading
- `GET /api/history/<hours>` - Get readings from the last N hours
- `GET /api/status` - Get plant health status
- `GET /api/stats` - Get 24-hour statistics

Example:
```bash
curl http://localhost:5000/api/latest
```

## Troubleshooting

### "Connection refused" or "Cannot connect to ESP32"

**Problem:** The app can't reach your ESP32
**Solution:**
1. Check that your ESP32 is powered on and connected to Wi-Fi
2. Verify the IP address in `app.py` matches your ESP32's actual IP
3. Make sure your computer and ESP32 are on the same Wi-Fi network
4. Check the Arduino IDE Serial Monitor to confirm the ESP32's IP address

### "No data available" or "Unknown" status

**Problem:** The dashboard shows no sensor data
**Solution:**
1. Wait 30 seconds for the first data fetch
2. Check that the ESP32 is running the Talking Plant firmware
3. Verify the ESP32 is returning data at `http://<ESP32_IP>/data`
4. Check the Flask app console for error messages

### Port 5000 already in use

**Problem:** "Address already in use" error
**Solution:**
1. Close any other Flask apps running on port 5000
2. Or modify the port in `app.py` (change `port=5000` to `port=5001`)

### Python not found

**Problem:** "python: command not found" or "python is not recognized"
**Solution:**
1. Make sure Python is installed and added to PATH
2. Try using `python3` instead of `python`
3. Restart your terminal/command prompt after installing Python

## File Structure

```
talking_plant_flask/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Web dashboard HTML/CSS/JavaScript
└── plant_data.db         # SQLite database (created automatically)
```

## Customization

### Change Polling Interval

Edit `app.py` and change this line:
```python
POLL_INTERVAL = 30  # Change to desired seconds
```

### Change Optimal Ranges

Edit the `get_status()` function in `app.py` to adjust what's considered "optimal":
```python
# Check temperature (optimal: 20-25°C, acceptable: 18-29°C)
if temp < 18 or temp > 29:
    issues.append(f"Temperature out of range: {temp}°C")
```

### Change Dashboard Port

Edit `app.py` and change this line:
```python
app.run(debug=False, host='localhost', port=5000)  # Change 5000 to desired port
```

## Stopping the Application

Press `Ctrl+C` in the terminal/command prompt where the Flask app is running.

## Next Steps

1. **Add Email Alerts**: Modify `app.py` to send email notifications when plant needs water
2. **Export Data**: Add a feature to download historical data as CSV
3. **Mobile App**: Create a mobile-friendly version or native app
4. **Multiple Plants**: Extend the database to monitor multiple plants
5. **Graphing**: Add charts using a JavaScript graphing library

## Support

If you encounter issues:

1. Check the Flask app console for error messages
2. Verify your ESP32 IP address and connectivity
3. Make sure all dependencies are installed: `pip install -r requirements.txt`
4. Restart both the Flask app and ESP32

## License

This project is open source and available for personal use.

---

**Happy plant monitoring! 🌿**
