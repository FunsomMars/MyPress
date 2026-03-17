from django import template
import re

register = template.Library()

@register.filter
def parse_shortcodes(content):
    """Parse WordPress shortcodes to HTML"""
    if not content:
        return content
    
    # Unescape WordPress/Wagtail escaped characters
    # The content has \" which is backslash + quote
    content = content.replace('\\"', '"')
    content = content.replace("\\'", "'")
    content = content.replace("\\\\", "\\")
    
    # Parse [audio] shortcode
    audio_pattern = r'\[audio mp3="([^"]+)"(.*?)\]'
    def replace_audio(match):
        mp3_url = match.group(1)
        extra = match.group(2) if match.group(2) else ''
        preload = 'auto' if 'preload="auto"' in extra else 'none'
        return f'<audio controls src="{mp3_url}" preload="{preload}"></audio>'
    content = re.sub(audio_pattern, replace_audio, content)
    
    # Parse [video] shortcode  
    video_pattern = r'\[video(.*?)\]'
    def replace_video(match):
        attrs = match.group(1)
        src_match = re.search(r'src="([^"]+)"', attrs)
        if src_match:
            src = src_match.group(1)
            return f'<video controls src="{src}"></video>'
        return match.group(0)
    content = re.sub(video_pattern, replace_video, content)
    
    # Clean up self-closing img tags
    content = re.sub(r'<img([^>]*)/>', r'<img\1 />', content)
    
    return content
