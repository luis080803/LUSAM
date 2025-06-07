#include "esp_camera.h"
#include <WiFi.h>
#include <WiFiUdp.h>

// ===========================
// Configuración WiFi y UDP
// ===========================
const char *ssid = "ESP32-CAM-AP";
const char *password = "12345678";
const unsigned int udpPort = 5000;

const int MotPin0 = 12;
const int MotPin1 = 13;
const int MotPin2 = 14;
const int MotPin3 = 15;

// Pines sensor ultrasónico
const int TRIG_PIN = 2;
const int ECHO_PIN = 4;

WiFiUDP udp;
IPAddress remoteIp;         // Última IP que envió comando
bool ipRemotaDetectada = false;

void startCameraServer();
void setupLedFlash(int pin);

long leerDistanciaCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duracion = pulseIn(ECHO_PIN, HIGH, 25000);
  long distancia = duracion * 0.034 / 2;
  return distancia;
}

void setup() {
  pinMode(MotPin0, OUTPUT);
  pinMode(MotPin1, OUTPUT);
  pinMode(MotPin2, OUTPUT);
  pinMode(MotPin3, OUTPUT);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // Config cámara
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sccb_sda = 26;
  config.pin_sccb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  if (config.pixel_format == PIXFORMAT_JPEG && psramFound()) {
    config.jpeg_quality = 10;
    config.fb_count = 2;
    config.grab_mode = CAMERA_GRAB_LATEST;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camara inicio con error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_SVGA);
  }

  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.println("Access Point iniciado");
  Serial.print("IP: ");
  Serial.println(IP);

  udp.begin(udpPort);
  Serial.printf("Servidor UDP iniciado en el puerto %d\n", udpPort);

  startCameraServer();
  Serial.println("Cámara Inicializada");
}

unsigned long tiempoAnterior = 0;

void loop() {
  // Enviar distancia cada segundo, solo si se conoce la IP remota
  if (millis() - tiempoAnterior > 1000) {
    tiempoAnterior = millis();
    long distancia = leerDistanciaCM();

    Serial.print("Distancia: ");
    Serial.print(distancia);
    Serial.println(" cm");

    if (ipRemotaDetectada) {
      char mensaje[50];
      snprintf(mensaje, sizeof(mensaje), "Distancia: %ld cm", distancia);
      udp.beginPacket(remoteIp, udpPort);  // puerto destino = puerto desde el cual se recibió
      udp.write((const uint8_t *)mensaje, strlen(mensaje));
      udp.endPacket();
    }
  }

  // Procesar comandos UDP
  int packetSize = udp.parsePacket();
  if (packetSize) {
    char packetBuffer[255];
    int len = udp.read(packetBuffer, sizeof(packetBuffer) - 1);
    if (len > 0) {
      packetBuffer[len] = '\0';

      // 📌 Guardar IP del remitente
      remoteIp = udp.remoteIP();
      ipRemotaDetectada = true;

      char command = packetBuffer[0];
      switch (command) {
        case 'W':
          digitalWrite(MotPin0, LOW);
          digitalWrite(MotPin1, HIGH);
          digitalWrite(MotPin2, HIGH);
          digitalWrite(MotPin3, LOW);
          delay(100);
          break;
        case 'S':
          digitalWrite(MotPin0, HIGH);
          digitalWrite(MotPin1, LOW);
          digitalWrite(MotPin2, LOW);
          digitalWrite(MotPin3, HIGH);
          delay(100);
          break;
        case 'A':
          digitalWrite(MotPin0, LOW);
          digitalWrite(MotPin1, HIGH);
          digitalWrite(MotPin2, LOW);
          digitalWrite(MotPin3, HIGH);
          delay(100);
          break;
        case 'D':
          digitalWrite(MotPin0, HIGH);
          digitalWrite(MotPin1, LOW);
          digitalWrite(MotPin2, HIGH);
          digitalWrite(MotPin3, LOW);
          delay(100);
          break;
        case 'R':
          digitalWrite(MotPin0, LOW);
          digitalWrite(MotPin1, LOW);
          digitalWrite(MotPin2, LOW);
          digitalWrite(MotPin3, LOW);
          break;
        default:
          Serial.println("Comando no reconocido");
      }

      // Apagar motores después del movimiento
      digitalWrite(MotPin0, LOW);
      digitalWrite(MotPin1, LOW);
      digitalWrite(MotPin2, LOW);
      digitalWrite(MotPin3, LOW);
    }
  }

  delay(10);
}
