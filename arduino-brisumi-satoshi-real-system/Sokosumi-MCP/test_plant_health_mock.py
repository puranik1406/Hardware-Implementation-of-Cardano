"""
Plant Health Monitoring Service - Mock Data Test
Tests Sokosumi integration with simulated Aloe Vera sensor data
"""

import asyncio
import httpx
import json
from datetime import datetime
from pathlib import Path

# Sokosumi Configuration
SOKOSUMI_API_KEY = "TBLHiLvybvTcoBzujMOzIoKoEVWrSAEXpWYsTByfTlfKfqAfsxwRlJoeWOnEgQZU"
SOKOSUMI_BASE_URL = "https://app.sokosumi.com/api"

# Report Storage
REPORTS_DIR = Path("../plant_reports")
REPORTS_DIR.mkdir(exist_ok=True)

# Mock Sensor Data for Aloe Vera
MOCK_PLANT_DATA = {
    "plant_type": "Aloe Vera",
    "plant_id": "aloe_001",
    "location": "Indoor Garden - Arduino Station",
    "sensor_data": {
        "soil_moisture": 65,      # 65% - Optimal for Aloe Vera (60-70%)
        "soil_moisture_raw": 350,  # ADC reading (0-1023)
        "temperature": 24.5,       # Celsius
        "humidity": 55,            # % Relative humidity
        "light_level": "medium",   # Qualitative assessment
        "digital_threshold": False # Moisture threshold sensor (DO pin)
    },
    "timestamp": datetime.now().isoformat(),
    "arduino_id": "COM6",
    "firmware_version": "1.0.0"
}

def generate_local_report(plant_data: dict, ai_analysis: str = None):
    """Generate and save local plant health report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"aloe_vera_report_{timestamp}.txt"
    filepath = REPORTS_DIR / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("🌱 ALOE VERA PLANT HEALTH REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Plant Type: {plant_data['plant_type']}\n")
        f.write(f"Plant ID: {plant_data['plant_id']}\n")
        f.write(f"Location: {plant_data['location']}\n")
        f.write(f"Arduino Port: {plant_data['arduino_id']}\n\n")
        
        f.write("-" * 70 + "\n")
        f.write("📊 SENSOR READINGS\n")
        f.write("-" * 70 + "\n")
        sensor = plant_data['sensor_data']
        
        # Soil Moisture Analysis
        moisture = sensor['soil_moisture']
        f.write(f"\n💧 Soil Moisture: {moisture}%\n")
        if 60 <= moisture <= 70:
            f.write("   Status: ✓ OPTIMAL - Perfect for Aloe Vera\n")
        elif 50 <= moisture < 60:
            f.write("   Status: ⚠ SLIGHTLY DRY - Consider watering soon\n")
        elif moisture > 70:
            f.write("   Status: ⚠ TOO WET - Risk of root rot\n")
        else:
            f.write("   Status: ❌ CRITICAL - Water immediately\n")
        
        f.write(f"   Raw ADC Reading: {sensor['soil_moisture_raw']}/1023\n")
        f.write(f"   Digital Threshold: {'DRY' if sensor['digital_threshold'] else 'OK'}\n")
        
        # Temperature Analysis
        temp = sensor['temperature']
        f.write(f"\n🌡️ Temperature: {temp}°C\n")
        if 18 <= temp <= 27:
            f.write("   Status: ✓ IDEAL RANGE\n")
        elif 15 <= temp < 18 or 27 < temp <= 30:
            f.write("   Status: ⚠ ACCEPTABLE - Monitor closely\n")
        else:
            f.write("   Status: ❌ OUT OF RANGE - Take action\n")
        
        # Humidity Analysis
        humidity = sensor['humidity']
        f.write(f"\n💨 Humidity: {humidity}%\n")
        if 40 <= humidity <= 60:
            f.write("   Status: ✓ GOOD\n")
        elif humidity < 40:
            f.write("   Status: ⚠ LOW - Consider misting\n")
        else:
            f.write("   Status: ⚠ HIGH - Ensure ventilation\n")
        
        # Light Level
        f.write(f"\n☀️ Light Level: {sensor['light_level'].upper()}\n")
        
        # AI Analysis Section
        if ai_analysis:
            f.write("\n" + "-" * 70 + "\n")
            f.write("🤖 AI ANALYSIS (Sokosumi Agent)\n")
            f.write("-" * 70 + "\n")
            f.write(ai_analysis + "\n")
        
        # Recommendations
        f.write("\n" + "-" * 70 + "\n")
        f.write("💡 RECOMMENDATIONS\n")
        f.write("-" * 70 + "\n")
        
        recommendations = []
        if moisture < 60:
            recommendations.append("• Water the plant - soil is getting dry")
        elif moisture > 70:
            recommendations.append("• Reduce watering - soil is too wet")
        else:
            recommendations.append("• Continue current watering schedule")
        
        if temp < 18:
            recommendations.append("• Move to warmer location or provide heating")
        elif temp > 27:
            recommendations.append("• Provide shade or cooling during hot hours")
        
        if humidity < 40:
            recommendations.append("• Increase humidity with misting or humidifier")
        elif humidity > 60:
            recommendations.append("• Improve air circulation")
        
        for rec in recommendations:
            f.write(rec + "\n")
        
        # Aloe Vera Specific Care
        f.write("\n" + "-" * 70 + "\n")
        f.write("🌵 ALOE VERA CARE GUIDE\n")
        f.write("-" * 70 + "\n")
        f.write("• Watering: Once every 2-3 weeks (when soil is dry)\n")
        f.write("• Light: Bright, indirect sunlight (6-8 hours/day)\n")
        f.write("• Temperature: 18-27°C (ideal range)\n")
        f.write("• Soil: Well-draining succulent/cactus mix\n")
        f.write("• Humidity: 40-60% (tolerates dry air)\n")
        f.write("• Fertilizer: Monthly during growing season (spring/summer)\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("End of Report\n")
        f.write("=" * 70 + "\n")
    
    print(f"✅ Report saved: {filepath.absolute()}")
    return filepath

async def test_sokosumi_mock():
    """Test Sokosumi integration with mock plant data"""
    print("\n" + "=" * 70)
    print("🧪 TESTING SOKOSUMI PLANT HEALTH MONITORING (MOCK DATA)")
    print("=" * 70)
    
    print("\n📋 Mock Plant Data:")
    print(json.dumps(MOCK_PLANT_DATA, indent=2))
    
    # Generate local report first (works without Sokosumi)
    print("\n📝 Generating local report...")
    report_path = generate_local_report(MOCK_PLANT_DATA)
    
    # Try to connect to Sokosumi (may fail if API key issues)
    print("\n🔌 Attempting to connect to Sokosumi API...")
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {SOKOSUMI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Test basic connectivity
            response = await client.get(
                f"{SOKOSUMI_BASE_URL}/agents",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                print("✅ Sokosumi API connection successful!")
                agents = response.json()
                print(f"   Found {len(agents)} available agents")
                
                # TODO: Find plant health agent and create job
                print("\n⚠️ Plant health agent integration - Coming soon")
                print("   For now, using local analysis only")
            else:
                print(f"⚠️ Sokosumi API returned status {response.status_code}")
                print("   Using local analysis only")
                
    except Exception as e:
        print(f"⚠️ Could not connect to Sokosumi: {e}")
        print("   Using local analysis only")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
    print(f"\n📄 Report Location: {report_path.absolute()}")
    print("\n🎯 Next Steps:")
    print("   1. Review the generated report")
    print("   2. Wire soil moisture sensor to Arduino")
    print("   3. Upload enhanced Arduino sketch")
    print("   4. Test with real sensor data")

if __name__ == "__main__":
    print("\n🌱 Plant Health Monitoring - Mock Data Test")
    asyncio.run(test_sokosumi_mock())
