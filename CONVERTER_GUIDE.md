# LaTeX to Glossary HTML Converter

A Python script to convert LaTeX glossaries to HTML format compatible with the glossary-hovercards.js system, with automatic synonym generation.

## Requirements

- Python 3.6+
- No additional dependencies

## Usage

### Basic Usage

```bash
python tex_to_glossary.py input.tex output.html
```

### With Custom Title

```bash
python tex_to_glossary.py input.tex output.html --title "My Glossary"
```

### With Synonym File

```bash
python tex_to_glossary.py input.tex output.html --synonyms synonyms.txt
```

### Without Visible Demo (Data Only)

```bash
python tex_to_glossary.py input.tex output.html --no-demo
```

This creates an HTML file with only the hidden glossary data, no visible definitions.

## Synonym Support

The converter automatically generates plural/singular variants for each term and supports additional custom synonyms.

### Automatic Synonym Generation

The converter automatically creates synonyms for common plural/singular patterns:

- **Regular plurals**: "Action" ↔ "Actions", "Part" ↔ "Parts"
- **-ies/-y**: "Identity" ↔ "Identities"
- **-es endings**: "Process" ↔ "Processes"

Examples from your glossary:
- "Empty Part" automatically gets synonym "Empty Parts"
- "Action" automatically gets synonym "Actions"
- "Relative Identity" automatically gets synonym "Relative Identities"

### Custom Synonym File

Create a text file with comma-separated synonyms (one line per term group):

```
# synonyms.txt
Action, Actions, operation, transformation
Thing, Things, entity, object
Structure Table, Structure Tables, structural table
Empty Part, Empty Parts, null part
Relative Identity, Relative Identities, relative equality
```

Rules:
- One line per synonym group
- Comma-separated values
- One synonym must match a term in the glossary
- Lines starting with `#` are comments
- Blank lines are ignored

### How Synonyms Work

When hovering over text in a definition:
- "Actions" will show the "Action" definition
- "Empty Parts" will show the "Empty Part" definition  
- "operation" (if in synonym file) will show the "Action" definition

Synonyms are stored in the HTML as `data-synonyms` attributes:

```html
<dt class="term" data-synonyms="Actions, operation, transformation">Action</dt>
```

## Input Format

The script expects a LaTeX file with a `\begin{description}...\end{description}` environment containing glossary entries:

```latex
\begin{description}

\item[\textbf{Term Name}]
Definition text with \emph{emphasis} and $math$.
Can reference other \textbf{Terms}.

\item[\textbf{Another Term}]
Another definition with:
\begin{enumerate}
\item Numbered items
\item More items
\end{enumerate}

\end{description}
```

## Supported LaTeX Features

### Formatting
- `\textbf{Term}` → `**Term**` (for hovercards)
- `\emph{text}` → `*text*` (italics)

### Math
- Inline math: `$x = y$` → `$x = y$` (preserved)
- Display math: `\[ equation \]` → `$$equation$$`
- LaTeX commands like `\neq`, `\dagger`, `\Longleftrightarrow` are preserved

### Lists
- `\begin{enumerate}...\end{enumerate}` → `<ol>...</ol>`
- `\begin{itemize}...\end{itemize}` → `<ul>...</ul>`
- `\item` → `<li>`

### Cleaned Up
- LaTeX comments (`% ...`) are removed
- Spacing commands (`\bigskip`, etc.) are removed
- Most other LaTeX commands are stripped

## Output

The script generates a complete HTML file with:

1. **MathJax configuration** for rendering math
2. **Styled glossary** with professional typography
3. **Visible definitions** (optional) - formatted nicely for reading
4. **Hidden glossary data** - in `<dl id="glossary-data">` for hovercards
5. **Script reference** to `glossary-hovercards.js`

## Complete Example

Given `EtterMinimalGlossary.tex`:

```latex
\begin{description}

\item[\textbf{Action}]
An \emph{action} is any transformation $A$ acting on a \textbf{Structure Table}
or \textbf{Count Table}.

\item[\textbf{Structure Table}]
A table containing structural information that can be transformed by an 
\textbf{Action}.

\end{description}
```

Run:
```bash
python tex_to_glossary.py --synonyms synonyms.txt EtterMinimalGlossary.tex glossary.html --title "Tom Etter's Relation Arithmetic Glossary"
```

This creates `glossary.html` with:
- Hoverable **Action** and **Structure Table** terms
- MathJax rendering for $A$
- Recursive hovercards (hovering "Structure Table" in Action's definition shows its definition)

## Next Steps

1. Place `glossary-hovercards.js` in the same directory as your HTML file
2. Open the HTML file in a browser
3. Hover over bold terms to see definitions!

## Troubleshooting

### "No \begin{description} environment found"
The script looks for `\begin{description}...\end{description}`. Make sure your LaTeX file contains this.

### Math not rendering
Ensure you have internet connection (MathJax loads from CDN). Or download MathJax locally and update the script path.

### Terms not hoverable
Terms must be marked with `\textbf{Term}` in the LaTeX source. The script converts these to `**Term**` which the hovercards system recognizes.

## Command Line Options

```
usage: tex_to_glossary.py [-h] [--title TITLE] [--no-demo] [--synonyms SYNONYMS] input output

Convert LaTeX glossary to HTML with hovercards

positional arguments:
  input                 Input LaTeX file
  output                Output HTML file

optional arguments:
  -h, --help            show this help message and exit
  --title TITLE         Page title (default: Glossary)
  --no-demo             Do not include visible definitions in output
  --synonyms SYNONYMS   Optional synonym file (comma-separated synonyms per line)
```

## Example Workflow

```bash
# Convert LaTeX to HTML
python tex_to_glossary.py my_glossary.tex my_glossary.html --title "Physics Glossary"

# Make sure hovercards script is present
ls glossary-hovercards.js

# Open in browser
open my_glossary.html
# or
firefox my_glossary.html
```

## Customization

The generated HTML includes embedded CSS. To customize appearance:

1. Generate the HTML file
2. Edit the `<style>` section
3. Modify colors, fonts, spacing, etc.

Or extract the CSS to a separate file and link it.
