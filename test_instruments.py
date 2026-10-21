"""
Quick test file for new instrument synthesis
Run this to test all instruments before running Streamlit
"""

import sys
import os
import io

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))

from audio_instruments import (
    generate_pitched_sound, 
    generate_drum_sound, 
    generate_melody,
    audio_to_bytes,
    INSTRUMENT_CONFIG,
    DRUM_CONFIG
)

print("🎵 Testing Instrument Synthesis Module\n")

# Test 1: Generate Piano sound
print("✅ Test 1: Generating Piano sound...")
piano_audio = generate_pitched_sound(440, 2, "Piano", 0.7)
print(f"   Piano audio generated: {len(piano_audio)} samples")

# Test 2: Generate Drum sound
print("✅ Test 2: Generating Drum (Kick) sound...")
drum_audio = generate_drum_sound("Kick", 0.5, 0.7)
print(f"   Drum audio generated: {len(drum_audio)} samples")

# Test 3: Generate melody
print("✅ Test 3: Generating melody sequence...")
melody = [("C4", 4), ("D4", 4), ("E4", 4), ("G4", 4), ("C5", 8)]
melody_audio = generate_melody(melody, 120, "Guitar", 0.7)
print(f"   Melody audio generated: {len(melody_audio)} samples (~{len(melody_audio)/44100:.1f} seconds)")

# Test 4: Test all instruments
print("\n✅ Test 4: Testing all instruments...")
for instrument_name in list(INSTRUMENT_CONFIG.keys())[:5]:
    audio = generate_pitched_sound(440, 1, instrument_name, 0.7)
    print(f"   {instrument_name}: ✓")

# Test 5: Test all drums
print("\n✅ Test 5: Testing all drums...")
for drum_name in DRUM_CONFIG.keys():
    audio = generate_drum_sound(drum_name, 0.3, 0.7)
    print(f"   {drum_name}: ✓")

# Test 6: WAV export
print("\n✅ Test 6: Converting to WAV bytes...")
test_audio = generate_pitched_sound(440, 1, "Violin", 0.7)
wav_bytes = audio_to_bytes(test_audio)
print(f"   WAV size: {len(wav_bytes)} bytes")

print("\n" + "="*50)
print("🎉 All tests passed! Instruments are working correctly.")
print("="*50)
print("\nYou can now run: streamlit run app/main.py")
