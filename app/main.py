import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from JSONParser.json_parser import convert_music_blocks
from audio_instruments import generate_pitched_sound, generate_drum_sound, generate_melody, audio_to_bytes, note_to_freq, DRUM_CONFIG, INSTRUMENT_CONFIG
import json
import streamlit as st
from retriever.retrieve import retrieve_relevant_chunks
from llm.openai import generate_response
from llm.gemini import ask_gemini
from datetime import datetime
import threading
import uvicorn
import numpy as np
from scipy import signal
from io import BytesIO
import wave
import qdrant_client
import pyperclip

# Music Blocks Instruments List
MUSIC_BLOCKS_INSTRUMENTS = {
    "🎹 Piano": "Piano",
    "🥁 Drum": "Drum",
    "🎺 Trumpet": "Trumpet",
    "🎸 Guitar": "Guitar",
    "🎻 Violin": "Violin",
    "🎷 Saxophone": "Saxophone",
    "🎺 Trombone": "Trombone",
    "🎸 Bass Guitar": "Bass Guitar",
    "🔔 Bells": "Bells",
    "🪕 Banjo": "Banjo",
    "🎙️ Voice": "Voice",
    "🎺 French Horn": "French Horn",
    "🎸 Electric Guitar": "Electric Guitar",
    "📯 Bugle": "Bugle",
    "⛔ Stop": "Stop",
}

# Audio Generation Function (Legacy - kept for compatibility)
def generate_simple_tone(frequency, duration, volume=0.7, sample_rate=44100):
    """Generate a simple sine wave tone (LEGACY - use generate_pitched_sound instead)"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    wave = volume * np.sin(2 * np.pi * frequency * t)
    return wave.astype(np.float32)

def note_to_frequency(note):
    """Convert note name to frequency (Hz)"""
    return note_to_freq(note)

def generate_music_audio(duration=30, bpm=120, note_freq=440, volume=70, instrument="Piano"):
    """Generate music audio from Music Blocks parameters using realistic instruments"""
    sample_rate = 44100
    total_duration = (duration / 4) * (60 / bpm) if duration > 0 else (60 / bpm)
    
    # Check if it's a drum
    if instrument == "Drum" or isinstance(note_freq, str) and note_freq in DRUM_CONFIG:
        audio = generate_drum_sound(note_freq if isinstance(note_freq, str) else "Kick", total_duration, volume/100)
    else:
        # Generate pitched instrument sound with realistic synthesis
        audio = generate_pitched_sound(note_freq, total_duration, instrument, volume/100)
    
    return audio, sample_rate

def save_audio_to_bytes(audio, sample_rate):
    """Convert audio array to WAV bytes"""
    return audio_to_bytes(audio, sample_rate)

import socket

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False

def run_fastapi():
    try:
        uvicorn.run("app.api:app", host="0.0.0.0", port=8000, log_level="warning")
    except Exception:
        pass

if not is_port_in_use(8000):
    threading.Thread(target=run_fastapi, daemon=True).start()

st.set_page_config(page_title="🎵 Music Blocks Debugger")

st.title("🎵 Music Blocks Debugger")

# Initialize session state FIRST before using it
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "project_code" not in st.session_state:
    st.session_state.project_code = ""
if "user_prompt_count" not in st.session_state:
    st.session_state.user_prompt_count = 0
if "selected_instrument" not in st.session_state:
    st.session_state.selected_instrument = "Piano"
if "code_valid" not in st.session_state:
    st.session_state.code_valid = False
if "raw_code" not in st.session_state:
    st.session_state.raw_code = ""

# Instrument Selection at the Top
col1, col2 = st.columns([3, 1])
with col1:
    st.session_state.selected_instrument = st.selectbox(
        "🎼 Choose an instrument to work with:",
        options=list(MUSIC_BLOCKS_INSTRUMENTS.keys()),
        index=list(MUSIC_BLOCKS_INSTRUMENTS.keys()).index("🎹 Piano"),
        help="Select the instrument you want to use in your Music Blocks project"
    )
with col2:
    st.info(f"**{st.session_state.selected_instrument}**")

st.divider()

# Play Music Button at Top - Initially Hidden
if st.session_state.code_valid and st.session_state.project_code:
    st.markdown("### 🎵 Music Playback")
    col_play1, col_play2, col_play3 = st.columns(3)
    
    # Volume control at top
    volume_top = st.slider("🔊 Volume", 0, 100, 70, key="volume_slider_top")
    
    with col_play1:
        if st.button("▶️ Play Music", key="play_btn_top", help="Play the processed Music Blocks project"):
            try:
                note_freq = note_to_frequency("C4")
                audio, sample_rate = generate_music_audio(duration=30, bpm=120, note_freq=note_freq, volume=volume_top, instrument=st.session_state.selected_instrument)
                audio_bytes = save_audio_to_bytes(audio, sample_rate)
                
                st.success("🎵 Music is playing!")
                st.audio(audio_bytes, format="audio/wav")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col_play2:
        if st.button("⏸️ Pause", key="pause_btn_top", help="Pause the music"):
            st.info("⏸️ Music paused (Note: Streamlit doesn't support live pause)")
    
    with col_play3:
        if st.button("🔄 Restart", key="restart_btn_top", help="Restart from the beginning"):
            try:
                note_freq = note_to_frequency("C4")
                audio, sample_rate = generate_music_audio(duration=30, bpm=120, note_freq=note_freq, volume=volume_top, instrument=st.session_state.selected_instrument)
                audio_bytes = save_audio_to_bytes(audio, sample_rate)
                
                st.info("🔄 Restarting music...")
                st.audio(audio_bytes, format="audio/wav")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display current instrument playing
    st.markdown(f"**🎺 Currently Playing:** {st.session_state.selected_instrument} | **Volume:** {volume_top}%")
    
    st.divider()

SYSTEM_INSTRUCTION = (
     """You are Music Blocks Bot, a friendly and playful assistant that helps kids debug their Music Blocks projects. Follow these rules:

        1. **Personality**: Be like a patient music teacher who makes learning fun! Use emojis 🎵✨ sometimes to keep it lively.

        2. **Language**:
            - Use simple words (max 2 syllables when possible)
            - Short sentences (max 10 words)
            - Examples: "Oh no! Your drums are too quiet 🥁 Let's turn them up!" or "Wow! That's a cool melody! 🎶"

        3. **Interactivity**:
            - Always ask questions to keep kids engaged
            - Offer choices: "Want to try fixing the drums first or the piano?"
            - Give high-fives for good work: "You fixed it! 🙌"

        4. **Debugging Help**:
            - Explain problems like stories: "The sleepy trumpet 🎺 isn't waking up because..."
            - Show don't tell - use simple comparisons: "Your loop is like a hamster wheel that never stops!"

        5. **Avoid**:
            - Long paragraphs
            - Technical words without explaining
            - Negative language (say "Let's try again!" not "You're wrong")

        6. **When stuck**:
            - Offer to "ask a grownup" if too hard
            - Suggest taking a music break and coming back

        First respond to the user by introducing yourself excitedly and asking about their Music Blocks project in a fun way! 🎼"""
)

with st.expander("🎒 Drop Your Music Blocks Project Here!", expanded=not st.session_state.project_code):
    code = st.text_area("🎼 Paste your magical music code below ✨", height=300, value=st.session_state.raw_code, key="code_input")
    st.session_state.raw_code = code
    
    st.markdown(f"**📍 Selected Instrument:** {st.session_state.selected_instrument}")
    
    # Code validation and error display
    if code.strip():
        st.markdown("### 🔍 Code Validation")
        col_val1, col_val2 = st.columns(2)
        
        # Check if it's valid JSON
        try:
            json_data = json.loads(code.strip())
            with col_val1:
                st.success("✅ Valid JSON Format")
            with col_val2:
                st.success("✅ Ready to Process")
            json_valid = True
        except json.JSONDecodeError as e:
            with col_val1:
                st.error(f"❌ JSON Error")
                # Display error details like VS Code
                with st.container(border=True):
                    st.markdown("**📍 Error Details:**")
                    error_msg = f"Line {e.lineno}, Column {e.colno}\n**Error:** {e.msg}"
                    st.markdown(error_msg)
                    # Show problematic line if available
                    lines = code.split('\n')
                    if e.lineno <= len(lines):
                        st.code(f">>> {lines[e.lineno-1]}", language="json")
            with col_val2:
                st.warning("⚠️ Fix errors above")
            json_valid = False
    else:
        json_valid = False
    
    if st.button("🚀 Launch My Music Blocks Project!"):
        if code.strip():
            try:
                json_data = json.loads(code.strip())
                try:
                    converted_text = "\n".join(convert_music_blocks(json_data))
                    st.session_state.project_code = converted_text
                    st.session_state.code_valid = True
                    st.success("✅ Project code saved !!")

                    with st.spinner("🎼 The Debugger is tuning its ears..."):
                        try:
                            context_chunks = retrieve_relevant_chunks(st.session_state.project_code)

                            intro_prompt = (
                                SYSTEM_INSTRUCTION + "\n\n"
                                + f"The user has selected the **{st.session_state.selected_instrument}** instrument to work with.\n\n"
                                + "You are being given a Music Blocks project code. Your task is to analyze this code and try to understand what the student is trying to build — is it a melody, a rhythm, a loop-based song, an instrument experiment, a math-based music pattern, etc.?\n\n"
                                + "Here is the full Music Blocks project code:\n"
                                + st.session_state.project_code + "\n\n"
                                + "Helpful parts from documentation or examples:\n"
                                + "\n".join(context_chunks) + "\n\n"
                                + "Now make your best guess: Start your message like this —\n"
                                + "\"It appears to me that your project is about...\" 🎶\n"
                                + "Then ask: \"Did I get that right? What else do you want to tell me about your project before we begin debugging?\"\n\n"
                                + "Keep your answer lively, musical, and kid-friendly. Use emojis where helpful. Keep sentences short and clear."
                            )

                            gemini_intro_reply = ask_gemini(intro_prompt)

                            st.session_state.chat_history.append({
                                "role": "gemini",
                                "content": gemini_intro_reply
                            })

                        except Exception as e:
                            st.warning(f"⚠️ Gemini API: {str(e)}")
                except Exception as convert_error:
                    st.error(f"❌ Error converting code: {str(convert_error)}")
                    st.info("ℹ️ Make sure your Music Blocks JSON is properly formatted")
                    st.session_state.code_valid = False
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON format")
                with st.container(border=True):
                    st.markdown(f"**Error at Line {e.lineno}, Column {e.colno}:**")
                    st.markdown(f"**Message:** {e.msg}")
                st.session_state.code_valid = False
        else:
            st.warning("Please enter a valid Music Blocks project code.")
# Play Music Section Below Code Block - Shows after successful code execution
if st.session_state.code_valid and st.session_state.project_code:
    st.divider()
    st.markdown("### 🎵 Play Your Music Below")
    col_play1, col_play2, col_play3, col_play4 = st.columns(4)
    
    # Get volume from slider
    volume = st.slider("🔊 Volume", 0, 100, 70, key="volume_slider_below")
    
    with col_play1:
        if st.button("▶️ Play", key="play_btn_below", help="Play the processed Music Blocks project"):
            try:
                # Generate realistic instrument sound
                note_freq = note_to_frequency("C4")  # Middle C
                audio, sample_rate = generate_music_audio(duration=30, bpm=120, note_freq=note_freq, volume=volume, instrument=st.session_state.selected_instrument)
                audio_bytes = save_audio_to_bytes(audio, sample_rate)
                
                st.success("🎵 Music is playing!")
                st.audio(audio_bytes, format="audio/wav")
                st.balloons()
            except Exception as e:
                st.error(f"Error generating audio: {str(e)}")
    
    with col_play2:
        if st.button("⏸️ Pause", key="pause_btn_below", help="Pause the music"):
            st.info("⏸️ Music paused (Note: Streamlit doesn't support live pause - refresh to stop)")
    
    with col_play3:
        if st.button("⏹️ Stop", key="stop_btn_below", help="Stop the music"):
            st.info("⏹️ Music stopped - Click Play again to replay")
    
    with col_play4:
        if st.button("🔄 Replay", key="replay_btn_below", help="Replay from the beginning"):
            try:
                note_freq = note_to_frequency("C4")
                audio, sample_rate = generate_music_audio(duration=30, bpm=120, note_freq=note_freq, volume=volume, instrument=st.session_state.selected_instrument)
                audio_bytes = save_audio_to_bytes(audio, sample_rate)
                
                st.info("🔄 Replaying music...")
                st.audio(audio_bytes, format="audio/wav")
            except Exception as e:
                st.error(f"Error generating audio: {str(e)}")
    
    st.markdown(f"**🔊 Volume:** {volume}% | **Instrument:** {st.session_state.selected_instrument}")
    
    st.divider()
if st.session_state.project_code:
    st.subheader("🎼 Curious Notes? Let’s Debug Together!")

    user_input = st.chat_input("🎹 Got a music mystery to solve?")

    if user_input:
        st.session_state.user_prompt_count += 1
        with st.spinner("🎼 The Debugger is tuning its ears..."):
            try:
                context_chunks = retrieve_relevant_chunks(st.session_state.project_code + user_input)
                conversation = ""
                for turn in st.session_state.chat_history:
                    role = "🎧 You" if turn["role"] == "user" else "🎹 Music Blocks Bot"
                    conversation += f"{role}: {turn['content']}\n"

                mode_instruction = ""

                if st.session_state.user_prompt_count < 2:
                    mode_instruction = (
                        "You should keep the tone curious and keep asking questions to understand what the student wants to do. "
                        "Keep things fun, ask what they’re trying to build, and make them feel excited to share more! 🎵"
                    )
                else:
                    mode_instruction = (
                        "Now it’s time to help more directly. Suggest changes to fix bugs, improve the music, or try new things. "
                        "Be confident, proactive, and guide them clearly through small changes. Offer direct help instead of just asking questions. 🎯"
                    )

                final_prompt = (
                        SYSTEM_INSTRUCTION + "\n\n"
                        + f"The user is working with the **{st.session_state.selected_instrument}** instrument.\n\n"
                        + mode_instruction + "\n\n"
                        + "Here is the full Music Blocks project code:\n"
                        + st.session_state.project_code + "\n\n"
                        + "Here are helpful parts from documentation or examples:\n"
                        + "\n".join(context_chunks) + "\n\n"
                        + "Conversation history so far:\n"
                        + conversation
                        + f"🎧 You: {user_input}\n🎹 Music Bot:"
                )

                gemini_reply = ask_gemini(final_prompt)

                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "music_blocks_bot", "content": gemini_reply})

            except Exception as e:
                st.error(f"Gemini API error: {str(e)}")

    for turn in st.session_state.chat_history:
        with st.chat_message("user" if turn["role"] == "user" else "assistant"):
            st.markdown(turn["content"])

    def generate_chat_export():
        export_content = "Music Blocks Debugger Chat Export\n"
        export_content += f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        export_content += "Project Code:\n"
        export_content += st.session_state.project_code + "\n\n"
        export_content += "Chat History:\n\n"

        for turn in st.session_state.chat_history:
            role = "You" if turn["role"] == "user" else "Music Blocks Bot"
            export_content += f"{role}:\n{turn['content']}\n\n"

        return export_content

    scroll_script = """
    <script>
        setTimeout(function() {
            var chatAnchor = document.getElementById("bottom-anchor");
            if (chatAnchor) {
                chatAnchor.scrollIntoView({ behavior: "smooth" });
            }
        }, 100);
    </script>
    <div id="bottom-anchor"></div>
    """
    st.components.v1.html(scroll_script, height=0)

    st.divider()
    
    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.chat_history:
            st.download_button(
                "💾 Export Chat",
                data=generate_chat_export(),
                file_name=f"music_blocks_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                help="Download the full chat history as a text file"
            )
        else:
            st.button("💾 Export Chat", disabled=True, help="No chat history to export yet")

    with col2:
        if st.button("🗑️ Clear Chat", help="Clear all chat messages"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")

