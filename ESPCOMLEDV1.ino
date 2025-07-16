#include <FastLED.h>

#define NUM_LEDS 20            // Número total de LEDs na fita
#define DATA_PIN 16             // GPIO onde a fita está conectada
#define LED_TYPE WS2812B       // Tipo da fita
#define COLOR_ORDER GRB        // Ordem das cores (mude pra RGB se necessário)

CRGB leds[NUM_LEDS];

// Buffer para receber os dados
uint8_t prefix[] = {'A', 'd', 'a'};
uint8_t buf[NUM_LEDS * 3];

void setup() {
  Serial.begin(115200);
  FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  FastLED.clear();
  FastLED.show();
}

void loop() {
  static uint8_t state = 0;
  static uint8_t prefix_pos = 0;
  static int bytesRead = 0;

  while (Serial.available()) {
    uint8_t c = Serial.read();

    switch (state) {
      case 0:  // Esperando prefixo "Ada"
        if (c == prefix[prefix_pos]) {
          prefix_pos++;
          if (prefix_pos == 3) {
            state = 1;
            prefix_pos = 0;
          }
        } else {
          prefix_pos = 0;
        }
        break;

      case 1: state = 2; break;  // Hi byte (ignorado)
      case 2: state = 3; break;  // Lo byte (ignorado)
      case 3: state = 4; bytesRead = 0; break; // Checksum (ignorado)

      case 4:
        buf[bytesRead++] = c;
        if (bytesRead >= NUM_LEDS * 3) {
          for (int i = 0; i < NUM_LEDS; i++) {
            leds[i].g = buf[i * 3];       // GRB
            leds[i].r = buf[i * 3 + 1];
            leds[i].b = buf[i * 3 + 2];
          }
          FastLED.show();
          state = 0;
        }
        break;
    }
  }
}
