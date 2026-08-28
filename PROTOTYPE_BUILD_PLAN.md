# Assam Flood Alert System — Prototype Build Plan
**Timeline:** Aug 29 → Sep 8, 2026 (11 days)
**Goal:** A working, demoable 3-node sensor mesh feeding a laptop dashboard that issues Green/Yellow/Orange/Red flood alerts, with an optional AI-classifier layer as a stretch feature.

---

## Priority tiers — read this first

If you run out of time, cut from the bottom up. Never cut from P0.

- **P0 (must work for any demo to make sense):** 3 hardware nodes reading water level, data reaching your laptop, rule-based Green/Yellow/Orange/Red logic, a visible dashboard/output.
- **P1 (makes it a strong SIH demo):** multi-node "sensor agreement" logic, simulated rainfall input feeding the risk score, node-failure resilience shown live.
- **P2 (stretch, only if P0+P1 are solid with days to spare):** the QLoRA-trained AI classifier running alongside the rule engine, ESP-NOW true mesh instead of WiFi star topology.

Build P0 completely before touching P1. Don't start P2 until P0 and P1 both work end-to-end at least once.

---

## Day 1 — Aug 29 (Sat): Setup & scope lock

- [ ] Confirm you have all hardware in hand: 3× ESP8266, 3× HC-SR04, 3× 18650 (protected or with TP4056+protection module), 3× boost/regulator modules
- [ ] Install Arduino IDE or PlatformIO, add ESP8266 board support
- [ ] Flash one ESP8266 with a basic "blink" sketch to confirm toolchain works
- [ ] Fix your Python environment for the laptop-side code (the `requirements.txt` issues from earlier — confirm `uv pip install -r requirements.txt` succeeds)
- [ ] Write down your exact demo narrative in one paragraph (what will you show, in what order, in how many minutes) — this shapes every decision below

**End-of-day check:** Toolchains work. You know exactly what you're demoing.

---

## Day 2 — Aug 30 (Sun): Single node, hardware bring-up

- [ ] Wire ONE full node: 18650 → protection/charging module → boost/regulator → ESP8266 → HC-SR04
- [ ] Write firmware to read HC-SR04 distance and print it over Serial every ~1s
- [ ] Convert raw distance reading into a "water level" value (distance from sensor to water surface → subtract from known container height)
- [ ] Test with a cup/tank of water on your desk — confirm readings change sensibly as you add/remove water
- [ ] Repeat wiring for node 2 and node 3 (same firmware, different device)

**End-of-day check:** All 3 nodes independently print sensible water-level readings over Serial.

**Watch out for:** boost module current rating under WiFi TX bursts (from earlier — undersized boost = random resets); battery polarity; HC-SR04 needs a stable, flat surface to "see" the water surface.

---

## Day 3 — Aug 31 (Mon): Get data off the nodes

- [ ] Add WiFi connectivity to each node's firmware (connect to your phone hotspot or a router)
- [ ] Pick ONE transport and commit to it for the demo: simplest is each node doing an HTTP POST to your laptop, or all 3 publishing to a lightweight MQTT broker running on your laptop (e.g. Mosquitto)
- [ ] Write a minimal Python receiver script on your laptop that logs incoming readings from all 3 nodes with a timestamp and node ID
- [ ] Test all 3 nodes simultaneously — confirm your laptop is receiving from all three, distinguishable by node ID

**End-of-day check:** Your laptop terminal shows a live, tagged stream of readings from all 3 nodes at once.

---

## Day 4 — Sep 1 (Tue): Rule-based risk logic (your guaranteed-to-work core)

- [ ] Implement the Green/Yellow/Orange/Red threshold logic in Python, based on:
  - current water level
  - rate of rise (compare current reading to reading from ~30–60s ago per node)
- [ ] Implement the "sensor agreement" rule: don't alert on a single node's spike — require 2+ nodes agreeing before escalating past Yellow
- [ ] Add a simulated rainfall input (a slider, config value, or command-line flag) that feeds into the risk score alongside water level, per your Risk = f(...) formula
- [ ] Print the current alert level clearly to console, updating live as readings come in

**End-of-day check:** You can manually raise water in 2 of 3 cups and watch the system escalate from Green → Yellow → Orange/Red in real time, driven by real sensor data.

This is your P0 finish line. Everything past this point is enhancement.

---

## Day 5 — Sep 2 (Wed): Dashboard / visual output

- [ ] Build a simple visual layer — a local web dashboard (Flask/FastAPI + a basic HTML page with auto-refresh, or a simple desktop GUI) showing:
  - each node's live water level and connection status
  - the current overall alert level, large and color-coded
  - a log of recent alert-level changes
- [ ] Keep this simple — judges care about clarity, not polish. A clean single page beats a complex one.

**End-of-day check:** Someone unfamiliar with the project can glance at your laptop screen and immediately understand the current flood risk state.

---

## Day 6 — Sep 3 (Thu): Resilience + node-failure demo (P1)

- [ ] Test unplugging/powering off one node mid-run — confirm the system keeps functioning on 2/3 nodes and clearly shows the missing node as offline (not just silently ignoring it)
- [ ] Test what happens if only 1 node spikes (should NOT trigger a high alert — this proves your "agreement" logic isn't naive)
- [ ] Calibrate your Yellow/Orange/Red thresholds against realistic values for your cup/tank setup so the demo escalates convincingly within a reasonable time (not too fast, not too slow)
- [ ] Write down the exact sequence of actions you'll perform live during the demo (pour water into cup 1, wait, pour into cup 2, etc.)

**End-of-day check:** You can run the full demo sequence start to finish, including a simulated node failure, without touching code.

---

## Day 7 — Sep 4 (Fri): AI classifier layer (P2 — only if P0/P1 solid)

- [ ] If you have a full day of buffer left, proceed with the QLoRA training pipeline (data generation → training → ONNX export) from your existing scripts
- [ ] If you're behind schedule, **skip this entirely** — the rule-based system alone is a complete, defensible prototype
- [ ] If you proceed: get it training in the background on your GPU machine while you keep working on other tasks — don't block the rest of the plan waiting on training to finish

**End-of-day check:** Either the AI layer is training/working, or you've made a clear decision to leave it out and are not losing time to it.

---

## Day 8 — Sep 5 (Sat): Integration + AI wiring (if applicable)

- [ ] If Day 7's training succeeded: wire the ONNX classifier into your dashboard as a second, side-by-side prediction next to the rule-based alert
- [ ] Full end-to-end run: hardware → WiFi/MQTT → laptop → rule logic (+ AI if included) → dashboard
- [ ] Time the full demo sequence — know exactly how long it takes

**End-of-day check:** One clean, complete run of the entire system, timed.

---

## Day 9 — Sep 6 (Sun): Buffer + bug fixing

- [ ] This day has no new features. Only fix what broke.
- [ ] Prepare a fallback: a short pre-recorded video or a "replay" mode with logged sensor data, in case live hardware fails during judging (WiFi congestion at a venue is common — don't let that sink your demo)
- [ ] Charge all batteries fully; test runtime under continuous operation to confirm they'll last through judging

**End-of-day check:** You have a working live demo AND a working fallback if the live one fails.

---

## Day 10 — Sep 7 (Mon): Pitch & presentation

- [ ] Build your slides/pitch around the ASSAM_FLOOD_PITCH.md content you already have — problem, hotspots, root causes, your system as the intervention
- [ ] Prepare honest answers for likely judge questions:
  - "Why AI/LLM for a 6-number classification?" → be upfront it's a pipeline demonstration, not an accuracy necessity
  - "How does this scale to real rivers?" → talk through solar power, ruggedized enclosures, ESP-NOW mesh as the production path
  - "What happens if a sensor fails?" → point to your Day 6 resilience demo
- [ ] Rehearse the full demo + pitch at least twice, timed

**End-of-day check:** You can run the pitch + demo in your allotted time without hesitation.

---

## Day 11 — Sep 8 (Tue): Demo day

- [ ] Morning: full system test at the venue (WiFi environment will differ from home — test early)
- [ ] Charge everything, pack spare batteries, pack the fallback video/replay on a laptop that doesn't depend on venue WiFi
- [ ] Present

---

## Quick reference — components confirmed in earlier planning

| Component | Choice |
|---|---|
| Microcontroller | ESP8266 |
| Water level sensor | HC-SR04 (ultrasonic) |
| Battery | 2000mAh 18650, rechargeable, with protection |
| Power regulation | Boost module (18650 → 5V for board VIN), rated ≥500mA-1A |
| Charging | TP4056 module with protection IC |
| Node count | 3 (to demonstrate mesh/agreement logic) |
| Compute | Laptop (Python receiver + risk logic + dashboard) |
| Networking (recommended for timeline) | WiFi → HTTP/MQTT star topology to laptop |
| Networking (stretch) | ESP-NOW peer-to-peer mesh |
| AI layer (stretch) | Qwen2.5-1.5B-Instruct, QLoRA fine-tuned, ONNX-exported |
