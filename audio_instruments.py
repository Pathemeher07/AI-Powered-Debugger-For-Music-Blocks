"""
Advanced Instrument Synthesis Module
Generates realistic audio for all Music Blocks instruments
"""

import numpy as np
from scipy import signal
from io import BytesIO
import wave

SAMPLE_RATE = 44100

# Instrument frequency characteristics
INSTRUMENT_CONFIG = {
    "Piano": {"base_freq": 440, "harmonics": [1, 2, 3, 4, 5], "decay": 0.3, "attack": 0.01},
    "Drum": {"base_freq": 80, "harmonics": [1], "decay": 0.1, "attack": 0.001},
    "Trumpet": {"base_freq": 440, "harmonics": [1, 2, 3, 4, 5], "decay": 0.2, "attack": 0.05},
    "Guitar": {"base_freq": 440, "harmonics": [1, 2, 3, 4], "decay": 0.5, "attack": 0.02},
    "Violin": {"base_freq": 440, "harmonics": [1, 2, 3, 4, 5, 6], "decay": 0.4, "attack": 0.1},
    "Saxophone": {"base_freq": 440, "harmonics": [1, 3, 5, 7], "decay": 0.25, "attack": 0.08},
    "Trombone": {"base_freq": 440, "harmonics": [1, 2, 3, 4], "decay": 0.3, "attack": 0.05},
    "Bass Guitar": {"base_freq": 220, "harmonics": [1, 2, 3], "decay": 0.6, "attack": 0.03},
    "Bells": {"base_freq": 440, "harmonics": [1, 2.1, 3.2, 4.5], "decay": 0.8, "attack": 0.01},
    "Banjo": {"base_freq": 440, "harmonics": [1, 2, 3, 4], "decay": 0.15, "attack": 0.005},
    "Voice": {"base_freq": 440, "harmonics": [1, 2, 3, 4, 5, 6], "decay": 0.35, "attack": 0.1},
    "French Horn": {"base_freq": 440, "harmonics": [1, 2, 3, 4, 5], "decay": 0.4, "attack": 0.08},
    "Electric Guitar": {"base_freq": 440, "harmonics": [1, 2, 3], "decay": 0.4, "attack": 0.01},
    "Bugle": {"base_freq": 440, "harmonics": [1, 2, 3, 4], "decay": 0.2, "attack": 0.05},
}

# Drum configurations
DRUM_CONFIG = {
    "Kick": {"freq": 60, "decay": 0.15, "attack": 0.001, "freq_end": 40},
    "Snare": {"freq": 200, "decay": 0.08, "attack": 0.001, "noise_mix": 0.7},
    "Hi-hat": {"freq": 8000, "decay": 0.05, "attack": 0.001, "noise_mix": 0.9},
    "Tom": {"freq": 300, "decay": 0.1, "attack": 0.002, "freq_end": 200},
    "Crash": {"freq": 6000, "decay": 0.4, "attack": 0.002, "noise_mix": 0.8},
}

def note_to_freq(note_str):
    """Convert note string (e.g., 'C4', 'D#5') to frequency in Hz"""
    notes = {
        'C': -9, 'C#': -8, 'D': -7, 'D#': -6,
        'E': -5, 'F': -4, 'F#': -3, 'G': -2,
        'G#': -1, 'A': 0, 'A#': 1, 'B': 2
    }
    
    try:
        # Parse note and octave
        note_name = note_str[:-1].upper()
        octave = int(note_str[-1])
        
        if note_name not in notes:
            return 440  # Default to A4
        
        semitones_from_a4 = notes[note_name] + (octave - 4) * 12
        freq = 440 * (2 ** (semitones_from_a4 / 12))
        return freq
    except:
        return 440

def envelope(duration, attack, decay, sample_rate):
    """Generate ADSR envelope"""
    attack_samples = int(attack * sample_rate)
    decay_samples = int((duration - attack - decay) * sample_rate)
    release_samples = int(decay * sample_rate)
    
    env = np.concatenate([
        np.linspace(0, 1, max(1, attack_samples)),
        np.linspace(1, 0.7, max(1, decay_samples)),
        np.linspace(0.7, 0, max(1, release_samples))
    ])
    
    # Pad or trim to exact duration
    target_length = int(duration * sample_rate)
    if len(env) < target_length:
        env = np.concatenate([env, np.zeros(target_length - len(env))])
    else:
        env = env[:target_length]
    
    return env

def generate_pitched_sound(frequency, duration, instrument="Piano", volume=0.7):
    """Generate realistic pitched instrument sound"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    config = INSTRUMENT_CONFIG.get(instrument, INSTRUMENT_CONFIG["Piano"])
    attack = config.get("attack", 0.01)
    decay = config.get("decay", 0.3)
    harmonics = config.get("harmonics", [1])
    
    # Generate fundamental + harmonics
    wave_data = np.zeros_like(t)
    for i, harmonic in enumerate(harmonics):
        harmonic_freq = frequency * harmonic
        # Reduce amplitude of higher harmonics
        harmonic_amp = 1.0 / (i + 1)
        wave_data += harmonic_amp * np.sin(2 * np.pi * harmonic_freq * t)
    
    # Normalize
    wave_data = wave_data / len(harmonics)
    
    # Apply envelope
    env = envelope(duration, attack, decay, SAMPLE_RATE)
    wave_data = wave_data * env * volume
    
    return wave_data.astype(np.float32)

def generate_drum_sound(drum_type, duration, volume=0.7):
    """Generate realistic drum sound"""
    config = DRUM_CONFIG.get(drum_type, DRUM_CONFIG["Kick"])
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    attack = config.get("attack", 0.001)
    decay = config.get("decay", 0.1)
    freq_start = config.get("freq", 100)
    freq_end = config.get("freq_end", freq_start)
    noise_mix = config.get("noise_mix", 0.0)
    
    # Generate pitch envelope (frequency slides down for kick)
    if freq_end != freq_start:
        # Frequency sweep
        freq_envelope = np.linspace(freq_start, freq_end, len(t))
        phase = 2 * np.pi * np.cumsum(freq_envelope) / SAMPLE_RATE
        wave_data = np.sin(phase)
    else:
        # Fixed frequency
        wave_data = np.sin(2 * np.pi * freq_start * t)
    
    # Mix in noise for hi-hat, snare
    if noise_mix > 0:
        noise = np.random.normal(0, 1, len(t))
        # High-pass filter for hi-hat/snare
        b, a = signal.butter(2, 0.5, 'high')
        noise = signal.filtfilt(b, a, noise)
        wave_data = (1 - noise_mix) * wave_data + noise_mix * noise
    
    # Apply envelope
    env = envelope(duration, attack, decay, SAMPLE_RATE)
    wave_data = wave_data * env * volume
    
    return wave_data.astype(np.float32)

def generate_melody(notes_list, bpm, instrument="Piano", volume=0.7):
    """
    Generate complete melody from note list
    notes_list: [(note_str, duration_beats), ...]
    Example: [('C4', 4), ('D4', 4), ('E4', 4)]
    """
    beat_duration = 60 / bpm
    total_audio = np.array([], dtype=np.float32)
    
    for note_str, duration_beats in notes_list:
        if note_str.lower() == "rest":
            # Rest/silence
            silence = np.zeros(int(beat_duration * duration_beats * SAMPLE_RATE), dtype=np.float32)
            total_audio = np.concatenate([total_audio, silence])
        elif note_str in DRUM_CONFIG:
            # Drum sound
            duration_sec = beat_duration * duration_beats
            drum_audio = generate_drum_sound(note_str, duration_sec, volume)
            total_audio = np.concatenate([total_audio, drum_audio])
        else:
            # Pitched sound
            frequency = note_to_freq(note_str)
            duration_sec = beat_duration * duration_beats
            pitched_audio = generate_pitched_sound(frequency, duration_sec, instrument, volume)
            total_audio = np.concatenate([total_audio, pitched_audio])
    
    return total_audio

def audio_to_bytes(audio, sample_rate=SAMPLE_RATE):
    """Convert numpy audio array to WAV bytes"""
    # Convert float32 to int16
    audio_int16 = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
    
    buffer = BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())
    
    buffer.seek(0)
    return buffer.getvalue()
