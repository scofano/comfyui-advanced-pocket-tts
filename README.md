# Advanced Pocket TTS 🎙️

**Lightweight CPU-based Text-to-Speech for ComfyUI — with full parameter control**

Fast, efficient TTS running at **6x real-time on CPU** without GPU requirements. Exposes all generation parameters for fine-grained control over quality, speed, and voice behavior.

> Forked from [ai-joe-git/ComfyUI-Pocket-TTS](https://github.com/ai-joe-git/ComfyUI-Pocket-TTS) and extended with advanced generation parameters.

---

## ✨ Features

- 🚀 **Fast**: ~200ms latency, 6x real-time on CPU
- 💻 **CPU Only**: No GPU needed (works on laptops!)
- 🎯 **Small Model**: Only 100M parameters
- 🎭 **8 Built-in Voices**: Ready to use
- 🔊 **Voice Cloning**: Use any audio input
- 📝 **Long Text**: Handles infinitely long inputs
- ⚡ **Low Memory**: Uses only 2 CPU cores
- 🔧 **Advanced Parameters**: Full control over temperature, decode steps, EOS threshold, quantization, and more

---

## 📦 Installation

### Method 1: ComfyUI Manager (Recommended)

1. Open ComfyUI Manager
2. Search for "Advanced Pocket TTS"
3. Click Install
4. Restart ComfyUI

### Method 2: Manual Install

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/scofano/ComfyUI-Pocket-TTS-V2
cd ComfyUI-Pocket-TTS-V2
pip install -r requirements.txt
```

---

## 🎮 Nodes

### 1. 🎙️ Advanced Pocket TTS Generate
**Generate speech with built-in voices and full parameter control**
- 8 voices: alba, marius, javert, jean, fantine, cosette, eponine, azelma
- 13 language models (English, Portuguese, Spanish, French, Italian, German)
- Full control over generation parameters

### 2. 🎙️ Advanced Pocket TTS Clone Voice
**Clone voice from any reference audio**
- Connect any AUDIO node as reference
- Optional 30s truncation of reference audio
- Same generation parameters as the Generate node

---

## 🎭 Built-in Voices

| Voice | Description |
|-------|-------------|
| **alba** | Alba Mackenna (default) |
| **marius** | Marius Pontmercy |
| **javert** | Inspector Javert |
| **jean** | Jean Valjean |
| **fantine** | Fantine |
| **cosette** | Cosette |
| **eponine** | Eponine |
| **azelma** | Azelma |

---

## 🌍 Language Models

| Model | Notes |
|-------|-------|
| `english` | Default (alias for `english_2026-04`) |
| `english_2026-01` | Earlier English model |
| `english_2026-04` | Latest English model |
| `portuguese_24l` | Larger, higher quality |
| `spanish_24l` | Larger, higher quality |
| `french_24l` | Larger, higher quality |
| `italian_24l` | Larger, higher quality |
| `german_24l` | Larger, higher quality |
| `portuguese` / `spanish` / `italian` / `german` | Smaller, faster variants |

`*_24l` models are larger and may produce better results but are slower to run.

---

## 🔧 Generation Parameters

Both nodes expose the following parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| **temperature** | `0.7` | Controls expressiveness. Lower = stable/neutral, higher = varied/expressive. Range: 0.0–2.0 |
| **lsd_decode_steps** | `1` | Decode steps per audio chunk. More steps = higher quality, slower generation. Range: 1–10 |
| **eos_threshold** | `-4.0` | End-of-speech sensitivity. Lower ends sooner; raise if audio gets cut off. Range: -10.0–0.0 |
| **frames_after_eos** | `0` | Extra silence frames after speech ends (~80ms each). `0` = let the model decide. Range: 0–200 |
| **quantize** | `False` | Use int8 quantization for lower memory usage and faster inference |

**Clone Voice only:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| **truncate** | `False` | Truncate reference audio to 30 seconds before voice conditioning |

> All defaults match the Pocket TTS library defaults, so existing workflows produce identical results without any changes.

---

## 🔧 Usage Examples

### Basic Generation

```
text:     "Hello world, this is a test."
voice:    alba
language: english
→ Audio Output
```

### Higher Quality (slower)

```
lsd_decode_steps: 4
temperature:      0.7
```

### More Expressive Voice

```
temperature: 1.2
```

### Audio Gets Cut Off?

```
eos_threshold:   -2.0   (raise toward 0)
frames_after_eos: 10    (add ~800ms of padding)
```

### Lower Memory / Faster

```
quantize: True
```

### Voice Cloning

1. Connect a reference audio to the **Clone Voice** node
2. Enter target text
3. Enable `truncate` if the reference is longer than 30 seconds

---

## ⚡ Performance

Tested on MacBook Air M4:

| Metric | Value |
|--------|-------|
| **Latency** | ~200ms first chunk |
| **Speed** | 6x real-time |
| **CPU Cores** | 2 cores |
| **Model Size** | 100M params |
| **Memory** | ~400MB RAM |

---

## 🔄 Workflow Integration

Works with:
- ✅ **Video Helper Suite** — Save audio
- ✅ **Audio Processing Nodes** — Effects/mixing
- ✅ **Batch Processing** — Multiple voices
- ✅ **Animation Workflows** — Lip sync

---

## 🐛 Troubleshooting

### ❌ "No module named 'pocket_tts'"

```bash
# In ComfyUI venv:
pip install pocket-tts
```

### ⚠️ Audio gets cut off

Raise `eos_threshold` (e.g. from `-4.0` to `-2.0`) or add `frames_after_eos` padding.

### ⚠️ Slow generation

- Keep `lsd_decode_steps` at `1` (default)
- Enable `quantize` to reduce memory pressure
- Close other applications

---

## 📚 Credits

- **Pocket TTS**: [Kyutai Labs](https://github.com/kyutai-labs/pocket-tts)
- **Original ComfyUI Node**: [ai-joe-git/ComfyUI-Pocket-TTS](https://github.com/ai-joe-git/ComfyUI-Pocket-TTS)
- **Advanced Parameters Fork**: scofano

---

## 📝 License

MIT License

---

## 🚀 Changelog

### v1.0.3
- Renamed to **Advanced Pocket TTS**
- Added `temperature`, `lsd_decode_steps`, `eos_threshold`, `frames_after_eos`, `quantize` parameters to both nodes
- Added `truncate` parameter to Clone Voice node
- Smart model caching by full parameter combination
- Tooltips on all new parameters

### v1.0.2
- Added Portuguese, Spanish, Italian, German language support
- Model caching per language

### v1.0.1
- Voice cloning support

### v1.0.0
- Initial release (forked from ai-joe-git/ComfyUI-Pocket-TTS)

---

## ⚠️ Prohibited Use

Voice cloning requires **explicit consent**. Do not use for:
- ❌ Voice impersonation without consent
- ❌ Misinformation/fake news
- ❌ Harassment or hate speech
- ❌ Privacy violations

See [Pocket TTS license](https://github.com/kyutai-labs/pocket-tts) for full terms.

---

**Made with ❤️ for the ComfyUI community**
