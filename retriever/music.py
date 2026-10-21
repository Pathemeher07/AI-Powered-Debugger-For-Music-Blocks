import streamlit as st
import numpy as np
from scipy.io import wavfile
import io
import uuid

# Define note frequencies (simple mapping for common notes)
NOTE_FREQS = {
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25
}

# Drum frequencies (low bass for kick, high for snare)
DRUM_FREQS = {'kick': 60.0, 'snare': 200.0}  # Hz for noise-like sounds

def note_to_freq(note):
    """Convert note name to frequency."""
    return NOTE_FREQS.get(note, 440.0)  # Default to A4

def generate_drum_audio(duration, sr, drum_type='kick'):
    """Generate simple drum sound (noise burst)."""
    t = np.linspace(0, duration, int(sr * duration), False)
    if drum_type == 'kick':
        # Low frequency sine with envelope
        freq = DRUM_FREQS['kick']
        audio = np.sin(2 * np.pi * freq * t) * np.exp(-t * 5)  # Decay
    else:  # snare
        # Noise
        audio = np.random.normal(0, 0.5, len(t)) * np.exp(-t * 3)
    return audio / np.max(np.abs(audio)) * 0.3

def generate_note_audio(duration, freq, sr):
    """Generate sine wave for a note with simple envelope."""
    t = np.linspace(0, duration, int(sr * duration), False)
    audio = 0.5 * np.sin(2 * np.pi * freq * t)
    # Soft envelope
    envelope = np.exp(-t * 2)  # Fade out
    audio *= envelope
    return audio / np.max(np.abs(audio))

def generate_audio(blocks, sample_rate=44100):
    """Generate WAV audio from sequence of blocks."""
    total_duration = sum(block.get('duration', 1.0) for block in blocks)
    if total_duration == 0:
        return None
    
    t_total = np.linspace(0, total_duration, int(sample_rate * total_duration), False)
    audio = np.zeros_like(t_total)
    
    start_time = 0
    for block in blocks:
        duration = block.get('duration', 1.0)
        end_time = start_time + duration
        block_idx_start = int(start_time * sample_rate)
        block_idx_end = int(end_time * sample_rate)
        
        block_t = t_total[block_idx_start:block_idx_end]
        
        if block['type'] == 'note' and 'note' in block:
            freq = note_to_freq(block['note'])
            block_audio = generate_note_audio(duration, freq, sample_rate)
        elif block['type'] == 'drum':
            drum_type = block.get('drum_type', 'kick')
            block_audio = generate_drum_audio(duration, sample_rate, drum_type)
        elif block['type'] == 'loop':
            # Simple loop: repeat a short pattern (e.g., C-D-E)
            sub_blocks = [{'type': 'note', 'note': 'C4', 'duration': 0.25},
                          {'type': 'note', 'note': 'D4', 'duration': 0.25},
                          {'type': 'note', 'note': 'E4', 'duration': 0.25},
                          {'type': 'note', 'note': 'G4', 'duration': 0.25}]
            sub_audio = generate_audio(sub_blocks * int(duration), sample_rate)
            if sub_audio is not None:
                sub_len = len(sub_audio)
                repeats = int(duration * sample_rate / sub_len)
                block_audio = np.tile(sub_audio[:sub_len], repeats)[:len(block_t)]
            else:
                block_audio = np.zeros(len(block_t))
        elif block['type'] == 'effect':
            # Placeholder: volume effect (multiply previous by factor)
            effect_factor = block.get('volume', 0.5)
            # For simplicity, apply to whole (future: chain effects)
            continue  # Skip for now, or apply globally later
        
        if 'block_audio' in locals():
            audio[block_idx_start:block_idx_end] += block_audio[:len(block_t)]
        
        start_time = end_time
    
    # Normalize
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))
    
    # Write to BytesIO buffer as WAV
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, (audio * 32767).astype(np.int16))
    buffer.seek(0)
    return buffer

def main():
    st.set_page_config(page_title="Advanced Music Blocks", layout="wide")
    st.title("🎵 Advanced Music Blocks with Streamlit")
    st.markdown("Add blocks from the sidebar to compose a sequence. Hit *Play* to hear your music! Blocks play in order.")

    # Initialize session state
    if 'blocks' not in st.session_state:
        st.session_state.blocks = []
    if 'next_id' not in st.session_state:
        st.session_state.next_id = 0

    # Sidebar: Toolbox
    with st.sidebar:
        st.header("🛠 Toolbox")
        st.markdown("Click to add blocks:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎹 C4 Note (1s)"):
                st.session_state.blocks.append({
                    'id': st.session_state.next_id,
                    'type': 'note',
                    'note': 'C4',
                    'duration': 1.0
                })
                st.session_state.next_id += 1
                st.rerun()
            
            if st.button("🥁 Kick Drum (0.5s)"):
                st.session_state.blocks.append({
                    'id': st.session_state.next_id,
                    'type': 'drum',
                    'drum_type': 'kick',
                    'duration': 0.5
                })
                st.session_state.next_id += 1
                st.rerun()
            
            if st.button("🔄 1s Loop"):
                st.session_state.blocks.append({
                    'id': st.session_state.next_id,
                    'type': 'loop',
                    'duration': 1.0
                })
                st.session_state.next_id += 1
                st.rerun()
        
        with col2:
            if st.button("🎹 D4 Note (0.5s)"):
                st.session_state.blocks.append({
                    'id': st.session_state.next_id,
                    'type': 'note',
                    'note': 'D4',
                    'duration': 0.5
                })
                st.session_state.next_id += 1
                st.rerun()
            
            if st.button("🥁 Snare Drum (0.25s)"):
                st.session_state.blocks.append({
                    'id': st.session_state.next_id,
                    'type': 'drum',
                    'drum_type': 'snare',
                    'duration': 0.25
                })
                st.session_state.next_id += 1
                st.rerun()
            
            if st.button("🔉 Volume Effect (0.5)"):
                st.session_state.blocks.append({
                    'id': st.session_state.next_id,
                    'type': 'effect',
                    'volume': 0.5,
                    'duration': 1.0  # Applies over next block(s)
                })
                st.session_state.next_id += 1
                st.rerun()
        
        st.markdown("---")
        if st.button("🗑 Clear All"):
            st.session_state.blocks = []
            st.session_state.next_id = 0
            st.rerun()

    # Main area: Display and manage blocks
    if not st.session_state.blocks:
        st.info("Add some blocks from the sidebar to get started! 🎼")
    else:
        st.subheader(f"📝 Your Composition ({len(st.session_state.blocks)} blocks)")
        
        for i, block in enumerate(st.session_state.blocks):
            with st.container():
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                
                with col1:
                    if block['type'] == 'note':
                        st.write(f"{block['type'].upper()}: {block['note']} ({block['duration']}s)")
                    elif block['type'] == 'drum':
                        st.write(f"{block['type'].upper()}: {block.get('drum_type', 'kick')} ({block['duration']}s)")
                    elif block['type'] == 'loop':
                        st.write(f"{block['type'].upper()}: {block['duration']}s pattern")
                    else:
                        st.write(f"{block['type'].upper()}: Volume {block.get('volume', 1.0)}")
                
                with col2:
                    if st.button("⬆", key=f"up_{i}"):
                        if i > 0:
                            st.session_state.blocks[i-1], st.session_state.blocks[i] = st.session_state.blocks[i], st.session_state.blocks[i-1]
                            st.rerun()
                
                with col3:
                    if st.button("⬇", key=f"down_{i}"):
                        if i < len(st.session_state.blocks) - 1:
                            st.session_state.blocks[i+1], st.session_state.blocks[i] = st.session_state.blocks[i], st.session_state.blocks[i+1]
                            st.rerun()
                
                with col4:
                    if st.button("🗑", key=f"del_{i}"):
                        del st.session_state.blocks[i]
                        st.rerun()
        
        st.markdown("---")
        
        # Controls
        col_play, col_export = st.columns(2)
        with col_play:
            if st.button("▶ Play Composition", use_container_width=True):
                with st.spinner("Generating audio..."):
                    audio_buffer = generate_audio(st.session_state.blocks)
                    if audio_buffer:
                        st.audio(audio_buffer, format='audio/wav')
                    else:
                        st.error("No audio generated. Add some notes or drums!")
        
        with col_export:
            if st.button("💾 Export as MIDI (Download)", use_container_width=True):
                # Simple MIDI export using midiutil
                from midiutil import MIDIFile
                
                midi = MIDIFile(1)  # One track
                track = 0
                channel = 0
                time = 0
                tempo = 120  # BPM
                midi.addTempo(track, time, tempo)
                
                for block in st.session_state.blocks:
                    duration = block.get('duration', 1.0)
                    if block['type'] == 'note' and 'note' in block:
                        note_num = {'C4': 60, 'D4': 62, 'E4': 64, 'F4': 65, 'G4': 67, 'A4': 69, 'B4': 71, 'C5': 72, 'D5': 74, 'E5': 76}.get(block['note'], 69)
                        midi.addNote(track, channel, note_num, time, duration, 100)
                        time += duration
                    elif block['type'] == 'drum':
                        # Drums on channel 10
                        drum_note = {'kick': 36, 'snare': 38}.get(block.get('drum_type', 'kick'), 36)
                        midi.addNote(track, 9, drum_note, time, duration, 100)  # Channel 10 for drums
                        time += duration
                    # Skip others for MIDI simplicity
                
                buffer = io.BytesIO()
                midi.writeFile(buffer)
                buffer.seek(0)
                
                b64 = base64.b64encode(buffer.read()).decode()
                href = f'<a href="data:audio/midi;base64,{b64}" download="musicblocks.mid">Download MIDI</a>'
                st.markdown(href, unsafe_allow_html=True)

if _name_ == "_main_":
    main()