#!/usr/bin/env python
"""
Fix URL in database - replace old WordPress URLs with local media paths
This script should be run in the Docker container after importing data.
"""
import sqlite3
import re

def fix_urls():
    conn = sqlite3.connect('/app/db.sqlite3')
    cur = conn.cursor()
    
    fixed_count = 0
    
    # Fix blog pages
    cur.execute('SELECT page_ptr_id, body FROM home_blogpage')
    blog_pages = cur.fetchall()
    
    for page_id, body in blog_pages:
        if body and 'www.mspace.tech/wp-content/uploads' in body:
            new_body = body.replace('https://www.mspace.tech/wp-content/uploads', '/media')
            new_body = new_body.replace('http://www.mspace.tech/wp-content/uploads', '/media')
            cur.execute('UPDATE home_blogpage SET body = ? WHERE page_ptr_id = ?', (new_body, page_id))
            print(f'Fixed blog page {page_id}')
            fixed_count += 1
    
    # Fix custom pages
    cur.execute('SELECT page_ptr_id, body FROM home_custompage')
    custom_pages = cur.fetchall()
    
    for page_id, body in custom_pages:
        if body and 'www.mspace.tech/wp-content/uploads' in body:
            new_body = body.replace('https://www.mspace.tech/wp-content/uploads', '/media')
            new_body = new_body.replace('http://www.mspace.tech/wp-content/uploads', '/media')
            new_body = new_body.replace('https://www.mspace.tech/wp-content', '/media')
            new_body = new_body.replace('http://www.mspace.tech/wp-content', '/media')
            cur.execute('UPDATE home_custompage SET body = ? WHERE page_ptr_id = ?', (new_body, page_id))
            print(f'Fixed custom page {page_id}')
            fixed_count += 1
    
    conn.commit()
    print(f'\nTotal: {fixed_count} pages fixed')

if __name__ == '__main__':
    fix_urls()
