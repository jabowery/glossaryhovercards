# Glossary Hovercards

A lightweight, recursive glossary system with hovercards and mathematical expression rendering. Hover over terms to see their definitions, with full support for nested definitions and LaTeX math rendering.

## Features

- **Recursive Hovercards**: Definitions can contain terms that trigger their own hovercards, creating a stack of definitions
- **Smart Positioning**: Hovercards appear covering the term they define, eliminating the "gap problem" where hovercards disappear before you can reach them
- **Intelligent Hiding**: Each hovercard disappears only when the mouse leaves it AND there are no hovercards above it in the stack
- **Math Rendering**: Automatic LaTeX math rendering via MathJax for inline (`$...$`) and display (`$$...$$`) equations
- **Zero Dependencies**: Pure JavaScript (except MathJax for math rendering)
- **Automatic Processing**: Automatically finds and processes terms marked with `**term**` syntax

## Installation

### 1. Include MathJax (for math rendering)

Add this to your HTML `<head>`:

```html
<!-- MathJax Configuration -->
<script>
  MathJax = {
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      processEscapes: true,
      processEnvironments: true
    },
    options: {
      skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
    }
  };
</script>

<!-- MathJax Library -->
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```

### 2. Include the Glossary Hovercards Module

```html
<script src="glossary-hovercards.js"></script>
```

## Usage

### Basic Setup

1. **Create your glossary data** in a hidden `<dl>` element with `id="glossary-data"`:

```html
<dl id="glossary-data" style="display: none;">
  <dt class="term">Action</dt>
  <dd class="definition">
    <p>An *action* is any transformation $A$ acting on a **Structure Table**
    or **Count Table** that satisfies certain properties.</p>
  </dd>
  
  <dt class="term">Structure Table</dt>
  <dd class="definition">
    <p>A table containing structural information that can be transformed 
    by an **Action**.</p>
  </dd>
  
  <dt class="term">Count Table</dt>
  <dd class="definition">
    <p>A table containing count data.</p>
  </dd>
</dl>
```

2. **Mark terms in your content** using `**term**` syntax:

```html
<dl>
  <dt class="term">Thing</dt>
  <dd class="definition">
    <p>A *thing* is anything transformed non-trivially by some **Action**.
    Formally: $t$ is a thing iff there exists an action $A$ with 
    $A(t) \neq A(0)$ under the induced **Relative Identity**.</p>
  </dd>
</dl>
```

3. **Initialize** (happens automatically when the script loads):

```javascript
// The module auto-initializes on page load
// Access the instance via: window.glossaryHovercards
```

### HTML Structure Requirements

#### Glossary Data Element

The glossary data must be in a `<dl>` element with `id="glossary-data"`:

```html
<dl id="glossary-data" style="display: none;">
  <dt class="term">Term Name</dt>
  <dd class="definition">
    <p>Definition with **Other Terms** and math $x = y$.</p>
  </dd>
</dl>
```

- **`<dt class="term">`**: Contains the term name (case-insensitive matching)
- **`<dd class="definition">`**: Contains the definition HTML
- **Hidden**: The glossary data element should be hidden (`display: none`)

#### Term Markup

Mark hoverable terms using double asterisks:

```html
<p>This concept relates to **Action** and **Thing**.</p>
```

Terms are case-insensitive when matching to definitions.

### Mathematical Expressions

Use standard LaTeX syntax within dollar signs:

- **Inline math**: `$A^2 = A$` → $A^2 = A$
- **Display math**: `$$\int_0^\infty e^{-x} dx = 1$$`
- **Special characters**: `$A(t) \neq A(0)$` → $A(t) \neq A(0)$

## Configuration

You can customize behavior by passing options to the constructor:

```javascript
window.glossaryHovercards = new GlossaryHovercards({
  hoverDelay: 300,  // Delay in ms before showing hovercard (default: 300)
  hideDelay: 200    // Delay in ms before hiding hovercard (default: 200)
});
```

## How It Works

### Recursive Hovercards

When you hover over a term:
1. A hovercard appears with the term's definition
2. If the definition contains other terms marked with `**term**`, they are also hoverable
3. Hovering over a nested term creates a new hovercard on top of the previous one
4. Hovercards stack with proper z-indexing

### Smart Positioning

Hovercards are positioned to **cover the term that triggered them**:
- The top of the hovercard overlaps slightly with the term
- Horizontally centered on the mouse pointer
- This eliminates gaps, preventing the "cruel dilemma" where hovercards disappear before you can reach them

### Intelligent Hiding

A hovercard disappears when BOTH conditions are met:
1. The mouse pointer is NOT on that hovercard, AND
2. There are NO hovercards above it in the stack

This means:
- You can freely move between hovercards without them disappearing
- Top-level hovercards disappear immediately when you move off them
- Lower hovercards stay visible as long as there are hovercards above them

## Complete Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>My Glossary</title>
  
  <!-- MathJax Configuration -->
  <script>
    MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: true,
        processEnvironments: true
      }
    };
  </script>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  
  <style>
    body {
      font-family: Georgia, serif;
      max-width: 800px;
      margin: 40px auto;
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <h1>Mathematical Definitions</h1>
  
  <dl>
    <dt class="term">Group</dt>
    <dd class="definition">
      <p>A **Set** with a binary **Operation** satisfying associativity,
      identity, and inverse properties.</p>
    </dd>
  </dl>
  
  <!-- Hidden glossary data -->
  <dl id="glossary-data" style="display: none;">
    <dt class="term">Set</dt>
    <dd class="definition">
      <p>A collection of distinct objects, denoted $S = \{x_1, x_2, \ldots\}$.</p>
    </dd>
    
    <dt class="term">Operation</dt>
    <dd class="definition">
      <p>A function $\circ: S \times S \to S$ that combines two elements
      of a **Set** to produce another element.</p>
    </dd>
  </dl>
  
  <script src="glossary-hovercards.js"></script>
</body>
</html>
```

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires ES6+ support (arrow functions, template literals, etc.)
- MathJax 3.x or 2.x for math rendering

## Styling

The module injects default styles, but you can override them:

```css
.glossary-term {
  /* Style for hoverable terms */
  font-weight: bold;
  border-bottom: 1px dotted #666;
  cursor: help;
}

.glossary-hovercard {
  /* Style for hovercard container */
  background: white;
  border: 2px solid #333;
  border-radius: 6px;
  max-width: 400px;
}

.glossary-hovercard-title {
  /* Style for term title in hovercard */
  font-weight: bold;
  font-size: 16px;
}

.glossary-hovercard-content {
  /* Style for definition content */
  color: #444;
}
```

## API Reference

### Constructor

```javascript
new GlossaryHovercards(options)
```

**Parameters:**
- `options.hoverDelay` (number): Milliseconds before showing hovercard (default: 300)
- `options.hideDelay` (number): Milliseconds before hiding hovercard (default: 200)

### Instance Properties

- `glossaryHovercards.glossaryData` (Map): Internal glossary term storage
- `glossaryHovercards.hovercardStack` (Array): Current stack of visible hovercards

### Methods

Generally, you don't need to call methods directly. The module handles everything automatically.

## Design Philosophy

This library was designed to solve a fundamental UX problem with hovercards: the gap between the trigger and the hovercard. Traditional implementations position hovercards offset from the trigger, creating a gap that causes the hovercard to disappear when you try to move your mouse to it.

Our solution:
1. **Cover the trigger**: Position the hovercard to overlap the term that triggered it
2. **Continuous hover area**: No gap means the mouse stays in a hover-sensitive area
3. **Smart stacking**: Recursive hovercards work naturally with proper z-indexing
4. **Independent hiding**: Each hovercard manages its own visibility based on the stack

This should have been a web standard from the beginning!

## License

MIT License - Feel free to use in your projects.

## Contributing

This is a single-file library designed for simplicity. Contributions welcome for:
- Bug fixes
- Performance improvements
- Additional configuration options
- Better accessibility support

## Acknowledgments

Built to solve the "cruel dilemma" of disappearing hovercards in mathematical and technical documentation.
