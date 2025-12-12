# DJ Set Song Manager

## Overview
This project contains a structured JSON database of DJ set songs organized by category, along with a Python script to easily add new songs.

## Files
- `songs.json` - The main database of songs organized by categories
- `add_song.py` - Python script to add new songs to the database
- `songs.txt` - Original song list (source file)

## Usage

### Adding a Song

The `add_song.py` script allows you to add songs to your DJ set in three ways:

#### 1. Auto-extract artist and title from YouTube
The script will fetch the video title and attempt to parse the artist and song name automatically:

```bash
python add_song.py 'https://www.youtube.com/watch?v=VIDEO_ID' 'Category Name'
```

**Example:**
```bash
python add_song.py 'https://www.youtube.com/watch?v=hTWKbfoikeg' 'Rock'
```

If the script can't automatically parse the artist/song, it will prompt you to enter them manually.

#### 2. Manually specify artist and title
You can provide the artist and song title directly:

```bash
python add_song.py 'URL' 'Category' 'Artist Name' 'Song Title'
```

**Example:**
```bash
python add_song.py 'https://www.youtube.com/watch?v=09R8_2nJtjg' 'Rock' 'Imagine Dragons' 'Radioactive'
```

#### 3. Interactive mode
If the script can't determine the artist or title, it will prompt you interactively.

### Supported YouTube URL Formats
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

### Categories
The current categories in your DJ set are:
- **Hip Hop**
- **Dance**
- **Country Vibe**
- **Disco**
- **Epics**
- **Rock**
- **2000's House - Defected**
- **End of the Night**

The script supports:
- Case-insensitive category matching
- Partial category name matching
- Creating new categories if they don't exist

### Examples

```bash
# Add a song with auto-detection
python add_song.py 'https://www.youtube.com/watch?v=kJQP7kiw5Fk' 'Dance'

# Add a song with manual details
python add_song.py 'https://www.youtube.com/watch?v=kJQP7kiw5Fk' 'Dance' 'Luis Fonsi' 'Despacito'

# Create a new category
python add_song.py 'https://www.youtube.com/watch?v=VIDEO_ID' 'EDM'
```

## Requirements
- Python 3.6+
- Standard library only (no external dependencies required)
- Optional: `yt-dlp` for better YouTube title extraction (falls back to curl if not available)

## Notes
- The script automatically formats the JSON with proper indentation
- Songs are appended to the end of their category
- The original YouTube URL is preserved exactly as provided
- UTF-8 encoding is used to support international characters
