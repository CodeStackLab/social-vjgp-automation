"""
Complete Professional Video Generation API
Integrates: Research Engine + Video Generator + Platform Optimizer
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import research_engine
import video_engine_pro
import platform_optimizer
import json
import time


def generate_complete_professional_video(topic: str, niche: str = "HR Training"):
    """
    Complete end-to-end professional video generation
    
    Steps:
    1. Research topic with Perplexity (keywords, hook, script)
    2. Generate 30s video with Veo 3.1 (photorealistic, audio, subtitles)
    3. Create platform-optimized content (titles, descriptions, hashtags)
    
    Args:
        topic: Video topic
        niche: Content niche
        
    Returns:
        Dict with:
        - video_path: Path to generated video
        - video_url: Public URL
        - platform_content: Content for all platforms
        - metadata: Generation stats
    """
    
    start_time = time.time()
    
    print("="*80)
    print("🎬 PROFESSIONAL VIDEO GENERATION PIPELINE")
    print("="*80)
    print(f"📝 Topic: {topic}")
    print(f"🎯 Niche: {niche}")
    print("="*80)
    
    # === STEP 1: RESEARCH ===
    print("\\n🔍 STEP 1: Perplexity Research & Script Generation")
    print("-"*80)
    
    research_data = research_engine.research_topic_with_keywords(topic, niche)
    
    if not research_data:
        return {
            "success": False,
            "error": "Research failed"
        }
    
    print(f"✅ Research complete!")
    print(f"   Keywords: {', '.join(research_data['keywords'][:5])}")
    print(f"   Hook: {research_data['hook']}")
    
    # === STEP 2: VIDEO GENERATION ===
    print("\\n🎬 STEP 2: Professional Video Generation (Veo 3.1)")
    print("-"*80)
    print(f"   Target: 3-5 minutes generation time")
    print(f"   Quality: Client-ready, photorealistic")
    
    creds = video_engine_pro.init_vertex()
    
    video_path, filename = video_engine_pro.create_professional_video(
        hook=research_data['hook'],
        main_script=research_data['main_script'],
        cta=research_data['cta'],
        visual_prompt=research_data['visual_prompt'],
        title=topic,
        creds=creds
    )
    
    if not video_path:
        return {
            "success": False,
            "error": f"Video generation failed: {filename}"
        }
    
    video_url = f"https://{os.getenv('DOMAIN', 'vjgu.online')}/videos/videos/{filename}"
    
    print(f"\\n✅ Video generated successfully!")
    print(f"   Path: {video_path}")
    print(f"   URL: {video_url}")
    
    # === STEP 3: PLATFORM OPTIMIZATION ===
    print("\\n📱 STEP 3: Multi-Platform Content Optimization")
    print("-"*80)
    
    platform_content = platform_optimizer.generate_all_platforms_content(
        hook=research_data['hook'],
        main_script=research_data['main_script'],
        cta=research_data['cta'],
        keywords=research_data['keywords']
    )
    
    print(f"✅ Platform content generated for:")
    for platform in platform_content.keys():
        print(f"   • {platform.upper()}")
    
    # === RESULTS ===
    generation_time = time.time() - start_time
    
    result = {
        "success": True,
        "video_path": video_path,
        "video_url": video_url,
        "filename": filename,
        "research": {
            "keywords": research_data['keywords'],
            "hook": research_data['hook'],
            "script": research_data['main_script'],
            "cta": research_data['cta']
        },
        "platform_content": platform_content,
        "metadata": {
            "generation_time_seconds": round(generation_time, 2),
            "generation_time_minutes": round(generation_time / 60, 2),
            "topic": topic,
            "niche": niche,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    
    print("\\n" + "="*80)
    print("✅ COMPLETE! Professional video ready for publishing")
    print("="*80)
    print(f"⏱️  Total time: {result['metadata']['generation_time_minutes']} minutes")
    print(f"🎬 Video: {video_url}")
    print(f"📱 Platforms: {len(platform_content)} platforms ready")
    print("="*80)
    
    return result


def save_result_to_file(result: dict, output_file: str = None):
    """Save complete result to JSON file"""
    
    if not output_file:
        output_file = f"/app/generated_media/results/result_{int(time.time())}.json"
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\\n💾 Results saved to: {output_file}")
    
    # Also save platform content as separate text file for easy copy-paste
    text_file = output_file.replace('.json', '_platforms.txt')
    with open(text_file, 'w') as f:
        f.write(platform_optimizer.format_output_for_display(result['platform_content']))
    
    print(f"📝 Platform content saved to: {text_file}")


if __name__ == "__main__":
    # Test the complete pipeline
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate professional video with multi-platform content')
    parser.add_argument('--topic', type=str, default="How to answer 'Tell me about yourself' in interviews",
                       help='Video topic')
    parser.add_argument('--niche', type=str, default="HR Training",
                       help='Content niche')
    parser.add_argument('--output', type=str, default=None,
                       help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Generate
    result = generate_complete_professional_video(args.topic, args.niche)
    
    if result['success']:
        # Save results
        save_result_to_file(result, args.output)
        
        # Print platform content
        print("\\n" + platform_optimizer.format_output_for_display(result['platform_content']))
    else:
        print(f"\\n❌ Generation failed: {result.get('error')}")
        exit(1)
