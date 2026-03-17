#!/usr/bin/env python3
import re

with open('data/wordpress_posts.sql') as f:
    content = f.read()

match = re.search(r'INSERT INTO `wp_posts` VALUES\s*\((.+)\);', content, re.DOTALL)
if match:
    values = match.group(1)
    raw_records = values.split('),(')
    record = raw_records[0]
    
    # FIXED: Better parse with proper depth tracking
    fields = []
    field = ''
    in_quotes = False
    depth = 0
    
    i = 0
    while i < len(record):
        char = record[i]
        
        # Handle escape
        if char == '\\' and i + 1 < len(record):
            field += char + record[i + 1]
            i += 2
            continue
        
        # Handle quotes
        if char == "'" and not in_quotes:
            in_quotes = True
        elif char == "'" and in_quotes:
            if i + 1 < len(record) and record[i + 1] == "'":
                field += "''"
                i += 2
                continue
            else:
                in_quotes = False
                fields.append(field.strip("'").strip())
                field = ''
                i += 1
                continue
        
        # Handle depth only outside quotes
        if not in_quotes:
            if char == '(':
                depth += 1
                field += char
            elif char == ')':
                depth -= 1
                field += char
            elif char == ',' and depth == 0:
                fields.append(field.strip())
                field = ''
                i += 1
                continue
        
        field += char
        i += 1
    
    if field:
        fields.append(field.strip().strip("'"))
    
    print(f'Fields: {len(fields)}')
    # Print key fields
    print(f'\nKey fields:')
    print(f'0 (ID): [{fields[0]}]')
    print(f'2 (date): [{fields[2]}]')
    print(f'4 (content): [{fields[4][:40]}...]')
    print(f'5 (title): [{fields[5]}]')
    print(f'7 (status): [{fields[7]}]')
    print(f'20 (type): [{fields[20]}]')
