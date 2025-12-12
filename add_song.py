#!/usr/bin/env python3
"""
Add a song to the DJ set from a YouTube link.
Usage: python add_song.py <youtube_url> <category>
"""

import json
import sys
import re
from urllib.parse import urlparse, parse_qs
import subprocess


def extract_video_id(youtube_url):
    """Extract video ID from various YouTube URL formats."""
    parsed_url = urlparse(youtube_url)
    
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    
    return None


def get_video_title(youtube_url):
    """Fetch video title using yt-dlp or curl."""
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return None
    
    # Try using yt-dlp first (if installed)
    try:
        result = subprocess.run(
            ['yt-dlp', '--get-title', '--no-playlist', youtube_url],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Fallback: Try to fetch title using curl and parsing HTML
    try:
        result = subprocess.run(
            ['curl', '-s', f'https://www.youtube.com/watch?v={video_id}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # Extract title from HTML
            match = re.search(r'"title":"([^"]+)"', result.stdout)
            if match:
                title = match.group(1)
                # Unescape common HTML entities
                title = title.replace('\\u0026', '&').replace('\\/', '/')
                return title
    except subprocess.TimeoutExpired:
        pass
    
    return None


def parse_title(title):
    """Parse artist and song title from video title."""
    if not title:
        return None, None
    
    # Common patterns for YouTube music videos
    patterns = [
        r'^(.+?)\s*[-–—]\s*(.+?)(?:\s*\(.*\))?(?:\s*\[.*\])?$',  # Artist - Song
        r'^(.+?)\s*[:|]\s*(.+?)(?:\s*\(.*\))?(?:\s*\[.*\])?$',   # Artist : Song or Artist | Song
        r'^"(.+?)"\s+by\s+(.+?)(?:\s*\(.*\))?$',                  # "Song" by Artist
    ]
    
    for pattern in patterns:
        match = re.match(pattern, title, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                # Pattern 3 has reversed order
                if 'by' in pattern:
                    return groups[1].strip(), groups[0].strip()
                else:
                    return groups[0].strip(), groups[1].strip()
    
    # If no pattern matches, prompt user
    return None, None


def load_songs_json(filepath='songs.json'):
    """Load the songs.json file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: {filepath} is not valid JSON")
        sys.exit(1)


def save_songs_json(data, filepath='songs.json'):
    """Save the songs.json file with proper formatting."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_category(data, category_name):
    """Find a category in the JSON structure."""
    categories = data.get('dj_set', {}).get('categories', [])
    
    # Try exact match first
    for cat in categories:
        if cat.get('category', '').lower() == category_name.lower():
            return cat
    
    # Try partial match
    for cat in categories:
        if category_name.lower() in cat.get('category', '').lower():
            return cat
    
    return None


def add_song(youtube_url, category_name, artist=None, song_title=None):
    """Add a song to the songs.json file."""
    # Load JSON
    data = load_songs_json()
    
    # Get video title if artist/song not provided
    if not artist or not song_title:
        print(f"Fetching video information from YouTube...")
        video_title = get_video_title(youtube_url)
        
        if video_title:
            print(f"Video title: {video_title}")
            parsed_artist, parsed_song = parse_title(video_title)
            
            if not artist:
                if parsed_artist:
                    artist = parsed_artist
                else:
                    artist = input("Enter artist name: ").strip()
            
            if not song_title:
                if parsed_song:
                    song_title = parsed_song
                else:
                    song_title = input("Enter song title: ").strip()
        else:
            print("Could not fetch video title. Please enter manually:")
            if not artist:
                artist = input("Enter artist name: ").strip()
            if not song_title:
                song_title = input("Enter song title: ").strip()
    
    # Validate inputs
    if not artist or not song_title:
        print("Error: Artist and song title are required")
        sys.exit(1)
    
    # Find category
    category = find_category(data, category_name)
    
    if not category:
        print(f"Category '{category_name}' not found.")
        print("Available categories:")
        for cat in data.get('dj_set', {}).get('categories', []):
            print(f"  - {cat.get('category')}")
        
        create_new = input(f"\nCreate new category '{category_name}'? (y/n): ").lower()
        if create_new == 'y':
            category = {
                'category': category_name,
                'songs': []
            }
            data['dj_set']['categories'].append(category)
        else:
            sys.exit(1)
    
    # Create song object
    song = {
        'title': song_title,
        'artist': artist,
        'youtube_url': youtube_url
    }
    
    # Add song to category
    if 'songs' not in category:
        category['songs'] = []
    
    category['songs'].append(song)
    
    # Save JSON
    save_songs_json(data)
    
    print(f"\n✓ Added '{song_title}' by {artist} to category '{category.get('category')}'")
    return True


def main():
    if len(sys.argv) < 3:
        print("Usage: python add_song.py <youtube_url> <category> [artist] [song_title]")
        print("\nExample:")
        print("  python add_song.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' 'Rock'")
        print("  python add_song.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' 'Rock' 'Rick Astley' 'Never Gonna Give You Up'")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    category = sys.argv[2]
    artist = sys.argv[3] if len(sys.argv) > 3 else None
    song_title = sys.argv[4] if len(sys.argv) > 4 else None
    
    add_song(youtube_url, category, artist, song_title)


if __name__ == '__main__':
    main()
