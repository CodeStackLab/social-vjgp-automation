# 🎬 Professional Video Generation System - Implementation Plan

## 📋 Overview
Build a complete video generation pipeline that creates **client-ready, professional 30-second vertical videos** with:
- Google Vertex AI Veo 3.1 (video + audio together)
- Auto-generated subtitles from audio
- Perplexity-based keyword research
- Multi-platform optimization (TikTok, Instagram, YouTube, Facebook, LinkedIn)
- Photorealistic human presenters (NO cartoons/anime)
- Professional branding throughout

## 🎯 Current Issues to Fix
1. ❌ Video generation taking 20+ minutes (Target: 3-5 minutes)
2. ❌ No videos being generated successfully
3. ❌ Missing Perplexity keyword research integration
4. ❌ No platform-specific content optimization
5. ❌ Subtitle system not working (google-cloud-speech installed but not tested)

## 🔧 Technical Architecture

### Phase 1: Core Video Generation Engine ✅ (Partially Done)
**File:** `video_engine.py`

#### 1.1 Veo 3.1 Integration
- [x] Using `veo-3.1-generate-preview` model
- [x] Audio generation enabled (`with_audio=True`)
- [x] Parallel clip generation (5-6 clips simultaneously)
- [ ] **FIX:** Optimize polling from 5s to 3s
- [ ] **FIX:** Add timeout handling (max 5 min per clip)
- [ ] **ADD:** Fallback to single longer clip if parallel fails

#### 1.2 Subtitle Generation System
- [x] Google Cloud Speech-to-Text integration added
- [ ] **TEST:** Verify transcription works with Veo audio
- [ ] **FIX:** Handle multiple audio formats (MP4, WAV)
- [ ] **ADD:** Karaoke-style word highlighting
- [ ] **ADD:** Platform-safe positioning (avoid crop zones)

#### 1.3 Photorealistic Character Prompts
**Current prompts are too generic. Need:**
```
❌ OLD: "A charismatic HR trainer giving a speech"
✅ NEW: "Photorealistic corporate trainer, 30s professional woman, natural skin texture, 
         confident eye contact, navy blazer, modern office, 4K cinematic, real human features,
         NOT cartoon, NOT anime, NOT stylized"
```

### Phase 2: Perplexity Research Integration 🆕
**File:** `research_engine.py` (NEW)

#### 2.1 Keyword Research
```python
def research_topic_with_keywords(topic):
    """
    1. Query Perplexity for trending keywords
    2. Analyze search intent
    3. Generate SEO-optimized script
    4. Return: keywords, script, visual_prompts
    """
```

#### 2.2 Content Generation
- Hook generation (first 3 seconds)
- Script optimization (25 seconds)
- CTA generation (last 2 seconds)

### Phase 3: Multi-Platform Optimizer 🆕
**File:** `platform_optimizer.py` (NEW)

#### 3.1 Platform Specifications
```python
PLATFORM_SPECS = {
    "tiktok": {
        "title_max": 100,
        "description_max": 2200,
        "hashtags": (3, 5),
        "tone": "casual, trendy"
    },
    "instagram": {
        "caption_max": 2200,
        "hashtags": (5, 10),
        "tone": "engaging, visual"
    },
    "youtube": {
        "title_max": 100,
        "description_max": 1000,
        "hashtags": (3, 5),
        "tone": "informative, searchable"
    },
    "facebook": {
        "caption_max": 2000,
        "tone": "conversational"
    },
    "linkedin": {
        "caption_max": 700,
        "hashtags": (3, 5),
        "tone": "professional, authoritative"
    }
}
```

#### 3.2 Content Adaptation
```python
def generate_platform_content(base_script, keywords, platform):
    """
    Generate unique title, description, hashtags for each platform
    - Use Perplexity keywords naturally
    - Follow character limits
    - Match platform tone
    - Optimize for engagement
    """
```

### Phase 4: Enhanced Video Structure 🔄
**File:** `video_engine.py` (UPDATE)

#### 4.1 Intro (0-3s)
- Clean branded intro
- Logo: top-right, 120px width, 80% opacity
- Smooth fade-in
- **Hook text overlay** (from Perplexity research)

#### 4.2 Main Content (3-25s)
- **Single photorealistic Veo clip** (NOT multiple clips - faster!)
- Realistic human presenter
- Natural movements and expressions
- Corporate/classroom environment
- Auto-generated subtitles synced to audio

#### 4.3 Outro (25-30s)
- Branded ending
- Logo + CTA: "Follow for more tips"
- Smooth fade-out

### Phase 5: Performance Optimization ⚡

#### 5.1 Speed Improvements
**Current:** 20+ minutes
**Target:** 3-5 minutes

**Changes:**
1. **Single Clip Strategy:** Generate ONE 22-second Veo clip instead of 5-6 clips
   - Reduces API calls from 6 to 1
   - Reduces total wait time from ~10 min to ~2 min
   
2. **Faster Polling:** 3s instead of 5s

3. **Parallel Processing:**
   - Generate video clip (async)
   - While waiting, prepare intro/outro assets
   - Process subtitles immediately after video completes

4. **Caching:**
   - Cache intro/outro clips (reusable)
   - Cache logo assets

#### 5.2 Error Handling
- Timeout after 5 minutes per clip
- Retry logic (max 2 retries)
- Fallback to image-based video if Veo fails

## 📁 File Structure

```
social_automato/
├── app/
│   ├── video_engine.py          # ✅ Core video generation (UPDATE)
│   ├── research_engine.py       # 🆕 Perplexity keyword research
│   ├── platform_optimizer.py    # 🆕 Multi-platform content
│   ├── main.py                  # ✅ Flask API (UPDATE endpoints)
│   ├── requirements.txt         # ✅ Updated dependencies
│   └── utils.py                 # 🆕 Helper functions
```

## 🚀 Implementation Steps

### Step 1: Fix Current Video Generation (URGENT)
1. Update video_engine.py:
   - Change from 5-6 clips to 1 long clip
   - Add timeout handling
   - Improve error logging
   - Test subtitle extraction

### Step 2: Add Perplexity Research
1. Create research_engine.py
2. Integrate with main.py
3. Test keyword extraction

### Step 3: Build Platform Optimizer
1. Create platform_optimizer.py
2. Add platform-specific templates
3. Test content generation for all platforms

### Step 4: Update Main API
1. Add new endpoint: `/api/generate-professional-video`
2. Integrate all components
3. Add progress tracking

### Step 5: Testing & Validation
1. Generate test video
2. Verify 3-5 minute generation time
3. Check subtitle quality
4. Validate platform content

## 📊 Success Metrics

- ✅ Video generation: 3-5 minutes (currently 20+ min)
- ✅ Photorealistic humans (NO cartoons)
- ✅ Auto-subtitles synced perfectly
- ✅ Platform-specific content for all 5 platforms
- ✅ SEO-optimized with Perplexity keywords
- ✅ Professional, client-ready quality

## 🔄 Next Actions

1. **IMMEDIATE:** Fix video generation speed
2. **TODAY:** Add Perplexity research
3. **TODAY:** Build platform optimizer
4. **TEST:** Generate first professional video
5. **DEPLOY:** Update production container
