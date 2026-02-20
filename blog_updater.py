import os
from pathlib import Path
from docx import Document
from bs4 import BeautifulSoup
from datetime import datetime

def get_user_mode():
    """Ask user whether to create new blog or update existing"""
    print("\nSelect mode:")
    print("1. Create new blog HTML file")
    print("2. Update existing blog HTML file")
    
    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice in ['1', '2']:
            return choice
        print("Invalid choice. Please enter 1 or 2.")

def get_user_input():
    """Get Word document and HTML file names from user"""
    while True:
        word_doc = input("Enter the Word document name (e.g., blog.docx): ").strip()
        if os.path.exists(word_doc):
            break
        print(f"Error: File '{word_doc}' not found. Please try again.")
    
    while True:
        html_file = input("Enter the blog HTML file name (e.g., blogs/blog1.html): ").strip()
        if os.path.exists(html_file):
            break
        print(f"Error: File '{html_file}' not found. Please try again.")
    
    return word_doc, html_file

def get_new_blog_input():
    """Get Word document and output path for new blog"""
    while True:
        word_doc = input("Enter the Word document name (e.g., blog.docx): ").strip()
        if os.path.exists(word_doc):
            break
        print(f"Error: File '{word_doc}' not found. Please try again.")
    
    while True:
        html_file = input("Enter the output HTML file path (e.g., blogs/blog2.html): ").strip()
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(html_file)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                print(f"Error creating directory: {e}")
                continue
        
        # Check if file already exists
        if os.path.exists(html_file):
            overwrite = input(f"File '{html_file}' already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite == 'y':
                break
        else:
            break
    
    return word_doc, html_file

def extract_content_from_docx(word_doc):
    """Extract content from Word document, skipping the first line (used as title)"""
    doc = Document(word_doc)
    content = []
    is_first_line = True
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            # Skip the first non-empty line as it will be used as the title
            if is_first_line:
                is_first_line = False
                continue
            
            # Determine if it's a heading based on style
            style = para.style.name
            if 'Heading' in style:
                level = int(style.split()[-1]) if style[-1].isdigit() else 1
                content.append({
                    'type': 'heading',
                    'level': level,
                    'text': text
                })
            else:
                # Check if the entire paragraph is bold
                is_bold = all(run.bold for run in para.runs if run.text.strip())
                
                if is_bold and len(para.runs) > 0:
                    # Treat bold lines as subheadings (h3)
                    content.append({
                        'type': 'heading',
                        'level': 3,
                        'text': text
                    })
                else:
                    content.append({
                        'type': 'paragraph',
                        'text': text
                    })
    
    return content

def get_blog_title_from_docx(word_doc):
    """Get the first line of the document as blog title"""
    doc = Document(word_doc)
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            return text
    
    return "Untitled Blog"

def get_blog_description_from_docx(word_doc):
    """Get the first paragraph (second non-empty line) as blog description"""
    doc = Document(word_doc)
    
    lines_found = 0
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            lines_found += 1
            if lines_found == 2:
                # Return first 150 characters as description
                return (text[:150] + "...") if len(text) > 150 else text
    
    return "Click to read more..."

def update_blogs_index(html_file, blog_title, blog_description):
    """Update the blogs/index.html to add the new blog to the list"""
    
    blogs_index = "blogs/index.html"
    
    if not os.path.exists(blogs_index):
        print(f"Warning: {blogs_index} not found. Skipping index update.")
        return False
    
    try:
        with open(blogs_index, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Find the blog-list div
        blog_list = soup.find('div', class_='blog-list')
        
        if not blog_list:
            print("Error: Could not find 'blog-list' div in blogs/index.html")
            return False
        
        # Create the relative path for the link (remove 'blogs/' prefix if present)
        link_path = html_file.replace('blogs/', '')
        
        # Create new blog card HTML
        new_card = f"""<a href="{link_path}" class="blog-card">
        <h3>{blog_title}</h3>
        <p>{blog_description}</p>
    </a>"""
        
        # Parse the new card
        new_soup = BeautifulSoup(new_card, 'html.parser')
        new_element = new_soup.find('a', class_='blog-card')
        
        # Append to blog-list
        blog_list.append(new_element)
        
        # Write back to file
        with open(blogs_index, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        return True
    
    except Exception as e:
        print(f"Error updating blogs index: {e}")
        return False

def update_blog_in_index(html_file, new_title):
    """Update an existing blog card in the blogs/index.html"""
    
    blogs_index = "blogs/index.html"
    
    if not os.path.exists(blogs_index):
        print(f"Warning: {blogs_index} not found. Skipping index update.")
        return False
    
    try:
        with open(blogs_index, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Create the relative path for the link (remove 'blogs/' prefix if present)
        link_path = html_file.replace('blogs/', '')
        
        # Find all blog cards
        blog_cards = soup.find_all('a', class_='blog-card')
        
        # Find the card that links to this blog
        for card in blog_cards:
            href = card.get('href', '')
            if href.endswith(link_path) or href == link_path:
                # Update the h3 title
                title_tag = card.find('h3')
                if title_tag:
                    title_tag.string = new_title
                    
                    # Write back to file
                    with open(blogs_index, 'w', encoding='utf-8') as f:
                        f.write(str(soup.prettify()))
                    return True
        
        print(f"Warning: Could not find blog card for {link_path} in index.")
        return False
    
    except Exception as e:
        print(f"Error updating blog in index: {e}")
        return False

def generate_html_content(content):
    """Generate HTML content from extracted data"""
    html_content = ""
    
    for item in content:
        if item['type'] == 'heading':
            level = item['level']
            html_content += f"    <h{level}>{item['text']}</h{level}>\n"
        elif item['type'] == 'paragraph':
            html_content += f"    <p>{item['text']}</p>\n"
    
    return html_content

def create_new_blog_html(html_file, content_html, blog_title):
    """Create a new blog HTML file from scratch"""
    
    # Create the HTML structure
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{blog_title}</title>
<link rel="stylesheet" href="../css/style.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
</head>
<body class="blog-page">

<nav class="navbar">
<a href="../index.html">Home</a>
<a href="index.html">Back to Blogs</a>
</nav>

<div class="blog-container">
    <h1>{blog_title}</h1>
    <p class="blog-date">{datetime.now().strftime("%B %Y")}</p>

{content_html}
</div>

<script src="../js/main.js"></script>
</body>
</html>
"""
    
    try:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_template)
        return True
    except Exception as e:
        print(f"Error creating file: {e}")
        return False

def update_html_file(html_file, content_html, blog_title):
    """Update the blog HTML file with new content and title"""
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Find the blog-container div
    blog_container = soup.find('div', class_='blog-container')
    
    if not blog_container:
        print("Error: Could not find 'blog-container' div in HTML file.")
        return False
    
    # Find and update the title (h1)
    title = blog_container.find('h1')
    if title:
        title.string = blog_title
    else:
        # Create a new h1 if it doesn't exist
        new_title = soup.new_tag('h1')
        new_title.string = blog_title
        blog_container.insert(0, new_title)
    
    # Find the date
    date = blog_container.find('p', class_='blog-date')
    
    # Clear the container
    blog_container.clear()
    
    # Add back title
    title = blog_container.find('h1')
    if not title:
        new_title = soup.new_tag('h1')
        new_title.string = blog_title
        blog_container.append(new_title)
    else:
        blog_container.append(title)
    
    # Add back date if it existed
    if date:
        blog_container.append(date)
    
    # Parse and add the new content
    new_soup = BeautifulSoup(content_html, 'html.parser')
    for element in new_soup.children:
        if element.name:  # Skip text nodes
            blog_container.append(element)
    
    # Write back to file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    
    return True

def main():
    """Main function"""
    print("=" * 50)
    print("Blog HTML Generator from Word Document")
    print("=" * 50)
    
    try:
        mode = get_user_mode()
        
        if mode == '1':
            # Create new blog
            print("\n--- Create New Blog ---")
            word_doc, html_file = get_new_blog_input()
            
            print(f"\nReading Word document: {word_doc}")
            
            # Get the blog title from the first line
            blog_title = get_blog_title_from_docx(word_doc)
            print(f"Blog title: '{blog_title}'")
            
            # Get the blog description from the second line
            blog_description = get_blog_description_from_docx(word_doc)
            print(f"Blog description: '{blog_description}'")
            
            # Extract content (skipping the first line which is the title)
            content = extract_content_from_docx(word_doc)
            
            print(f"Generating HTML content...")
            content_html = generate_html_content(content)
            
            print(f"Creating new blog file: {html_file}")
            if create_new_blog_html(html_file, content_html, blog_title):
                print("✓ New blog created successfully!")
                print(f"Created file: {html_file}")
                print(f"Blog title: '{blog_title}'")
                
                # Update blogs index
                print(f"Updating blogs index...")
                if update_blogs_index(html_file, blog_title, blog_description):
                    print("✓ Blogs index updated!")
                else:
                    print("✗ Failed to update blogs index. You may need to add it manually.")
            else:
                print("\n✗ Failed to create blog file.")
        
        else:
            # Update existing blog
            print("\n--- Update Existing Blog ---")
            word_doc, html_file = get_user_input()
            
            print(f"\nReading Word document: {word_doc}")
            
            # Get the blog title from the first line
            blog_title = get_blog_title_from_docx(word_doc)
            print(f"Blog title: '{blog_title}'")
            
            # Extract content (skipping the first line which is the title)
            content = extract_content_from_docx(word_doc)
            
            print(f"Generating HTML content...")
            content_html = generate_html_content(content)
            
            print(f"Updating blog file: {html_file}")
            if update_html_file(html_file, content_html, blog_title):
                print("✓ Blog updated successfully!")
                print(f"Updated file: {html_file}")
                print(f"Blog title: '{blog_title}'")
                
                # Update the blog title in index
                print(f"Updating blogs index...")
                if update_blog_in_index(html_file, blog_title):
                    print("✓ Blog title updated in index!")
                else:
                    print("✗ Could not update blog title in index.")
            else:
                print("\n✗ Failed to update blog file.")
    
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Make sure you have python-docx and beautifulsoup4 installed:")
        print("pip install python-docx beautifulsoup4")

if __name__ == "__main__":
    main()
