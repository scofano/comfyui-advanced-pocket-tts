"""
ComfyUI-Pocket-TTS - Text-to-Speech nodes using Kyutai's Pocket TTS
"""

import torch
import numpy as np

print("\n" + "="*70)
print("🎙️ ComfyUI-Pocket-TTS - Loading...")
print("="*70)

# Import pocket_tts
try:
    from pocket_tts import TTSModel
    POCKET_TTS_AVAILABLE = True
    print("✅ Pocket TTS library imported successfully")
except ImportError as e:
    POCKET_TTS_AVAILABLE = False
    print(f"❌ [Pocket-TTS] Import Error: {e}")
    TTSModel = None

# Global cache
_MODEL_CACHE = {}

# Built-in voices
VOICES = ["alba", "marius", "javert", "jean", "fantine", "cosette", "eponine", "azelma"]

# Pocket-TTS v2 language models.
# Portuguese support requires a recent pocket-tts package version.
LANGUAGES = [
    "english",
    "english_2026-01",
    "english_2026-04",
    "italian",
    "italian_24l",
    "german",
    "german_24l",
    "spanish",
    "spanish_24l",
    "portuguese",
    "portuguese_24l",
    "french_24l",
]


def load_model(language="english", temp=0.7, lsd_decode_steps=1, eos_threshold=-4.0, quantize=False):
    """Load Pocket-TTS model with caching per unique parameter combination."""
    global _MODEL_CACHE

    cache_key = f"pocket_tts::{language}::temp={temp}::steps={lsd_decode_steps}::eos={eos_threshold}::q={quantize}"
    if cache_key in _MODEL_CACHE:
        return _MODEL_CACHE[cache_key]

    print(f"🔄 Loading Pocket TTS model: {language} (temp={temp}, steps={lsd_decode_steps}, eos={eos_threshold}, quantize={quantize})")
    model = TTSModel.load_model(
        language=language,
        temp=temp,
        lsd_decode_steps=lsd_decode_steps,
        eos_threshold=eos_threshold,
        quantize=quantize,
    )
    print("✅ Model loaded!")

    _MODEL_CACHE[cache_key] = model
    return model


class PocketTTSGenerate:
    """Generate speech with built-in voices"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "default": "Hello world, this is a test.",
                    "multiline": True
                }),
                "voice": (VOICES, {"default": "alba"}),
                "language": (LANGUAGES, {"default": "english"}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.05,
                                          "tooltip": "Controls expressiveness/randomness. Lower = stable, higher = varied."}),
                "lsd_decode_steps": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1,
                                             "tooltip": "Decode steps per audio chunk. More steps = higher quality but slower."}),
                "eos_threshold": ("FLOAT", {"default": -4.0, "min": -10.0, "max": 0.0, "step": 0.1,
                                            "tooltip": "End-of-speech threshold. Lower = ends sooner; raise if audio gets cut off."}),
                "frames_after_eos": ("INT", {"default": 0, "min": 0, "max": 200, "step": 1,
                                             "tooltip": "Extra frames after speech ends (~80ms each). 0 = let model decide."}),
                "quantize": ("BOOLEAN", {"default": False,
                                         "tooltip": "Use int8 quantization for lower memory usage and faster inference."}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate"
    CATEGORY = "audio/Pocket-TTS"

    def generate(self, text, voice, language, temperature, lsd_decode_steps, eos_threshold, frames_after_eos, quantize):
        if not POCKET_TTS_AVAILABLE:
            raise RuntimeError("pocket-tts not installed")

        if not text:
            raise RuntimeError("Text is required")

        model = load_model(language, temp=temperature, lsd_decode_steps=lsd_decode_steps,
                           eos_threshold=eos_threshold, quantize=quantize)

        print(f"🎤 Using voice: {voice} | language: {language}")
        voice_state = model.get_state_for_audio_prompt(voice)

        fae = frames_after_eos if frames_after_eos > 0 else None
        print(f"🎙️ Generating: {len(text)} chars")
        with torch.inference_mode(False):
            audio = model.generate_audio(voice_state, text, frames_after_eos=fae)

        waveform = audio.unsqueeze(0).unsqueeze(0)

        return ({"waveform": waveform, "sample_rate": model.sample_rate},)


class PocketTTSClone:
    """Clone voice from reference audio"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ref_audio": ("AUDIO",),
                "target_text": ("STRING", {
                    "default": "Hello world, this is a test.",
                    "multiline": True
                }),
                "language": (LANGUAGES, {"default": "english"}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.05,
                                          "tooltip": "Controls expressiveness/randomness. Lower = stable, higher = varied."}),
                "lsd_decode_steps": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1,
                                             "tooltip": "Decode steps per audio chunk. More steps = higher quality but slower."}),
                "eos_threshold": ("FLOAT", {"default": -4.0, "min": -10.0, "max": 0.0, "step": 0.1,
                                            "tooltip": "End-of-speech threshold. Lower = ends sooner; raise if audio gets cut off."}),
                "frames_after_eos": ("INT", {"default": 0, "min": 0, "max": 200, "step": 1,
                                             "tooltip": "Extra frames after speech ends (~80ms each). 0 = let model decide."}),
                "quantize": ("BOOLEAN", {"default": False,
                                         "tooltip": "Use int8 quantization for lower memory usage and faster inference."}),
                "truncate": ("BOOLEAN", {"default": True,
                                         "tooltip": "Truncate reference audio to 30 seconds before voice conditioning."}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate"
    CATEGORY = "audio/Pocket-TTS"

    def audio_tensor_to_numpy(self, audio_tensor):
        """Convert ComfyUI audio to numpy"""
        waveform = None
        sr = None

        # Handle dict format
        if isinstance(audio_tensor, dict):
            if "waveform" in audio_tensor:
                waveform = audio_tensor.get("waveform")
                sr = audio_tensor.get("sample_rate") or audio_tensor.get("sr")
            elif "data" in audio_tensor:
                waveform = audio_tensor.get("data")
                sr = audio_tensor.get("sampling_rate")

        # Convert to numpy
        if waveform is not None:
            if isinstance(waveform, torch.Tensor):
                waveform = waveform.cpu().numpy()

            # Remove all extra dimensions
            while waveform.ndim > 1:
                if waveform.shape[0] == 1:
                    waveform = waveform.squeeze(0)
                elif waveform.shape[-1] == 1:
                    waveform = waveform.squeeze(-1)
                else:
                    # Multi-channel - average to mono
                    waveform = np.mean(waveform, axis=0 if waveform.shape[0] <= 2 else -1)

            waveform = waveform.astype(np.float32)

        if waveform is None or sr is None or waveform.size == 0:
            raise RuntimeError("Failed to parse reference audio")

        return waveform, int(sr)

    def generate(self, ref_audio, target_text, language, temperature, lsd_decode_steps, eos_threshold, frames_after_eos, quantize, truncate):
        if not POCKET_TTS_AVAILABLE:
            raise RuntimeError("pocket-tts not installed")

        if not target_text:
            raise RuntimeError("Text is required")

        model = load_model(language, temp=temperature, lsd_decode_steps=lsd_decode_steps,
                           eos_threshold=eos_threshold, quantize=quantize)

        wav_np, sr = self.audio_tensor_to_numpy(ref_audio)

        print(f"📊 Audio shape: {wav_np.shape}, dtype: {wav_np.dtype}, sr: {sr}")

        if wav_np.ndim != 1:
            raise RuntimeError(f"Audio must be 1D, got shape {wav_np.shape}")

        if wav_np.size < 100:
            raise RuntimeError(f"Audio too short: {wav_np.size} samples")

        import tempfile
        import os
        from scipy.io import wavfile

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            wav_int16 = (wav_np * 32767).astype(np.int16)
            wavfile.write(tmp_path, sr, wav_int16)

            print(f"🎤 Cloning voice | language: {language} | truncate: {truncate}")
            voice_state = model.get_state_for_audio_prompt(tmp_path, truncate=truncate)

            fae = frames_after_eos if frames_after_eos > 0 else None
            with torch.inference_mode(False):
                audio = model.generate_audio(voice_state, target_text, frames_after_eos=fae)

            waveform = audio.unsqueeze(0).unsqueeze(0)

            return ({"waveform": waveform, "sample_rate": model.sample_rate},)

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# Register nodes
NODE_CLASS_MAPPINGS = {
    "PocketTTSGenerate": PocketTTSGenerate,
    "PocketTTSClone": PocketTTSClone,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PocketTTSGenerate": "🎙️ Advanced Pocket TTS Generate",
    "PocketTTSClone": "🎙️ Advanced Pocket TTS Clone Voice",
}

print("="*70)
print("✅ Pocket TTS nodes registered")
print("="*70 + "\n")
