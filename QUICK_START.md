# 🎵 Music Blocks Debugger - Quick Start Guide
**Version:** 1.0 | **Last Updated:** January 20, 2026

---

## ⚡ Quick Features Overview

### 🎯 Main Components

| Component | Feature | Status |
|-----------|---------|--------|
| 🎼 Instrument Selector | Choose from 15 instruments | ✅ Ready |
| 📝 Code Input Area | Paste JSON Music Blocks code | ✅ Ready |
| 🔍 Validation | Real-time error checking (VS Code style) | ✅ Ready |
| ▶️ Play Button (Top) | Quick access playback controls | ✅ Ready |
| ▶️ Play Button (Below) | Playback after code execution | ✅ Ready |
| 🎵 Volume Control | Adjustable from 0-100% | ✅ Ready |
| 💬 AI Debugger | Gemini-powered debugging assistant | ✅ Ready |
| 💾 Export | Save chat history as .txt | ✅ Ready |

---

## 🚀 Usage Flow

```
1. SELECT INSTRUMENT
   ↓
2. PASTE JSON CODE
   ↓
3. VALIDATE (Real-time)
   ↓
4. LAUNCH PROJECT
   ↓
5. PLAY & TEST MUSIC
   ↓
6. DEBUG WITH AI CHAT
   ↓
7. EXPORT RESULTS
```

---

## 🎹 Supported Instruments (15 Total)

```
🎹 Piano          🎺 Trumpet       🎻 Violin
🥁 Drum           🎸 Guitar        🎷 Saxophone
🎺 Trombone       🎸 Bass Guitar   🔔 Bells
🪕 Banjo          🎙️ Voice         🎺 French Horn
🎸 Electric Guitar 📯 Bugle        ⛔ Stop
```

---

## 🔧 Technical Details

### Session State Variables
- `chat_history` - Chat messages
- `project_code` - Processed code
- `raw_code` - Original JSON input
- `selected_instrument` - Active instrument
- `code_valid` - Validation status
- `user_prompt_count` - Conversation turn counter

### API Integrations
- **Gemini API** - AI debugging responses
- **Qdrant** - Vector database for code retrieval
- **FastAPI** - Backend API (port 8000)

### Supported Format
- **JSON** - Music Blocks exported projects

---

## 📍 Section Locations

| Section | Where to Find |
|---------|---------------|
| Instrument Selector | Top, below title |
| Play Controls (1) | Below instrument selector |
| Code Input | "Drop Your Project Here" expander |
| Validation Panel | Below code input |
| Launch Button | Bottom of code expander |
| Play Controls (2) | **BELOW code expander (NEW)** |
| Debug Chat | Below play controls |
| Export/Clear | Bottom of page |

---

## 🎯 Error Handling

### Validation Shows:
- ✅ **Valid JSON** - Green checkmark
- ❌ **JSON Error** - Red X with details
  - Line number
  - Column number
  - Error message
  - Problematic code snippet

### Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| JSON Error at Line X | Syntax issue | Check JSON formatting |
| Missing comma | Array/object syntax | Add missing commas |
| Unclosed bracket | Incomplete JSON | Close all brackets |

---

## 🎵 Play Music Features

### Top Controls (Quick Access)
- ▶️ Play Music - Start playback
- ⏸️ Pause - Pause playback
- 🔄 Restart - Restart from beginning
- 🔊 Volume slider

### Bottom Controls (After Code Run)
- ▶️ Play - Play with celebration 🎈
- ⏸️ Pause - Pause playback
- ⏹️ Stop - Stop playback
- 🔄 Replay - Replay from beginning
- 🔊 Volume slider with instrument name

---

## 💬 AI Debugging Chat

### Features:
- **Smart Mode Detection**
  - First 2 turns: Asks exploratory questions
  - After 2 turns: Provides direct help
  
- **Context Aware**
  - Knows selected instrument
  - Analyzes your code
  - Gives instrument-specific suggestions

- **Kid-Friendly**
  - Simple language
  - Short sentences
  - Encouraging tone with emojis

---

## 📊 Data & Export

### Export Chat
- Includes: Full chat history + processed code
- Format: Plain text (.txt)
- Filename: `music_blocks_chat_YYYYMMDD_HHMMSS.txt`

### Clear Chat
- Removes all messages
- Code remains saved
- Can restart debugging

---

## ⚙️ Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=your_key_here
QDRANT_API_KEY=your_key_here
QDRANT_URL=your_url_here
```

### Python Version
- Required: Python 3.10+
- Virtual Environment: `.venv/`

---

## 🐛 Troubleshooting

### Issue: Code area is empty
**Solution:** Refresh the page - session state will restore

### Issue: Play button not appearing
**Solution:** 
1. Check JSON validation (must be green ✅)
2. Click "Launch" button
3. Wait for Gemini response

### Issue: Gemini API error
**Solution:**
1. Check OPENAI_API_KEY in .env
2. Verify internet connection
3. Check API rate limits

---

## 📈 Future Enhancements

- [ ] Audio generation module
- [ ] More instruments
- [ ] MIDI file export
- [ ] Real-time visualization
- [ ] Code suggestions
- [ ] Preset templates

---

## ✅ All Changes Saved

**Files Modified:**
- ✅ `app/main.py` - All features implemented
- ✅ `CHANGES_LOG.md` - Complete change documentation

**Status:** Production Ready 🚀

**No data loss:** All changes use safe session state management

---

## 📞 Support

For issues or questions, check:
1. Session state initialization (top of main.py)
2. API keys in .env file
3. JSON format validation
4. Browser console for errors

---

**Enjoy debugging your Music Blocks projects! 🎵**
