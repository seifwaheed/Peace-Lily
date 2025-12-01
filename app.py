import serial
import json
import sqlite3
from flask import Flask, render_template, jsonify
from datetime import datetime
import threading
import time

app = Flask(__name__)

# --- Configuration ---
SERIAL_PORT = "COM6"  # Change to your ESP32's COM port (Windows: COM3, COM4, etc.)
                      # On Mac/Linux: /dev/ttyUSB0 or /dev/ttyACM0
BAUD_RATE = 115200
DATABASE = "plant_data.db"

# Moisture sensor calibration
# Raw value 1700 = fully watered (wet)
# Raw value 3000 = completely dry
MOISTURE_WET_VALUE = 1700
MOISTURE_DRY_VALUE = 3000

# Default values
DEFAULT_MOISTURE_PERCENT = 50  # Default moisture when sensor data not available

# Moisture thresholds (in percentage)
MOISTURE_DRY_THRESHOLD = 30    # Below this = too dry, needs water
MOISTURE_WET_THRESHOLD = 75    # Above this = too wet, reduce watering
MOISTURE_OPTIMAL_MIN = 50      # Optimal range minimum
MOISTURE_OPTIMAL_MAX = 60      # Optimal range maximum

# --- Global variables ---
latest_data = {
    "temperature": None,
    "humidity": None,
    "moisture": None,
    "timestamp": None
}

# --- Initialize Database ---
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS readings
                 (id INTEGER PRIMARY KEY, 
                  temperature REAL, 
                  humidity REAL, 
                  moisture INTEGER, 
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

# --- Convert raw moisture sensor value to percentage ---
def convert_moisture_raw_to_percent(raw_value):
    """
    Convert raw moisture sensor reading to percentage.
    Lower raw values = wetter, higher raw values = drier
    Raw 1700 = 100% (fully watered)
    Raw 3000 = 0% (completely dry)
    """
    # Clamp the raw value to the expected range
    raw_value = max(MOISTURE_WET_VALUE, min(MOISTURE_DRY_VALUE, raw_value))
    
    # Convert: lower raw = higher percentage (inverted scale)
    # Formula: percentage = ((dry_value - raw_value) / (dry_value - wet_value)) * 100
    percentage = ((MOISTURE_DRY_VALUE - raw_value) / (MOISTURE_DRY_VALUE - MOISTURE_WET_VALUE)) * 100
    
    # Round to integer and clamp to 0-100
    return max(0, min(100, int(round(percentage))))

# --- Check if value is likely a raw sensor reading vs percentage ---
def is_raw_moisture_value(value):
    """
    Determine if the moisture value is a raw sensor reading (1700-3000 range)
    or already a percentage (0-100 range)
    """
    return 500 <= value <= 4000  # Raw values typically in this range

# --- Read from Serial Port ---
def read_serial_data():
    global latest_data
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to ESP32 on {SERIAL_PORT}")
    except Exception as e:
        print(f"Error connecting to serial port: {e}")
        return
    
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                
                # Parse data in format: TEMP:24.5,HUM:65.0,MOIST:55 or MOIST:1700 (raw)
                if line.startswith("TEMP:"):
                    try:
                        parts = line.split(",")
                        temp = float(parts[0].split(":")[1])
                        hum = float(parts[1].split(":")[1])
                        moist_raw = int(parts[2].split(":")[1])
                        
                        # Convert raw moisture value to percentage if needed
                        if is_raw_moisture_value(moist_raw):
                            moist = convert_moisture_raw_to_percent(moist_raw)
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Moisture: raw={moist_raw} -> {moist}%")
                        else:
                            moist = moist_raw  # Already a percentage
                        
                        # Update latest data
                        latest_data = {
                            "temperature": temp,
                            "humidity": hum,
                            "moisture": moist,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        # Store in database
                        conn = sqlite3.connect(DATABASE)
                        c = conn.cursor()
                        c.execute("INSERT INTO readings (temperature, humidity, moisture, timestamp) VALUES (?, ?, ?, ?)",
                                  (temp, hum, moist, datetime.now()))
                        conn.commit()
                        conn.close()
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Data stored: Temp={temp}°C, Humidity={hum}%, Moisture={moist}%")
                    
                    except Exception as e:
                        print(f"Error parsing data: {e}")
                
                # Parse data in format: Temp: 25.00°C | Humidity: 53.40%
                elif "Temp:" in line and "Humidity:" in line:
                    try:
                        # Extract temperature: "Temp: 25.00°C"
                        temp_part = line.split("Temp:")[1].split("°C")[0].strip()
                        temp = float(temp_part)
                        
                        # Extract humidity: "Humidity: 53.40%"
                        hum_part = line.split("Humidity:")[1].split("%")[0].strip()
                        hum = float(hum_part)
                        
                        # Try to extract moisture if present: "Moisture: 55%" or "Moisture: 1700" (raw)
                        moist = None
                        if "Moisture:" in line:
                            # Extract moisture value (could be percentage or raw)
                            moist_str = line.split("Moisture:")[1].strip()
                            # Remove % if present, then convert to number
                            moist_str = moist_str.split("%")[0].strip()
                            moist_raw = int(float(moist_str))
                            
                            # Convert raw moisture value to percentage if needed
                            if is_raw_moisture_value(moist_raw):
                                moist = convert_moisture_raw_to_percent(moist_raw)
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] Moisture: raw={moist_raw} -> {moist}%")
                            else:
                                moist = moist_raw  # Already a percentage
                        else:
                            # Default moisture value if not provided
                            moist = DEFAULT_MOISTURE_PERCENT
                        
                        # Update latest data
                        latest_data = {
                            "temperature": temp,
                            "humidity": hum,
                            "moisture": moist,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        # Store in database
                        conn = sqlite3.connect(DATABASE)
                        c = conn.cursor()
                        c.execute("INSERT INTO readings (temperature, humidity, moisture, timestamp) VALUES (?, ?, ?, ?)",
                                  (temp, hum, moist, datetime.now()))
                        conn.commit()
                        conn.close()
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Data stored: Temp={temp}°C, Humidity={hum}%, Moisture={moist}%")
                    
                    except Exception as e:
                        print(f"Error parsing data: {e}")
                        print(f"  Line was: {line}")
                else:
                    # Print other serial output for debugging
                    print(f"[ESP32] {line}")
        
        except Exception as e:
            print(f"Serial read error: {e}")
            time.sleep(1)

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/latest')
def get_latest():
    return jsonify(latest_data)

@app.route('/api/history/<int:hours>')
def get_history(hours):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(f"SELECT * FROM readings WHERE timestamp > datetime('now', '-{hours} hours') ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    
    data = [{"temperature": row[1], "humidity": row[2], "moisture": row[3], "timestamp": row[4]} for row in rows]
    return jsonify(data)

@app.route('/api/status')
def get_status():
    if latest_data["temperature"] is None:
        return jsonify({
            "status": "Unknown", 
            "message": "Waiting for data from ESP32...",
            "temperature": None,
            "humidity": None,
            "moisture": None
        })
    
    temp = latest_data["temperature"]
    hum = latest_data["humidity"]
    moist = latest_data["moisture"]
    
    issues = []
    
    # Check temperature (optimal: 20-25°C)
    if temp < 18 or temp > 29:
        issues.append(f"Temperature out of range: {temp}°C")
    
    # Check humidity (optimal: 50-80%)
    if hum < 40 or hum > 90:
        issues.append(f"Humidity out of range: {hum}%")
    
    # Check moisture (optimal: 50-60%)
    if moist < MOISTURE_DRY_THRESHOLD:
        issues.append("Soil too dry - needs water!")
    elif moist > MOISTURE_WET_THRESHOLD:
        issues.append("Soil too wet - reduce watering")
    
    if issues:
        status = "Fair" if len(issues) == 1 else "Needs Care"
    else:
        status = "Healthy"
    
    return jsonify({
        "status": status,
        "issues": issues,
        "temperature": temp,
        "humidity": hum,
        "moisture": moist
    })

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT AVG(temperature), MIN(temperature), MAX(temperature), AVG(humidity), MIN(humidity), MAX(humidity), AVG(moisture), MIN(moisture), MAX(moisture) FROM readings WHERE timestamp > datetime('now', '-24 hours')")
    row = c.fetchone()
    conn.close()
    
    if row[0] is None:
        return jsonify({"message": "No data available yet"})
    
    return jsonify({
        "temperature": {"avg": round(row[0], 1), "min": round(row[1], 1), "max": round(row[2], 1)},
        "humidity": {"avg": round(row[3], 1), "min": round(row[4], 1), "max": round(row[5], 1)},
        "moisture": {"avg": round(row[6], 1), "min": round(row[7], 1), "max": round(row[8], 1)}
    })

# --- Main ---
if __name__ == '__main__':
    init_db()
    
    # Start serial reading in background thread
    serial_thread = threading.Thread(target=read_serial_data, daemon=True)
    serial_thread.start()
    
    print("\n" + "="*60)
    print("Talking Plant Monitor - Flask Web Application")
    print("="*60)
    print(f"Serial Port: {SERIAL_PORT}")
    print(f"Baud Rate: {BAUD_RATE}")
    print(f"Database: {DATABASE}")
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5000" )
    print("="*60 + "\n")
    
    app.run(debug=False, host='localhost', port=5000)
