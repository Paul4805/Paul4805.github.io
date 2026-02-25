import os
from pathlib import Path
from datetime import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom

# Try to import docx library for Word document support
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Configuration
BLOGS_DIR = Path(__file__).parent / "blogs"
BLOG_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>{title} | J Paul Masillamani</title>
    <link rel="preconnect" href="https://fonts.googleapis.com"/>
    <link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
    <link href="https://fonts.googleapis.com/css2?family=Nothing+You+Could+Do&family=Inter:wght@300;400;600&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet"/>
    <link href="../css/blog_post_style.css" rel="stylesheet"/>
</head>
<body class="blog-post-page">

    <nav class="navbar">
        <a href="../index.html">Home</a>
        <a href="index.html">Back to Blogs</a>
    </nav>

    <main class="blog-container">
        <article class="glass-card">
            <header class="post-header">
                <h1 class="post-title">{title}</h1>
                <p class="blog-date">{date}</p>
            </header>

            <div class="blog-content">
{content}
            </div>
            
            <footer class="post-footer">
                <a href="index.html" class="back-link">← Back to all stories</a>
            </footer>
        </article>
    </main>

</body>
</html>"""

def read_markdown_file(file_path):
    """Read markdown/text/docx file and convert to HTML paragraphs.
    Lines/paragraphs with ALL BOLD characters are treated as subtopics (h3 headings).
    """
    file_path = Path(file_path)
    file_ext = file_path.suffix.lower()
    
    # Handle Word documents (.docx)
    if file_ext == '.docx':
        if not DOCX_AVAILABLE:
            print("Error: To read .docx files, install python-docx:")
            print("  pip install python-docx")
            return None
        
        try:
            doc = Document(file_path)
            html_content = []
            first_para = True
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                
                # Check if all runs in this paragraph are bold
                is_all_bold = all(run.bold for run in para.runs if run.text.strip())
                
                if is_all_bold and any(run.text.strip() for run in para.runs):
                    # Treat as subtopic heading
                    html_content.append(f'                <h3 class="blog-subtitle">{text}</h3>')
                elif first_para:
                    # First paragraph is lead
                    html_content.append(f'                <p class="lead">\n                    {text}\n                </p>')
                    first_para = False
                else:
                    # Regular paragraph
                    html_content.append(f'                <p>\n                    {text}\n                </p>')
            
            return '\n                \n'.join(html_content)
        except Exception as e:
            print(f"Error reading Word document: {e}")
            return None
    
    # Handle plain text and markdown files
    elif file_ext in ['.txt', '.md', '.markdown']:
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read().strip()
                break
            except (UnicodeDecodeError, LookupError):
                continue
        
        if content is None:
            print(f"Error: Could not read file '{file_path}' with any supported encoding.")
            return None
        
        try:
            # Split by double newlines to identify paragraphs
            paragraphs = content.split('\n\n')
            html_content = []
            first_para = True
            
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                # Check if line is all bold (markdown syntax: **text** or __text__)
                # Remove markdown bold markers and check if that's all there is
                clean_para = para.replace('**', '').replace('__', '')
                is_bold_line = (
                    para.startswith('**') and para.endswith('**') and len(para) > 4 and
                    '**' not in clean_para
                ) or (
                    para.startswith('__') and para.endswith('__') and len(para) > 4 and
                    '__' not in clean_para
                )
                
                if is_bold_line:
                    # Remove markdown bold markers and create heading
                    heading_text = para.replace('**', '').replace('__', '')
                    html_content.append(f'                <h3 class="blog-subtitle">{heading_text}</h3>')
                elif first_para:
                    # First paragraph is lead
                    html_content.append(f'                <p class="lead">\n                    {para}\n                </p>')
                    first_para = False
                else:
                    # Regular paragraph
                    html_content.append(f'                <p>\n                    {para}\n                </p>')
            
            return '\n                \n'.join(html_content)
        except Exception as e:
            print(f"Error processing file: {e}")
            return None
    
    else:
        print(f"Error: Unsupported file type '{file_ext}'")
        print("Supported file types: .txt, .md, .markdown, .docx")
        return None

def create_blog_html(filename, title, content_html, date=None):
    """Create a new blog HTML file."""
    if date is None:
        date = datetime.now().strftime("%B %Y")
    
    html_content = BLOG_TEMPLATE.format(
        title=title,
        date=date,
        content=content_html
    )
    
    file_path = BLOGS_DIR / filename
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ Blog created: {file_path}")
        return True
    except Exception as e:
        print(f"Error creating blog file: {e}")
        return False

def update_blog_html(file_path, title, content_html, date=None):
    """Update an existing blog HTML file."""
    if date is None:
        date = datetime.now().strftime("%B %Y")
    
    html_content = BLOG_TEMPLATE.format(
        title=title,
        date=date,
        content=content_html
    )
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ Blog updated: {file_path}")
        return True
    except Exception as e:
        print(f"Error updating blog file: {e}")
        return False

def add_to_blog_index(filename, title, description):
    """Add a blog entry to the blogs/index.html file."""
    index_path = BLOGS_DIR / "index.html"
    
    if not index_path.exists():
        print(f"Error: {index_path} not found.")
        return False
    
    # Read the current index file
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading index file: {e}")
        return False
    
    # Create the blog card HTML
    blog_card = f"""     <a class="blog-card" href="{filename}">
      <h3>
       {title}
      </h3>
      <p>
       {description}
      </p>
      <span class="read-more">
       Read Entry →
      </span>
     </a>
"""
    
    # Find the blog-list div and insert the new card
    blog_list_end = content.find('    </div>\n   </div>')
    
    if blog_list_end == -1:
        print("Error: Could not find blog-list div in index.html")
        return False
    
    # Check if blog already exists in index
    if f'href="{filename}"' in content:
        # Update existing entry
        import re
        pattern = rf'<a class="blog-card" href="{re.escape(filename)}">\s*<h3>\s*[^<]+\s*</h3>\s*<p>\s*[^<]+\s*</p>\s*<span class="read-more">\s*Read Entry →\s*</span>\s*</a>'
        if re.search(pattern, content):
            content = re.sub(pattern, blog_card.rstrip(), content)
            print(f"✓ Index updated: {filename}")
        else:
            print("Warning: Could not find existing entry for update.")
            return False
    else:
        # Insert new entry
        closing_divs = '    </div>\n   </div>'
        new_content = content[:blog_list_end] + '\n' + blog_card + closing_divs + content[blog_list_end + len(closing_divs):]
        content = new_content
        print(f"✓ Index updated: Added {filename}")
    
    # Write back to index file
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing to index file: {e}")
        return False

def main():
    """Main function to handle user interaction."""
    print("\n" + "="*60)
    print("      BLOG UPDATER - Manage Your Blog Posts")
    print("="*60 + "\n")
    
    # Step 1: Ask user if they want to update or create
    while True:
        print("What would you like to do?")
        print("1. Update existing blog")
        print("2. Create new blog from scratch")
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice in ['1', '2']:
            break
        print("Invalid choice. Please enter 1 or 2.\n")
    
    if choice == '1':
        update_blog()
    else:
        create_new_blog()

def update_blog():
    """Handle updating an existing blog."""
    print("\n" + "-"*60)
    print("UPDATE EXISTING BLOG")
    print("-"*60 + "\n")
    
    # Get HTML file path
    while True:
        html_file = input("Enter the path to the HTML file to update (e.g., blogs/blog1.html): ").strip()
        html_path = Path(html_file)
        
        if not html_path.exists():
            print(f"Error: File '{html_file}' not found. Try again.\n")
            continue
        break
    
    # Get doc file path
    while True:
        doc_file = input("Enter the path to the document file (e.g., docs/blog1.md or docs/blog1.txt): ").strip()
        doc_path = Path(doc_file)
        
        if not doc_path.exists():
            print(f"Error: File '{doc_file}' not found. Try again.\n")
            continue
        break
    
    # Get blog title
    title = input("Enter the blog title: ").strip()
    if not title:
        print("Error: Title cannot be empty.")
        return
    
    # Ask for date (optional)
    date_input = input("Enter the date (optional, format: Month Year, e.g., 'February 2026'): ").strip()
    date = date_input if date_input else datetime.now().strftime("%B %Y")
    
    # Read and convert content
    content_html = read_markdown_file(doc_path)
    if content_html is None:
        return
    
    # Update the blog HTML file
    if update_blog_html(html_path, title, content_html, date):
        print("\n✓ Blog updated successfully!")
    else:
        print("\n✗ Failed to update blog.")

def create_new_blog():
    """Handle creating a new blog from scratch."""
    print("\n" + "-"*60)
    print("CREATE NEW BLOG")
    print("-"*60 + "\n")
    
    # Get new filename
    while True:
        filename = input("Enter the new HTML filename (e.g., blog2.html): ").strip()
        
        if not filename.endswith('.html'):
            filename += '.html'
        
        file_path = BLOGS_DIR / filename
        
        if file_path.exists():
            overwrite = input(f"File '{filename}' already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite == 'y':
                break
            else:
                continue
        else:
            break
    
    # Get doc file path
    while True:
        doc_file = input("Enter the path to the document file (e.g., docs/blog2.md or docs/blog2.txt): ").strip()
        doc_path = Path(doc_file)
        
        if not doc_path.exists():
            print(f"Error: File '{doc_file}' not found. Try again.\n")
            continue
        break
    
    # Get blog title
    title = input("Enter the blog title: ").strip()
    if not title:
        print("Error: Title cannot be empty.")
        return
    
    # Ask for date (optional)
    date_input = input("Enter the date (optional, format: Month Year, e.g., 'February 2026'): ").strip()
    date = date_input if date_input else datetime.now().strftime("%B %Y")
    
    # Get blog description for index
    description = input("Enter a brief description for the blog listing (1-2 sentences): ").strip()
    if not description:
        print("Error: Description cannot be empty.")
        return
    
    # Read and convert content
    content_html = read_markdown_file(doc_path)
    if content_html is None:
        return
    
    # Create the blog HTML file
    if create_blog_html(filename, title, content_html, date):
        # Add to index.html
        if add_to_blog_index(filename, title, description):
            print("\n✓ Blog created and added to index successfully!")
        else:
            print("\n⚠ Blog created but failed to add to index.")
    else:
        print("\n✗ Failed to create blog.")

if __name__ == "__main__":
    main()
