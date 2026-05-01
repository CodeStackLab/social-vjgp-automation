"""
Research and Script Generation Engine
Integrates Perplexity for research and Gemini for script generation
"""

import os
import json
import requests
import time
from typing import Dict, List, Optional

# API Configuration
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

def perplexity_research(topic: str, api_key: str) -> Dict:
    """Research a topic using Perplexity AI"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "You are an expert HR and career consultant. Provide detailed, actionable advice for job seekers and professionals."},
                {"role": "user", "content": f"Research this HR/career topic in detail: {topic}. Provide key insights, tips, and actionable advice that would be valuable for a 20-30 second social media video."}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        research_content = data['choices'][0]['message']['content']
        return {"success": True, "topic": topic, "research": research_content, "sources": data.get('citations', [])}
    except Exception as e:
        print(f"Perplexity research error: {e}")
        return {"success": False, "topic": topic, "error": str(e), "research": f"Failed to research topic: {topic}"}

def gemini_generate_script(
    research_data: Dict,
    client_details: Optional[Dict] = None,
    api_key: str = None,
    duration: int = 24
) -> Dict:
    """Generate video script from research using Gemini (AI Studio)"""
    try:
        active_key = api_key
        if not active_key or active_key.startswith("AQ."):
            # The AQ key is for Vertex, or if key is missing, use the Studio key
            active_key = os.getenv("GEMINI_API_KEY")

        # Build character description
        character = "a professional HR consultant in her 40s, warm smile, professional attire, modern office setting"
        if client_details and 'character_profile' in client_details:
            profile = client_details['character_profile']
            character = f"{profile.get('profession', 'HR consultant')}, {profile.get('appearance', 'professional attire')}, {profile.get('setting', 'modern office')}"
        
        # Build prompt for Gemini
        prompt = f"""You are a professional video script writer for HR and career content.

Research Topic: {research_data['topic']}
Video Style: Direct Response Marketing (Problem -> Agitation -> Solution -> CTA)

Character: {character} (Name: Julia, 20+ years experience as Recruiter)

Create a {duration}-second video script with the following STRICT structure:

1. HOOK (3-5 seconds): Call out the specific problem directly. (e.g., "Are you feeling overwhelmed by...?")
2. INTRO & AUTHORITY (3-5 seconds): "My name is Julia and I've been working as a recruiter for the last 20 years." (Always include this specific phrasing).
3. VALUE/SOLUTION (10-12 seconds): Explain how your "one-to-one coaching session" solves the problem. Mention "step-by-step guidance" or "checking documents".
4. CALL TO ACTION (3-5 seconds): "If you're interested, click on the link below."

For each segment, provide:
- Spoken text (what Julia says)
- Visual description (what we see on screen)
- Timing (duration in seconds)

Format your response as JSON:
{{
  "title": "Catchy video title",
  "hook": {{
    "text": "Are you currently looking for a new job and...",
    "visual": "Close up, concerned expression",
    "duration": 4
  }},
  "intro": {{
    "text": "My name is Julia and I've been working as a recruiter for the last 20 years.",
    "visual": "Julia smiling warmly, text overlay: 'Julia - 20 Years Experience'",
    "duration": 4
  }},
  "main_points": [
    {{
      "text": "In my one-to-one coaching session...",
      "visual": "Julia showing a document or checklist",
      "duration": 10
    }}
  ],
  "cta": {{
    "text": "If you're interested, click on the link below.",
    "visual": "Julia pointing down, graphical arrow overlay",
    "duration": 3
  }},
  "total_duration": {duration}
}}

Keep it conversational, empathetic, and professional. The character should speak directly to camera."""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={active_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 2048}
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        script_text = data['candidates'][0]['content']['parts'][0]['text']
        
        try:
            if '```json' in script_text:
                script_text = script_text.split('```json')[1].split('```')[0].strip()
            elif '```' in script_text:
                script_text = script_text.split('```')[1].split('```')[0].strip()
            script_data = json.loads(script_text)
        except:
            script_data = {"title": research_data['topic'], "raw_script": script_text, "total_duration": duration}
        
        return {"success": True, "script": script_data, "character": character, "topic": research_data['topic']}
    except Exception as e:
        print(f"Gemini script generation error: {e}")
        return {"success": False, "error": str(e), "script": {"title": research_data['topic']}}

def gemini_generate_social_content(
    script: Dict,
    platform: str,
    api_key: str
) -> Dict:
    """Generate platform-specific titles and hashtags"""
    try:
        active_key = api_key
        if not active_key or active_key.startswith("AQ."):
            active_key = os.getenv("GEMINI_API_KEY")

        title = script.get('title', 'Career Tips')
        spec = {
            'instagram': 'Instagram Reels - max 2200 chars, engaging caption, 20-30 hashtags',
            'tiktok': 'TikTok - max 150 chars title, catchy and trendy, 3-5 hashtags',
            'youtube': 'YouTube Shorts - max 100 chars title, SEO-optimized, 5-10 hashtags'
        }.get(platform, 'Instagram Reels')
        
        prompt = f"""Create {spec} for this video:
Title: {title}
Content: {script.get('raw_script', json.dumps(script))}

Provide:
1. Platform-optimized title
2. Engaging caption
3. Relevant hashtags

Format as JSON:
{{
  "title": "Title here",
  "caption": "Caption here",
  "hashtags": ["hashtag1", "hashtag2", ...]
}}"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={active_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024}
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        content_text = data['candidates'][0]['content']['parts'][0]['text']
        
        try:
            if '```json' in content_text:
                content_text = content_text.split('```json')[1].split('```')[0].strip()
            elif '```' in content_text:
                content_text = content_text.split('```')[1].split('```')[0].strip()
            social_data = json.loads(content_text)
        except:
            social_data = {"title": title, "caption": f"Check out this video about {title}!", "hashtags": ["HR", "CareerTips"]}
        
        return {"success": True, "platform": platform, "content": social_data}
    except Exception as e:
        print(f"Social content generation error: {e}")
        return {"success": False, "error": str(e), "content": {"title": title, "caption": "", "hashtags": []}}

def create_character_prompt(script_segment: Dict, character: str) -> str:
    """Create detailed Veo prompt with character consistency"""
    text = script_segment.get('text', '')
    visual = script_segment.get('visual', '')
    prompt = f"{character}, {visual}, speaking directly to camera"
    if 'gestur' in text.lower() or 'point' in text.lower():
        prompt += ", making expressive hand gestures"
    else:
        prompt += ", speaking confidently"
    prompt += ", medium close-up shot, professional lighting, shallow depth of field, cinematic quality, 4k"
    prompt += ", clear audio, professional voice, ambient office sounds"
    return prompt
