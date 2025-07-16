# 💡 Mini RGB Controller

Controlador leve e personalizável de LEDs RGB via porta serial (Adalight), feito em Python com interface gráfica (Tkinter) e integração com a bandeja do sistema.

---

## 🎯 Funcionalidades

- 🎨 Troca de efeitos em tempo real (ex: arco-íris, respiração, cores aleatórias)
- 🎛️ Controle de velocidade e cor base (HSV)
- 🪟 Interface gráfica com suporte a minimização na bandeja
- 🔌 Comunicação serial com placas como ESP32, Arduino ou ESP8266 com firmware Adalight
- 🧠 Leve e sem console (`.pyw`) – ideal para rodar em segundo plano

---

## 🧰 Requisitos

- Python 3.10+ instalado
- Bibliotecas:

```bash
pip install pyserial numpy pillow pystray
