#!/usr/bin/env python
"""
Extract WordPress pages from SQL dump
"""
import re
import json

def extract_pages(sql_file):
    """Parse WordPress pages from SQL dump"""
    pages = []
    
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find INSERT statements
    pattern = r"INSERT INTO `wp_posts` VALUES\s*\((.+)\);"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("No wp_posts data found")
        return pages
    
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
        
        try:
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
            
            # Only import published pages
            if post_type == 'page' and post_status == 'publish':
                if post_title and post_title.strip():
                    pages.append({
                        'ID': post_id,
                        'title': post_title,
                        'content': post_content,
                        'date': post_date,
                        'slug': post_name
                    })
        except Exception as e:
            print(f"Error parsing record: {e}")
            continue
    
    return pages

def main():
    sql_file = '/Users/mars/Documents/Coding/my_press/data/pages.sql'
    pages = extract_pages(sql_file)
    print(f"Found {len(pages)} pages")
    
    # Save to JSON
    output_file = '/Users/mars/Documents/Coding/my_press/data/pages.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {output_file}")
    
    # Print all pages
    for page in pages:
        print(f"\n{page['title']}")
        print(f"  Slug: {page['slug']}")
        print(f"  Date: {page['date']}")

if __name__ == '__main__':
    main()
