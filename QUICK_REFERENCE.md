# Glossary Hovercards - Quick Reference

## Installation

```bash
# Include in your HTML <head>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

# Include before </body>
<script src="glossary-hovercards.js"></script>
```

## Convert LaTeX to HTML

```bash
# Basic
python tex_to_glossary.py input.tex output.html

# With title
python tex_to_glossary.py input.tex output.html --title "My Glossary"

# With custom synonyms
python tex_to_glossary.py input.tex output.html --synonyms synonyms.txt

# Data only (no visible demo)
python tex_to_glossary.py input.tex output.html --no-demo
```

## HTML Structure

```html
<!-- Hidden glossary data -->
<dl id="glossary-data" style="display: none;">
  <dt class="term" data-synonyms="Actions, operation">Action</dt>
  <dd class="definition">
    <p>Definition with **Other Terms** and $math$.</p>
  </dd>
</dl>

<!-- Visible content -->
<p>An **Action** transforms things.</p>
```

## Synonym File Format

```
# synonyms.txt
Action, Actions, operation, transformation
Thing, Things, entity
Empty Part, Empty Parts, null part
```

Rules:
- Comma-separated
- One line per group
- `#` for comments
- One must match glossary term

## Automatic Synonyms

Generated automatically for:
- Regular plurals: Part → Parts
- -ies/-y: Identity → Identities  
- -es: Process → Processes

## Mark Terms in Content

```html
<!-- Use **term** for hoverable terms -->
<p>An **Action** operates on a **Structure Table**.</p>
```

## Math Expressions

```html
<!-- Inline math -->
$A^2 = A$

<!-- Display math -->
$$\int_0^\infty e^{-x}dx$$
```

## Behavior

**Show hovercard:** Hover term for 300ms  
**Hide hovercard:** Leave term AND no cards above it  
**Recursive:** Hover terms in hovercards  
**Case-insensitive:** "Action" = "action" = "ACTION"

## Customization

```javascript
window.glossaryHovercards = new GlossaryHovercards({
  hoverDelay: 300,  // ms before showing
  hideDelay: 200    // ms before hiding
});
```

## CSS Classes

Override these for custom styling:

```css
.glossary-term              /* Hoverable terms */
.glossary-hovercard         /* Hovercard container */
.glossary-hovercard-title   /* Term title */
.glossary-hovercard-content /* Definition */
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Terms not hoverable | Check `**term**` markup |
| Math not rendering | Verify MathJax loaded |
| Synonym not working | Check `data-synonyms` attribute |
| Hovercard positioning | Check term overlap |

## Files Included

- `glossary-hovercards.js` - Main library
- `tex_to_glossary.py` - LaTeX converter
- `README.md` - Full documentation
- `CONVERTER_GUIDE.md` - Converter guide
- `SYNONYM_GUIDE.md` - Synonym details
- `example_synonyms.txt` - Template
- `demo.html` - Working example
- `synonym-test.html` - Test file

## Quick Test

```bash
# Open test file
open synonym-test.html

# Verify:
# - "Actions" shows "Action" definition ✓
# - "Things" shows "Thing" definition ✓
# - Hovercards stack ✓
# - Math renders ✓
```

## Common Patterns

### LaTeX Input
```latex
\item[\textbf{Action}]
An \emph{action} is a transformation $A$ on a \textbf{Structure Table}.
```

### Generated HTML
```html
<dt class="term" data-synonyms="Actions">Action</dt>
<dd class="definition">
  <p>An *action* is a transformation $A$ on a **Structure Table**.</p>
</dd>
```

### Result
- "Action" → shows definition
- "Actions" → shows definition (synonym)
- "action" → shows definition (case-insensitive)

## Best Practices

✅ **DO:**
- Use synonyms for plural/singular
- Include common alternatives
- Test in browser after generating
- Keep synonym lists focused

❌ **DON'T:**
- Add too many synonyms
- Forget to copy .js file
- Skip testing synonym matches
- Use exact quotes from LaTeX

## Support

Check documentation:
- `README.md` - Usage & API
- `CONVERTER_GUIDE.md` - LaTeX conversion
- `SYNONYM_GUIDE.md` - Synonym details
- `FINAL_SUMMARY.md` - Complete overview

## License

MIT - Use freely!

---

**One-line summary:** Interactive glossaries with recursive hovercards, math rendering, and automatic synonym support.
