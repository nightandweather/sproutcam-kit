#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include "esp_camera.h"
#include "camera_pins.h"
#include "secrets.h"

constexpr uint8_t PIN_LOW_WATER = D0;
constexpr uint8_t PIN_PUMP = D1;
constexpr uint8_t PIN_LIGHT = D2;
constexpr unsigned long PUMP_MAX_RUN_MS = 30000;
constexpr unsigned long PUMP_DAILY_LIMIT_MS = 300000;
constexpr unsigned long DAY_MS = 86400000;

WebServer server(80);
unsigned long pumpStartedAt = 0;
unsigned long pumpRequestedMs = 0;
unsigned long pumpUsedToday = 0;
unsigned long dayStartedAt = 0;
bool pumpRunning = false;
bool sensorReady = false;

bool readSHT40(float &temperature, float &humidity) {
  Wire.beginTransmission(0x44); Wire.write(0xFD);
  if (Wire.endTransmission() != 0) return false;
  delay(10);
  if (Wire.requestFrom(0x44, 6) != 6) return false;
  uint16_t rawT=(Wire.read()<<8)|Wire.read(); Wire.read();
  uint16_t rawH=(Wire.read()<<8)|Wire.read(); Wire.read();
  temperature=-45.0f+175.0f*(rawT/65535.0f);
  humidity=-6.0f+125.0f*(rawH/65535.0f);
  humidity=constrain(humidity,0.0f,100.0f);
  return true;
}

const char DASHBOARD[] PROGMEM = R"HTML(
<!doctype html><html lang="ko"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{font-family:system-ui;background:#f3f2ea;color:#111;margin:0}.wrap{max-width:520px;margin:auto;padding:24px}h1{font-size:38px;margin:12px 0}.card{background:white;border:1px solid #111;border-radius:18px;padding:18px;margin:14px 0;box-shadow:5px 5px #111}img{width:100%;border-radius:12px;background:#ddd}button{background:#b7ff22;border:1px solid #111;border-radius:999px;padding:13px 18px;font-weight:800;margin-right:8px}.danger{background:#ff6138}.muted{color:#666;font-size:13px}</style>
<div class="wrap"><div class="muted">SPROUTCAM ONE / LOCAL</div><h1>오늘도 자라는 중.</h1>
<div class="card"><img id="photo" src="/photo.jpg"><p><button onclick="snap()">새로 촬영</button></p></div>
<div class="card"><h2>환경</h2><div id="status">읽는 중...</div></div>
<div class="card"><h2>수동 제어</h2><button onclick="pump(3)">펌프 3초</button><button class="danger" onclick="pump(0)">정지</button><p class="muted">저수위에서는 펌프가 켜지지 않습니다.</p></div></div>
<script>
async function refresh(){let r=await fetch('/api/status');let s=await r.json();status.innerHTML=`온도 <b>${s.temperature_c}°C</b><br>습도 <b>${s.humidity_pct}%</b><br>수위 <b>${s.low_water?'부족':'정상'}</b><br>펌프 <b>${s.pump?'작동':'정지'}</b>`}
function snap(){photo.src='/photo.jpg?t='+Date.now()}
async function pump(sec){await fetch('/api/pump?seconds='+sec,{method:'POST'});refresh()}
refresh();setInterval(refresh,5000);
</script></html>)HTML";

bool lowWater() { return digitalRead(PIN_LOW_WATER) == HIGH; }

void stopPump() {
  if (pumpRunning) {
    unsigned long elapsed = millis() - pumpStartedAt;
    pumpUsedToday += min(elapsed, PUMP_MAX_RUN_MS);
  }
  digitalWrite(PIN_PUMP, LOW);
  pumpRunning = false;
}

bool startPump(unsigned long durationMs) {
  if (lowWater() || pumpRunning || pumpUsedToday >= PUMP_DAILY_LIMIT_MS) return false;
  durationMs = min(durationMs, PUMP_MAX_RUN_MS);
  pumpStartedAt = millis();
  pumpRequestedMs = durationMs;
  pumpRunning = true;
  digitalWrite(PIN_PUMP, HIGH);
  return true;
}

void initCamera() {
  camera_config_t c{};
  c.ledc_channel = LEDC_CHANNEL_0; c.ledc_timer = LEDC_TIMER_0;
  c.pin_d0=Y2_GPIO_NUM; c.pin_d1=Y3_GPIO_NUM; c.pin_d2=Y4_GPIO_NUM; c.pin_d3=Y5_GPIO_NUM;
  c.pin_d4=Y6_GPIO_NUM; c.pin_d5=Y7_GPIO_NUM; c.pin_d6=Y8_GPIO_NUM; c.pin_d7=Y9_GPIO_NUM;
  c.pin_xclk=XCLK_GPIO_NUM; c.pin_pclk=PCLK_GPIO_NUM; c.pin_vsync=VSYNC_GPIO_NUM;
  c.pin_href=HREF_GPIO_NUM; c.pin_sccb_sda=SIOD_GPIO_NUM; c.pin_sccb_scl=SIOC_GPIO_NUM;
  c.pin_pwdn=PWDN_GPIO_NUM; c.pin_reset=RESET_GPIO_NUM; c.xclk_freq_hz=20000000;
  c.pixel_format=PIXFORMAT_JPEG; c.frame_size=FRAMESIZE_SXGA; c.jpeg_quality=12; c.fb_count=2;
  c.grab_mode=CAMERA_GRAB_LATEST; c.fb_location=CAMERA_FB_IN_PSRAM;
  if (esp_camera_init(&c) != ESP_OK) Serial.println("camera init failed");
}

void handleStatus() {
  float temperature = NAN, humidity = NAN;
  sensorReady=readSHT40(temperature,humidity);
  String json = "{\"temperature_c\":" + String(temperature,1) +
    ",\"humidity_pct\":" + String(humidity,1) +
    ",\"low_water\":" + String(lowWater()?"true":"false") +
    ",\"pump\":" + String(pumpRunning?"true":"false") +
    ",\"pump_daily_ms\":" + String(pumpUsedToday) + "}";
  server.send(200,"application/json",json);
}

void handlePhoto() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) { server.send(503,"text/plain","camera unavailable"); return; }
  server.setContentLength(fb->len);
  server.send(200,"image/jpeg","");
  WiFiClient client=server.client(); client.write(fb->buf,fb->len);
  esp_camera_fb_return(fb);
}

void handlePump() {
  int seconds = constrain(server.arg("seconds").toInt(),0,30);
  if (seconds == 0) { stopPump(); server.send(200,"application/json","{\"ok\":true}"); return; }
  bool ok=startPump(seconds*1000UL);
  server.send(ok?200:409,"application/json",ok?"{\"ok\":true}":"{\"ok\":false,\"reason\":\"low-water-or-limit\"}");
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LOW_WATER,INPUT_PULLUP); pinMode(PIN_PUMP,OUTPUT); pinMode(PIN_LIGHT,OUTPUT);
  stopPump(); digitalWrite(PIN_LIGHT,HIGH);
  Wire.begin(); initCamera();
  WiFi.begin(WIFI_SSID,WIFI_PASSWORD);
  for (int i=0;i<60 && WiFi.status()!=WL_CONNECTED;i++){delay(500);Serial.print('.');}
  Serial.printf("\nDashboard: http://%s/\n",WiFi.localIP().toString().c_str());
  server.on("/",[](){server.send_P(200,"text/html",DASHBOARD);});
  server.on("/api/status",HTTP_GET,handleStatus);
  server.on("/photo.jpg",HTTP_GET,handlePhoto);
  server.on("/api/pump",HTTP_POST,handlePump);
  server.begin(); dayStartedAt=millis();
}

void loop() {
  server.handleClient();
  unsigned long now=millis();
  if (pumpRunning && (lowWater() || now-pumpStartedAt>=pumpRequestedMs)) stopPump();
  if (now-dayStartedAt>=DAY_MS){pumpUsedToday=0;dayStartedAt=now;}
  delay(2);
}
