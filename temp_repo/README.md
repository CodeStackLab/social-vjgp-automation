# Social Media Automation with Veo 3 Fast

Automated social media content generation using Google's Veo 3.1 Fast model for video generation with professional branding.

## Features

✅ **Veo 3 Fast Video Generation**
- 8-second clips in ~90 seconds
- Native audio included
- 9:16 vertical format (720p)
- Model: `veo-3.1-fast-generate-001`

✅ **Professional Branding**
- Intro scene with logo
- Outro with branding message
- Logo overlay on main content
- Custom fonts (Montserrat)

✅ **Optimized Performance**
- Parallel video generation
- Proper async polling
- Token-efficient single video tests

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install google-genai moviepy pillow numpy

# Set environment variables
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/google_credentials.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="True"
```

### 2. Generate Single Video (Testing)

```bash
python single_test.py
```

### 3. Add Branding to Existing Video

```bash
python add_branding.py
```

### 4. Full Branded Video Generation

```bash
python test_branded_veo3.py
```

## Key Files

- **`app/video_engine.py`** - Core video generation engine
- **`single_test.py`** - Single video test (token-efficient)
- **`add_branding.py`** - Add branding to existing videos
- **`veo3_official.py`** - Official documentation implementation

## Veo 3 Integration

### Correct Implementation

```python
from google import genai
from google.genai.types import GenerateVideosConfig

client = genai.Client(vertexai=True, project=PROJECT_ID, location='us-central1')

operation = client.models.generate_videos(
    model="veo-3.1-fast-generate-001",
    prompt="Your video prompt here",
    config=GenerateVideosConfig(aspect_ratio='9:16')
)

# CRITICAL: Use client.operations.get() for polling
while not operation.done:
    time.sleep(15)
    operation = client.operations.get(operation)  # Refresh status

# Extract video bytes (NOT .data!)
video_bytes = operation.result.generated_videos[0].video.video_bytes
```

### Common Mistakes Fixed

❌ **Wrong:** `operation.result.generated_videos[0].video.data`
✅ **Correct:** `operation.result.generated_videos[0].video.video_bytes`

❌ **Wrong:** Polling without refreshing operation
✅ **Correct:** `operation = client.operations.get(operation)`

## Performance

- **Single 8s clip:** ~90 seconds
- **4 clips parallel:** ~2-3 minutes total
- **Branding assembly:** ~30 seconds

## Assets Required

```
assets/
├── fonts/
│   ├── Montserrat-Bold.ttf
│   └── Montserrat-Light.ttf
└── Virtual Job Guru/
    └── Final Files/
        └── PNG Files/
            └── virtualjobguru-01.png
```

## Output

Videos are saved to:
- `/app/generated_media/videos/` (web-accessible)
- Format: MP4, 9:16, 30fps, 8000k bitrate
- Audio: AAC codec

## License

MIT

## Credits

- **Veo 3.1 Fast** - Google DeepMind
- **VirtualJobGuru** - Branding assets
