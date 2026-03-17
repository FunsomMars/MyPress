#!/bin/bash
# 获取南京市浦口区天气

LOCATION="Nanjing,Pukou"
TIMEZONE="Asia/Shanghai"

# 使用 wttr.in 获取天气（更稳定）
echo "🌤️ 南京市浦口区天气 - $(date '+%Y年%m月%d日 %H:%M')" 
echo "======================================"
curl -s "https://wttr.in/$LOCATION?format=j1" | python3 << 'PYTHON_SCRIPT'
import json, sys
data = json.load(sys.stdin)
current = data['current_condition'][0]
weather = data['weather'][0]

print(f"🌡️  温度: {current['temp_C']}°C (体感 {current['FeelsLikeC']}°C)")
print(f"☀️  天气: {current['weatherDesc'][0]['value']}")
print(f"💧 湿度: {current['humidity']}%")
print(f"💨 风速: {current['windspeedKmph']} km/h {current['winddir16Point']}")
print(f"📊 气压: {current['pressure']} hPa")
print()
print("📅 今日预报")
print(f"🔺 最高: {weather['maxtempC']}°C")
print(f"🔻 最低: {weather['mintempC']}°C")
print(f"🌅 日出: {weather['astronomy'][0]['sunrise']}")
print(f"🌇 日落: {weather['astronomy'][0]['sunset']}")

# 明日预报
tomorrow = data['weather'][1] if len(data['weather']) > 1 else None
if tomorrow:
    print()
    print("📅 明日预报")
    print(f"天气: {tomorrow['hourly'][7]['lang_zh'][0]['value'] if tomorrow['hourly'][7].get('lang_zh') else '未知'}")
    print(f"🔺 最高: {tomorrow['maxtempC']}°C")
    print(f"🔻 最低: {tomorrow['mintempC']}°C")
PYTHON_SCRIPT
