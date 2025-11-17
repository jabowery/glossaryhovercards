#!/usr/bin/env python3
"""
Convert LaTeX glossary to HTML format for glossary hovercards.

Usage:
    python tex_to_glossary.py input.tex output.html
"""

import re
import sys
import argparse
from pathlib import Path


def generate_plural_singular_synonyms(term):
    """Generate plural/singular variants of a term."""
    synonyms = []
    
    # Remove any math or special characters for analysis
    clean_term = re.sub(r'\$[^$]+\$', '', term).strip()
    
    # Check if it ends with common plural patterns
    if clean_term.endswith('ies'):
        # Identities -> Identity
        singular = clean_term[:-3] + 'y'
        synonyms.append(term.replace(clean_term, singular))
    elif clean_term.endswith('es') and len(clean_term) > 3:
        # If it ends in -es, try removing just 's' or the whole 'es'
        # Tables -> Table
        if clean_term[-3] in 'sxz' or clean_term.endswith('ches') or clean_term.endswith('shes'):
            singular = clean_term[:-2]
        else:
            singular = clean_term[:-1]
        synonyms.append(term.replace(clean_term, singular))
    elif clean_term.endswith('s') and len(clean_term) > 2:
        # Parts -> Part, Actions -> Action
        # But avoid words that naturally end in 's' (basis, analysis, etc.)
        if not clean_term.endswith('ss'):
            singular = clean_term[:-1]
            synonyms.append(term.replace(clean_term, singular))
    elif not clean_term.endswith('s'):
        # If singular, try to make plural
        if clean_term.endswith('y') and len(clean_term) > 1 and clean_term[-2] not in 'aeiou':
            # Identity -> Identities
            plural = clean_term[:-1] + 'ies'
            synonyms.append(term.replace(clean_term, plural))
        elif clean_term.endswith(('s', 'x', 'z', 'ch', 'sh')):
            # Process -> Processes
            plural = clean_term + 'es'
            synonyms.append(term.replace(clean_term, plural))
        else:
            # Action -> Actions
            plural = clean_term + 's'
            synonyms.append(term.replace(clean_term, plural))
    
    return [s for s in synonyms if s != term]


def load_synonym_file(synonym_file_path):
    """Load additional synonyms from a file.
    
    Format: one line per term, comma-separated synonyms, one of which must match the term.
    Example:
        Action, Actions, act
        Empty Part, Empty Parts
    """
    synonyms_dict = {}
    
    if not synonym_file_path or not Path(synonym_file_path).exists():
        return synonyms_dict
    
    with open(synonym_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 2:
                continue
            
            # All parts are synonyms of each other
            # Store each as a list of all the others
            for term in parts:
                if term:
                    # Remove the term itself from its synonym list
                    term_synonyms = [p for p in parts if p != term]
                    if term in synonyms_dict:
                        synonyms_dict[term].extend(term_synonyms)
                    else:
                        synonyms_dict[term] = term_synonyms
    
    return synonyms_dict


def extract_term_name(item_line):
    r"""Extract term name from \item[\textbf{Term}] or \item[\textbf{Term} $math$] etc."""
    # Match \item[\textbf{Term}...] where ... can be anything until ]
    # We want just the term inside \textbf{...}
    match = re.search(r'\\item\[\\textbf\{([^}]+)\}', item_line)
    if match:
        term = match.group(1)
        # Clean up any remaining LaTeX in the term name (shouldn't be any, but just in case)
        term = re.sub(r'\$[^$]+\$', '', term)  # Remove any math
        return term.strip()
    return None


def convert_latex_to_html(text):
    """Convert LaTeX formatting to HTML with glossary term markup."""
    
    # Remove LaTeX comments (lines starting with %)
    text = re.sub(r'^%.*$', '', text, flags=re.MULTILINE)
    
    # Convert \textbf{Term} to **Term** for hovercard processing
    text = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', text)
    
    # Convert \emph{text} to *text*
    text = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', text)
    
    # Handle display math \[ ... \]
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    
    # Inline math $...$ stays as is
    
    # Convert \neq to \neq (already LaTeX compatible)
    # Convert other common LaTeX commands
    text = text.replace(r'\neq', r'\neq')
    text = text.replace(r'\dagger', r'\dagger')
    text = text.replace(r'\Longleftrightarrow', r'\Longleftrightarrow')
    
    # Remove \bigskip, \medskip, etc.
    text = re.sub(r'\\(big|med|small)skip', '', text)
    
    # Convert itemize/enumerate to HTML
    text = re.sub(r'\\begin\{enumerate\}', '<ol>', text)
    text = re.sub(r'\\end\{enumerate\}', '</ol>', text)
    text = re.sub(r'\\begin\{itemize\}', '<ul>', text)
    text = re.sub(r'\\end\{itemize\}', '</ul>', text)
    text = re.sub(r'\\item\s+', '<li>', text)
    
    # Close list items properly
    text = re.sub(r'<li>([^<]*?)(?=<li>|</[ou]l>)', r'<li>\1</li>', text, flags=re.DOTALL)
    
    # Remove remaining LaTeX commands that we don't need
    text = re.sub(r'\\[a-zA-Z]+\*?\s*', '', text)
    
    # Remove book-keeping (discretionary hyphen in "book\-keeping")
    text = text.replace(r'\-', '')
    
    # Clean up extra whitespace and blank lines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
    
    return text.strip()


def parse_latex_glossary(latex_content, synonym_file=None):
    """Parse LaTeX glossary and extract term definitions with synonyms."""
    
    # Load additional synonyms from file
    file_synonyms = load_synonym_file(synonym_file)
    
    # Find the description environment
    desc_match = re.search(
        r'\\begin\{description\}(.*?)\\end\{description\}',
        latex_content,
        re.DOTALL
    )
    
    if not desc_match:
        raise ValueError("No \\begin{description} environment found")
    
    desc_content = desc_match.group(1)
    
    # Split into items
    # Look for \item[\textbf{...}]
    items = re.split(r'(?=\\item\[\\textbf\{)', desc_content)
    
    glossary = []
    
    for item in items:
        if not item.strip() or not item.strip().startswith(r'\item'):
            continue
        
        # Split into lines
        lines = item.split('\n', 1)
        if len(lines) < 2:
            continue
        
        term_line = lines[0]
        definition_text = lines[1] if len(lines) > 1 else ""
        
        # Extract term name
        term = extract_term_name(term_line)
        if not term:
            continue
        
        # Get definition text (everything until next \item or end)
        definition = definition_text.strip()
        
        # Convert LaTeX to HTML
        definition_html = convert_latex_to_html(definition)
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in definition_html.split('\n\n') if p.strip()]
        
        # Generate synonyms
        synonyms = []
        
        # Add auto-generated plural/singular
        auto_synonyms = generate_plural_singular_synonyms(term)
        synonyms.extend(auto_synonyms)
        
        # Add synonyms from file
        if term in file_synonyms:
            synonyms.extend(file_synonyms[term])
        
        # Remove duplicates and the term itself
        synonyms = list(set(s for s in synonyms if s.lower() != term.lower()))
        
        glossary.append({
            'term': term,
            'paragraphs': paragraphs,
            'synonyms': synonyms
        })
    
    return glossary


def generate_html(glossary, title="Glossary", include_demo=True):
    """Generate complete HTML file with glossary hovercards."""
    
    # Generate glossary data (hidden)
    glossary_data_html = '<dl id="glossary-data" style="display: none;">\n'
    for entry in glossary:
        synonyms_attr = ''
        if entry['synonyms']:
            synonyms_str = ', '.join(entry['synonyms'])
            synonyms_attr = f' data-synonyms="{synonyms_str}"'
        
        glossary_data_html += f'  <dt class="term"{synonyms_attr}>{entry["term"]}</dt>\n'
        glossary_data_html += '  <dd class="definition">\n'
        for para in entry['paragraphs']:
            glossary_data_html += f'    <p>{para}</p>\n'
        glossary_data_html += '  </dd>\n'
        glossary_data_html += '\n'
    glossary_data_html += '</dl>'
    
    # Generate visible definitions (optional demo)
    visible_html = ''
    if include_demo:
        visible_html = '<div class="content">\n'
        visible_html += '  <h2>Glossary Definitions</h2>\n'
        visible_html += '  <p class="note">Hover over <strong>bold terms</strong> to see their definitions.</p>\n'
        visible_html += '  <dl>\n'
        for entry in glossary:
            visible_html += f'    <dt class="term">{entry["term"]}</dt>\n'
            visible_html += '    <dd class="definition">\n'
            for para in entry['paragraphs']:
                visible_html += f'      <p>{para}</p>\n'
            visible_html += '    </dd>\n'
            visible_html += '\n'
        visible_html += '  </dl>\n'
        visible_html += '</div>\n'
    
    # Complete HTML document
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  
  <!-- MathJax Configuration -->
  <script>
    MathJax = {{
      tex: {{
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
        processEscapes: true,
        processEnvironments: true
      }},
      options: {{
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
      }}
    }};
  </script>
  
  <!-- MathJax for rendering mathematical expressions -->
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  
  <style>
    body {{
      font-family: Georgia, serif;
      max-width: 900px;
      margin: 40px auto;
      padding: 0 20px;
      line-height: 1.6;
      color: #333;
    }}
    
    h1 {{
      color: #222;
      border-bottom: 3px solid #333;
      padding-bottom: 10px;
      margin-bottom: 30px;
    }}
    
    h2 {{
      color: #444;
      margin-top: 40px;
      margin-bottom: 20px;
    }}
    
    .note {{
      background: #f0f0f0;
      padding: 15px;
      border-left: 4px solid #666;
      margin: 20px 0;
      font-style: italic;
    }}
    
    dt.term {{
      font-weight: bold;
      margin-top: 30px;
      font-size: 18px;
      color: #222;
    }}
    
    dd.definition {{
      margin-left: 20px;
      margin-top: 10px;
      margin-bottom: 20px;
    }}
    
    dd.definition p {{
      margin: 12px 0;
    }}
    
    dd.definition ol, dd.definition ul {{
      margin: 10px 0;
      padding-left: 30px;
    }}
    
    dd.definition li {{
      margin: 8px 0;
    }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  
  {visible_html}
  
  <!-- Hidden glossary data (loaded by glossary-hovercards.js) -->
  {glossary_data_html}
  
  <!-- Load the glossary hovercards module -->
  <script src="glossary-hovercards.js"></script>
</body>
</html>
'''
    
    return html


def main():
    parser = argparse.ArgumentParser(
        description='Convert LaTeX glossary to HTML with hovercards'
    )
    parser.add_argument(
        'input',
        help='Input LaTeX file'
    )
    parser.add_argument(
        'output',
        help='Output HTML file'
    )
    parser.add_argument(
        '--title',
        default='Glossary',
        help='Page title (default: Glossary)'
    )
    parser.add_argument(
        '--no-demo',
        action='store_true',
        help='Do not include visible definitions in output'
    )
    parser.add_argument(
        '--synonyms',
        help='Optional synonym file (comma-separated synonyms per line)'
    )
    
    args = parser.parse_args()
    
    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Reading {args.input}...")
    latex_content = input_path.read_text(encoding='utf-8')
    
    # Parse glossary
    print("Parsing glossary terms...")
    try:
        glossary = parse_latex_glossary(latex_content, args.synonyms)
        print(f"Found {len(glossary)} terms")
        
        # Show synonyms if verbose
        total_synonyms = sum(len(entry['synonyms']) for entry in glossary)
        print(f"Generated {total_synonyms} synonyms")
        
    except Exception as e:
        print(f"Error parsing LaTeX: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate HTML
    print("Generating HTML...")
    html = generate_html(
        glossary,
        title=args.title,
        include_demo=not args.no_demo
    )
    
    # Write output
    output_path = Path(args.output)
    output_path.write_text(html, encoding='utf-8')
    print(f"Wrote {args.output}")
    print("\nDon't forget to place glossary-hovercards.js in the same directory!")


if __name__ == '__main__':
    main()
