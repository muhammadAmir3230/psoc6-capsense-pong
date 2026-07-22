# 🏓 PSoC 6 CapSense Pong

> Classic Nokia-style Pong — but the controller is a **touch slider on a PSoC 6 microcontroller**. Two boards, two players, zero joysticks.

![Platform](https://img.shields.io/badge/platform-PSoC%206-blue)
![Board](https://img.shields.io/badge/board-CY8CPROTO--062--4343W-orange)
![ModusToolbox](https://img.shields.io/badge/ModusToolbox-3.5-green)
![Python](https://img.shields.io/badge/python-3.x-yellow)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 🎮 What is this?

We turned Infineon's **CY8CPROTO-062-4343W** prototyping kit into a game
controller. Slide your finger along the CapSense touch strip and your
paddle follows in real time — the board's LED even glows brighter as your
paddle climbs. Plug in a **second board** and it's head-to-head Pong,
old-Nokia-LCD style.

```
 Player 1 finger ──> CapSense slider ──> UART "P42" ──> COM6 ──┐
                                                               ├──> pygame 🏓
 Player 2 finger ──> CapSense slider ──> UART "P73" ──> COM7 ──┘
```

**The trick:** both boards run *identical firmware*. They're told apart
purely by COM port — flash once, plug in twice, play.

## ✨ Features

- 🖐️ **True analog touch control** — 0–100 position from a 5-segment CapSense slider, not just buttons
- 👥 **1 or 2 players** — second paddle is an AI if you're alone, a friend if you're not
- 💡 **LED feedback** — board LED brightness mirrors your paddle position
- 🛟 **Graceful fallback** — cable pops out? That player drops to keyboard, the game never crashes
- 📟 **Nokia LCD aesthetic** — that green. You know the one.
- ⚡ **Rally speedup** — ball gets 5% faster on every paddle hit; edge hits deflect sharper

## 🔧 Hardware

| Item | Qty | Notes |
|---|---|---|
| CY8CPROTO-062-4343W | 1–2 | PSoC 6 Wi-Fi BT Prototyping Kit |
| USB-A → Micro-B cable | 1–2 | Must be a **data** cable |
| Laptop (Windows) | 1 | Runs the game |

## 🚀 Quick start

### 1. Flash the firmware (once per board)

Open the `CAPSENSE_Buttons_and_Slider` project in **Eclipse IDE for
ModusToolbox** (tools 3.5), let the Library Manager fetch dependencies
(`make getlibs`), then **Build** and **Program**.

The firmware change over the stock Infineon example is a single line —
we stream the slider position over UART:

```c
printf("P%lu\r\n", led_data.brightness);   /* 0–100 paddle position */
```

### 2. Run the game

```bash
pip install pygame pyserial

python pong.py COM6 COM7   # two boards = two players
python pong.py COM6        # one board vs AI
python pong.py             # no board? keyboard test (W/S vs arrows)
```

Find your COM ports in **Device Manager → Ports → KitProg3 USB-UART**.

> ⚠️ Close any serial terminal (Tera Term / Eclipse Serial Terminal)
> before launching — only one program can hold a COM port.

### 3. Play

| Input | Action |
|---|---|
| Finger on slider | Move paddle |
| `Esc` | Quit |
| First to lose | Buys the kuih 🍡 |

## 🗺️ Roadmap

- [ ] CapSense buttons as start/pause
- [ ] Bounce & score sound effects
- [ ] 📡 **Wireless mode** — positions over Wi-Fi UDP instead of USB (the 4343W has Wi-Fi begging to be used)
- [ ] LED blink on every paddle hit (PC → board feedback channel)

## 🧠 What we learned

- ModusToolbox toolchains **hate spaces in paths** (ask us how we know)
- `CY_TOOLS_PATHS` and `CY_COMPILER_GCC_ARM_DIR` environment variables
- CapSense widget processing, centroid position, and scan/process loops
- UART retarget-io, serial protocols, and COM port etiquette
- Threading a serial reader alongside a 60 FPS pygame loop

## 👥 Team

| | |
|---|---|
| [@muhammadAmir3230](https://github.com/muhammadAmir3230) | firmware, setup survival, board wrangling |
| [@thoughtdenham2005](https://github.com/thoughtdenham2005) | co-developer |

Built on Infineon's `mtb-example-psoc6-capsense-buttons-slider` code example.

## 📄 License

MIT — see [LICENSE](LICENSE). Game on.

