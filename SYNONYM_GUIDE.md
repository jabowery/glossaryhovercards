# Synonym Support in Glossary Hovercards

The glossary hovercard system now supports synonyms, allowing multiple variations of a term to trigger the same definition.

## Why Synonyms?

In technical writing, terms often appear in different forms:
- **Plural vs Singular**: "Action" / "Actions", "Empty Part" / "Empty Parts"
- **Alternative names**: "discriminator" / "discriminating action"
- **Abbreviations**: "GA" / "Geometric Algebra"
- **Case variations**: "action" / "Action"

Without synonym support, hovering over "Actions" wouldn't show the "Action" definition. Now it does!

## How It Works

### In the HTML

Synonyms are specified in the `data-synonyms` attribute of term definitions:

```html
<dl id="glossary-data" style="display: none;">
  <dt class="term" data-synonyms="Actions, operation, transformation">Action</dt>
  <dd class="definition">
    <p>Definition of action...</p>
  </dd>
</dl>
```

### Lookup Behavior

When you hover over a term in a definition:
1. The system extracts the term text (e.g., "Actions")
2. Converts it to lowercase for matching
3. Checks if it matches:
   - The main term name ("action")
   - Any synonym in the `data-synonyms` list
4. If found, displays the definition

All matching is **case-insensitive**.

## Using the Python Converter

### Automatic Synonym Generation

The `tex_to_glossary.py` script automatically generates plural/singular variants:

```bash
python tex_to_glossary.py input.tex output.html
```

Automatically creates:
- "Action" → "Actions"
- "Empty Part" → "Empty Parts"  
- "Identity" → "Identities"
- "Process" → "Processes"

### Custom Synonyms

Create a synonym file with additional variations:

**synonyms.txt:**
```
Action, Actions, operation, transformation
Thing, Things, entity, object
Discriminator, Discriminators, discriminating action
Empty Part, Empty Parts, null part, void component
```

Then use it:
```bash
python tex_to_glossary.py input.tex output.html --synonyms synonyms.txt
```

### Synonym File Format

- One line per synonym group
- Comma-separated values
- At least one synonym must match a term in the glossary
- Comments start with `#`
- Blank lines ignored

Example:
```
# Core concepts
Action, Actions, operation
Thing, entity, object

# Special cases  
World of a Discriminator, discriminator world, World(x)
```

## Examples

### Example 1: Plural/Singular

**LaTeX:**
```latex
\item[\textbf{Empty Part}]
A component that cancels out.
```

**Generated HTML:**
```html
<dt class="term" data-synonyms="Empty Parts">Empty Part</dt>
```

**Result:** Both "Empty Part" and "Empty Parts" show the same definition.

### Example 2: Multiple Synonyms

**Synonym file:**
```
Action, Actions, operation, transformation, operator
```

**Generated HTML:**
```html
<dt class="term" data-synonyms="Actions, operation, transformation, operator">Action</dt>
```

**Result:** All five terms show the "Action" definition.

### Example 3: Cross-References

```html
<dl id="glossary-data" style="display: none;">
  <dt class="term" data-synonyms="Things">Thing</dt>
  <dd class="definition">
    <p>A **Thing** is transformed by **Actions**.</p>
  </dd>
  
  <dt class="term" data-synonyms="Actions">Action</dt>
  <dd class="definition">
    <p>An **Action** operates on **Things**.</p>
  </dd>
</dl>
```

**Result:** 
- Hovering "Thing" or "Things" works
- Hovering "Action" or "Actions" works
- Cross-references work with both forms

## Implementation Details

### JavaScript (glossary-hovercards.js)

The `loadGlossaryData()` function:
1. Reads each term and its `data-synonyms` attribute
2. Creates a Map with multiple keys pointing to the same definition
3. Main term → definition
4. Each synonym → same definition

```javascript
// Stores under main term
this.glossaryData.set('action', entry);

// Stores under each synonym
this.glossaryData.set('actions', entry);
this.glossaryData.set('operation', entry);
```

### Python Converter (tex_to_glossary.py)

The converter has three functions:

**1. `generate_plural_singular_synonyms(term)`**
- Analyzes term endings
- Generates plural from singular or vice versa
- Handles: -s, -es, -ies patterns

**2. `load_synonym_file(path)`**
- Reads synonym file
- Parses comma-separated values
- Returns dictionary of term → synonyms

**3. `parse_latex_glossary(content, synonym_file)`**
- Combines automatic + file synonyms
- Removes duplicates
- Stores in glossary data structure

## Testing

Use `synonym-test.html` to verify functionality:

```bash
# Open test file
open synonym-test.html

# Test cases:
# - Hover "Actions" (plural)
# - Hover "actions" (lowercase)
# - Hover "Things" (plural)
# - Hover "Empty Parts" (plural)
```

All should show the correct definition.

## Best Practices

### 1. Always Include Plural/Singular
```
Empty Part, Empty Parts
```

### 2. Add Common Alternatives
```
Action, Actions, operation, transformation
```

### 3. Include Abbreviations
```
Geometric Algebra, GA
```

### 4. Don't Overdo It
Too many synonyms can be confusing. Focus on:
- Natural variations users will encounter
- Common terminology in your field
- Plural/singular forms

### 5. Test Your Synonyms
After generating HTML:
1. Open in browser
2. Try hovering different forms
3. Verify all variations work

## Troubleshooting

### Synonym Not Working

**Problem:** Hovering "Actions" doesn't show definition

**Checklist:**
1. Is `data-synonyms="Actions"` in the `<dt>` tag?
2. Is the term marked with `**Actions**` in the definition?
3. Is the glossary-hovercards.js script loaded?
4. Check browser console for errors

### Case Sensitivity

**Problem:** "ACTION" doesn't work but "Action" does

**Solution:** All matching is case-insensitive. This should work automatically. If not, check that the term is properly marked with `**ACTION**`.

### Synonym File Not Applied

**Problem:** Custom synonyms not appearing

**Checklist:**
1. Did you use `--synonyms` flag?
2. Is the path to synonym file correct?
3. Does at least one synonym match a term?
4. Check for syntax errors in synonym file

## Performance

Synonyms have minimal performance impact:
- Stored as additional Map entries
- Lookup is O(1) - same speed as without synonyms
- No runtime overhead for synonym resolution

## Future Enhancements

Possible improvements:
- Fuzzy matching for misspellings
- Automatic abbreviation detection
- Multi-language synonym support
- Regular expression patterns

---

**This feature makes the glossary system truly practical for technical documentation where terminology naturally varies!**
