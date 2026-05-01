"""
Multi-Platform Content Optimizer
Generates unique titles, descriptions, and hashtags for each social media platform
"""

from typing import Dict, List
import textwrap


# Platform specifications and character limits
PLATFORM_SPECS = {
    "tiktok": {
        "title_max": 150,
        "caption_max": 2000,
        "hashtag_range": (3, 5),
        "tone": "casual, trendy, energetic",
        "emoji_friendly": True,
        "aspect_ratio": "9:16",
        "width": 1080,
        "height": 1920
    },
    "instagram": {
        "title_max": 150,
        "caption_max": 2200,
        "hashtag_range": (5, 10),
        "tone": "engaging, visual, inspirational",
        "emoji_friendly": True,
        "aspect_ratio": "1:1",
        "width": 1080,
        "height": 1080
    },
    "youtube": {
        "title_max": 100,
        "caption_max": 5000,
        "hashtag_range": (3, 5),
        "tone": "informative, searchable, clear",
        "emoji_friendly": False,
        "aspect_ratio": "9:16",
        "width": 1080,
        "height": 1920
    },
    "facebook": {
        "title_max": 255,
        "caption_max": 2000,
        "hashtag_range": (2, 4),
        "tone": "conversational, friendly",
        "emoji_friendly": True,
        "aspect_ratio": "1:1",
        "width": 1080,
        "height": 1080
    },
    "linkedin": {
        "title_max": 200,
        "caption_max": 3000,
        "hashtag_range": (3, 5),
        "tone": "professional, authoritative, insightful",
        "emoji_friendly": False,
        "aspect_ratio": "4:5",
        "width": 1080,
        "height": 1350
    },
    "reels": {
        "title_max": 150,
        "caption_max": 2200,
        "hashtag_range": (5, 10),
        "tone": "energetic, visual",
        "emoji_friendly": True,
        "aspect_ratio": "9:16",
        "width": 1080,
        "height": 1920
    }
}


def generate_platform_content(
    hook: str,
    main_script: str,
    cta: str,
    keywords: List[str],
    platform: str
) -> Dict[str, str]:
    """
    Generate optimized content for a specific platform
    
    Args:
        hook: Attention-grabbing hook
        main_script: Main content script
        cta: Call to action
        keywords: SEO keywords
        platform: Target platform name
        
    Returns:
        Dict with title, description, hashtags
    """
    
    spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["instagram"])
    
    # Generate title (for platforms that need it)
    title = _generate_title(hook, keywords, spec)
    
    # Generate description/caption
    description = _generate_description(
        hook, main_script, cta, keywords, spec, platform
    )
    
    # Generate hashtags
    hashtags = _generate_hashtags(keywords, spec, platform)
    
    return {
        "title": title,
        "description": description,
        "hashtags": hashtags,
        "full_caption": f"{description}\n\n{' '.join(hashtags)}" if hashtags else description
    }


def _generate_title(hook: str, keywords: List[str], spec: Dict) -> str:
    """Generate SEO-optimized title with strict length enforcement"""
    
    # Use hook as base, add primary keyword if space allows
    title = hook
    title_max = spec.get("title_max", 100)
    
    if len(title) < title_max - 20 and keywords:
        # Add primary keyword
        primary_keyword = keywords[0].title()
        if primary_keyword.lower() not in title.lower():
            title = f"{title} | {primary_keyword}"
    
    # Strictly truncate if needed
    if len(title) > title_max:
        title = title[:title_max-3].strip() + "..."
    
    return title


def _generate_description(
    hook: str,
    main_script: str,
    cta: str,
    keywords: List[str],
    spec: Dict,
    platform: str
) -> str:
    """Generate platform-optimized description"""
    
    # Platform-specific formatting
    if platform == "linkedin":
        # LinkedIn: Professional, structured
        description = f"{hook}\n\n{main_script}\n\n{cta}"
        
        # Add professional sign-off
        description += "\n\n---\n💼 VirtualJobGuru - Your Career Growth Partner"
        
    elif platform == "youtube":
        # YouTube: Searchable, keyword-rich
        description = f"{hook}\n\n{main_script}\n\n{cta}\n\n"
        description += f"🔍 Topics: {', '.join(keywords[:5])}\n\n"
        description += "📧 Contact: info@virtualjobguru.com\n"
        description += "🌐 www.virtualjobguru.com"
        
    elif platform == "tiktok":
        # TikTok: Short, punchy, emoji-rich
        description = f"{hook} 🔥\n\n{main_script}\n\n{cta} 👉"
        
    elif platform == "instagram":
        # Instagram: Engaging, visual, story-driven
        description = f"{hook} ✨\n\n{main_script}\n\n{cta} 💡\n\n"
        description += "---\n"
        description += "Follow @virtualjobguru for daily career tips!"
        
    else:  # Facebook
        # Facebook: Conversational, community-focused
        description = f"{hook}\n\n{main_script}\n\n{cta}\n\n"
        description += "Like and share if you found this helpful! 👍"
    
    # Truncate if needed
    max_length = spec["caption_max"]
    if len(description) > max_length:
        description = description[:max_length-3] + "..."
    
    return description


def _generate_hashtags(keywords: List[str], spec: Dict, platform: str) -> List[str]:
    """Generate platform-optimized hashtags"""
    
    hashtags = []
    min_tags, max_tags = spec["hashtag_range"]
    
    # Convert keywords to hashtags
    for keyword in keywords[:max_tags-2]:  # Reserve space for platform tags
        # Clean and format
        tag = keyword.replace(" ", "").replace("-", "").title()
        hashtags.append(f"#{tag}")
    
    # Add platform-specific trending tags
    platform_tags = {
        "instagram": ["#Reels", "#CareerTips", "#ProfessionalGrowth"],
        "tiktok": ["#FYP", "#CareerTok", "#JobTips"],
        "youtube": ["#Shorts", "#CareerAdvice"],
        "linkedin": ["#CareerDevelopment", "#ProfessionalGrowth", "#Leadership"],
        "facebook": ["#CareerTips", "#JobAdvice"]
    }
    
    # Add platform tags
    for tag in platform_tags.get(platform, []):
        if len(hashtags) < max_tags and tag not in hashtags:
            hashtags.append(tag)
    
    # Ensure we meet minimum
    generic_tags = ["#Career", "#Success", "#Growth", "#Tips", "#Motivation"]
    for tag in generic_tags:
        if len(hashtags) >= max_tags:
            break
        if tag not in hashtags:
            hashtags.append(tag)
    
    # Trim to max
    hashtags = hashtags[:max_tags]
    
    return hashtags


def generate_all_platforms_content(
    hook: str,
    main_script: str,
    cta: str,
    keywords: List[str]
) -> Dict[str, Dict]:
    """
    Generate optimized content for ALL platforms
    
    Returns:
        Dict with platform names as keys, each containing title, description, hashtags
    """
    
    all_content = {}
    
    for platform in PLATFORM_SPECS.keys():
        all_content[platform] = generate_platform_content(
            hook, main_script, cta, keywords, platform
        )
    
    return all_content


def format_output_for_display(all_content: Dict[str, Dict]) -> str:
    """
    Format all platform content for easy copy-paste
    """
    
    output = []
    output.append("=" * 80)
    output.append("📱 MULTI-PLATFORM CONTENT - READY TO PUBLISH")
    output.append("=" * 80)
    
    for platform, content in all_content.items():
        output.append(f"\n{'='*80}")
        output.append(f"🎯 {platform.upper()}")
        output.append(f"{'='*80}")
        
        if content.get("title"):
            output.append(f"\n📌 TITLE:")
            output.append(f"{content['title']}")
        
        output.append(f"\n📝 DESCRIPTION/CAPTION:")
        output.append(f"{content['description']}")
        
        if content.get("hashtags"):
            output.append(f"\n🏷️  HASHTAGS:")
            output.append(f"{' '.join(content['hashtags'])}")
        
        output.append(f"\n📊 CHARACTER COUNT: {len(content['description'])}/{PLATFORM_SPECS[platform]['caption_max']}")
    
    output.append(f"\n{'='*80}")
    output.append("✅ All content optimized and ready to publish!")
    output.append(f"{'='*80}")
    
    return "\n".join(output)


if __name__ == "__main__":
    # Test the platform optimizer
    print("📱 Testing Platform Optimizer\n")
    
    test_hook = "Want to ace your next interview?"
    test_script = "Master these proven techniques that HR professionals actually look for. From body language to answering tough questions, these strategies will set you apart."
    test_cta = "Follow for more career tips!"
    test_keywords = ["interview tips", "job interview", "career success", "HR advice", "professional growth"]
    
    all_content = generate_all_platforms_content(
        test_hook, test_script, test_cta, test_keywords
    )
    
    print(format_output_for_display(all_content))
