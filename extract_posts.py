#!/usr/bin/env python
"""
Extract WordPress posts from SQL dump
"""
import re
import json
import sys

def extract_posts(sql_file):
    """Parse WordPress posts from SQL dump"""
    posts = []
    
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find INSERT statements
    pattern = r"INSERT INTO `wp_posts` VALUES\s*\((.+)\);"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("No wp_posts data found")
        return posts
    
    values_content = match.group(1)
    raw_records = values_content.split('),(')
    
    for i, raw in enumerate(raw_records):
        if i == 0:
            record = '(' + raw
        elif i == len(raw_records) - 1:
            record = raw + ')'
        else:
            record = '(' + raw + ')'
        
        if not record.strip():
            continue
        
        # Simple split - won't handle all edge cases
        # This is a simplified parser
        try:
            # Match pattern: (num, 'string', 'date', ...)
            parts = []
            current = ''
            in_string = False
            escape_next = False
            
            for char in record:
                if escape_next:
                    current += char
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    current += char
                    continue
                
                if char == "'" and not escape_next:
                    in_string = not in_string
                    current += char
                elif char == ',' and not in_string:
                    parts.append(current.strip().strip("'"))
                    current = ''
                else:
                    current += char
            
            # Add last part
            parts.append(current.strip().strip("'"))
            
            if len(parts) < 21:
                continue
            
            post_id = parts[0]
            post_date = parts[2] if len(parts) > 2 else ''
            post_content = parts[4] if len(parts) > 4 else ''
            post_title = parts[5] if len(parts) > 5 else ''
            post_status = parts[7] if len(parts) > 7 else ''
            post_type = parts[20] if len(parts) > 20 else ''
            post_name = parts[11] if len(parts) > 11 else ''
            
            if post_type == 'post' and post_status == 'publish':
                if post_title and post_title.strip():
                    posts.append({
                        'ID': post_id,
                        'title': post_title,
                        'content': post_content,
                        'date': post_date,
                        'slug': post_name
                    })
        except Exception as e:
            print(f"Error parsing record: {e}")
            continue
    
    return posts

def main():
    sql_file = '/Users/mars/Documents/Coding/my_press/data/wordpress_posts.sql'
    posts = extract_posts(sql_file)
    print(f"Found {len(posts)} posts")
    
    # Save to JSON
    output_file = '/Users/mars/Documents/Coding/my_press/data/posts.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {output_file}")
    
    # Print first 3 posts as sample
    for post in posts[:3]:
        print(f"\n{post['title'][:50]}...")
        print(f"  Date: {post['date']}")
        print(f"  Slug: {post['slug']}")

if __name__ == '__main__':
    main()
