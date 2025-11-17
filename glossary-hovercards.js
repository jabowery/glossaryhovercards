/**
 * Glossary Hovercards Module
 * Provides recursive hovercards for glossary terms with MathJax rendering
 */

class GlossaryHovercards {
  constructor(options = {}) {
    this.glossaryData = new Map();
    this.hoverDelayMs = options.hoverDelay || 300;
    this.hideDelayMs = options.hideDelay || 200;
    this.hoverTimeout = null;
    this.hideTimeout = null;
    this.hovercardStack = [];
    this.hovercardElements = new Set();
    
    this.init();
  }

  init() {
    this.loadGlossaryData();
    this.processDocument();
    this.injectStyles();
    this.setupGlobalMouseTracking();
  }

  loadGlossaryData() {
    const glossaryElement = document.getElementById('glossary-data');
    if (!glossaryElement) {
      console.warn('Glossary data element not found');
      return;
    }

    const terms = glossaryElement.querySelectorAll('dt.term');
    const definitions = glossaryElement.querySelectorAll('dd.definition');

    for (let i = 0; i < terms.length; i++) {
      const term = terms[i].textContent.trim();
      const definition = definitions[i].innerHTML;
      this.glossaryData.set(term.toLowerCase(), {
        term: term,
        definition: definition
      });
    }
  }

  processDocument() {
    const definitions = document.querySelectorAll('dd.definition');
    definitions.forEach(def => this.processDefinitionElement(def));
  }

  processDefinitionElement(element) {
    this.processTextNodes(element);
  }

  processTextNodes(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = node.textContent;
      const regex = /\*\*([^*]+)\*\*/g;
      
      if (regex.test(text)) {
        const fragment = document.createDocumentFragment();
        let lastIndex = 0;
        const matches = text.matchAll(/\*\*([^*]+)\*\*/g);
        
        for (const match of matches) {
          if (match.index > lastIndex) {
            fragment.appendChild(
              document.createTextNode(text.substring(lastIndex, match.index))
            );
          }
          
          const term = match[1];
          const span = document.createElement('span');
          span.className = 'glossary-term';
          span.textContent = term;
          span.dataset.term = term.toLowerCase();
          fragment.appendChild(span);
          
          lastIndex = match.index + match[0].length;
        }
        
        if (lastIndex < text.length) {
          fragment.appendChild(
            document.createTextNode(text.substring(lastIndex))
          );
        }
        
        node.parentNode.replaceChild(fragment, node);
      }
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      if (!node.classList.contains('glossary-term') && 
          !node.classList.contains('glossary-hovercard') &&
          node.tagName !== 'SCRIPT' && 
          node.tagName !== 'STYLE') {
        Array.from(node.childNodes).forEach(child => this.processTextNodes(child));
      }
    }
  }

  setupGlobalMouseTracking() {
    let currentTerm = null;
    
    document.addEventListener('mousemove', (e) => {
      const term = e.target.closest('.glossary-term');
      const hovercard = e.target.closest('.glossary-hovercard');
      
      // If on a term, start hover timer
      if (term && term !== currentTerm) {
        currentTerm = term;
        clearTimeout(this.hoverTimeout);
        
        this.hoverTimeout = setTimeout(() => {
          this.showHovercard(term, e);
        }, this.hoverDelayMs);
      }
      
      // If not on the same term anymore, clear the hover timer
      if (!term || term !== currentTerm) {
        if (!term) {
          currentTerm = null;
        }
        clearTimeout(this.hoverTimeout);
      }
      
      // Always check if any hovercards should be hidden (no delay)
      this.hideOrphanedHovercards(e.clientX, e.clientY);
    });
  }

  showHovercard(termElement, event) {
    const termKey = termElement.dataset.term;
    const glossaryEntry = this.glossaryData.get(termKey);
    
    if (!glossaryEntry) {
      return;
    }

    // Create hovercard
    const hovercard = document.createElement('div');
    hovercard.className = 'glossary-hovercard';
    hovercard.dataset.level = this.hovercardStack.length;
    hovercard.dataset.triggerTerm = termKey;
    
    const title = document.createElement('div');
    title.className = 'glossary-hovercard-title';
    title.textContent = glossaryEntry.term;
    
    const content = document.createElement('div');
    content.className = 'glossary-hovercard-content';
    content.innerHTML = glossaryEntry.definition;
    
    hovercard.appendChild(title);
    hovercard.appendChild(content);

    // Process nested terms
    this.processDefinitionElement(content);

    // Add to document
    document.body.appendChild(hovercard);
    this.hovercardElements.add(hovercard);

    // Position with top edge covering the term
    this.positionHovercard(hovercard, termElement, event.clientX, event.clientY);

    // Add to stack
    this.hovercardStack.push({
      element: hovercard,
      triggerTerm: termElement
    });

    // Render math
    this.renderMath(hovercard);
  }

  positionHovercard(hovercard, termElement, mouseX, mouseY) {
    const rect = hovercard.getBoundingClientRect();
    const termRect = termElement.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const padding = 10;
    
    // Center horizontally on the mouse pointer
    let left = mouseX - (rect.width / 2);
    
    // Position so the top of the hovercard covers/overlaps the term
    // This ensures there's no gap when moving from term to hovercard
    let top = termRect.top - 5; // Slight overlap to cover the term

    // Adjust if off screen horizontally
    if (left < padding) {
      left = padding;
    } else if (left + rect.width > viewportWidth - padding) {
      left = viewportWidth - rect.width - padding;
    }

    // Adjust if off screen vertically
    if (top + rect.height > viewportHeight - padding) {
      // Try positioning above the term instead
      top = termRect.bottom - rect.height + 5;
      if (top < padding) {
        top = padding;
      }
    }
    
    if (top < padding) {
      top = padding;
    }

    hovercard.style.left = `${left}px`;
    hovercard.style.top = `${top}px`;
    
    // Set z-index based on stack position
    const level = parseInt(hovercard.dataset.level);
    hovercard.style.zIndex = 10000 + level;
  }

  hideOrphanedHovercards(mouseX, mouseY) {
    const elementUnderMouse = document.elementFromPoint(mouseX, mouseY);
    
    // Check each hovercard to see if it should be removed
    const toRemove = [];
    
    for (let i = 0; i < this.hovercardStack.length; i++) {
      const item = this.hovercardStack[i];
      const level = parseInt(item.element.dataset.level);
      
      // Check if mouse is on this specific hovercard
      const rect = item.element.getBoundingClientRect();
      const mouseOnThis = (
        mouseX >= rect.left && 
        mouseX <= rect.right && 
        mouseY >= rect.top && 
        mouseY <= rect.bottom
      );
      
      // Check if there are any hovercards above this one (higher level)
      const hasHovercardsAbove = this.hovercardStack.some(other => 
        parseInt(other.element.dataset.level) > level
      );
      
      // Remove if: mouse is NOT on it AND there are NO hovercards above it
      if (!mouseOnThis && !hasHovercardsAbove) {
        toRemove.push(i);
      }
    }
    
    // Remove hovercards in reverse order to maintain indices
    for (let i = toRemove.length - 1; i >= 0; i--) {
      const index = toRemove[i];
      const item = this.hovercardStack[index];
      item.element.remove();
      this.hovercardElements.delete(item.element);
      this.hovercardStack.splice(index, 1);
    }
    
    // Update levels after removal
    this.hovercardStack.forEach((item, index) => {
      item.element.dataset.level = index;
      item.element.style.zIndex = 10000 + index;
    });
  }

  renderMath(element) {
    // Wait for MathJax to be available
    const tryRender = () => {
      if (typeof MathJax !== 'undefined') {
        if (MathJax.typesetPromise) {
          // MathJax 3
          MathJax.typesetPromise([element]).catch((err) => {
            console.warn('MathJax rendering failed:', err);
          });
        } else if (MathJax.Hub && MathJax.Hub.Queue) {
          // MathJax 2
          MathJax.Hub.Queue(['Typeset', MathJax.Hub, element]);
        }
      } else {
        // MathJax not loaded yet, try again in 100ms
        setTimeout(tryRender, 100);
      }
    };
    
    tryRender();
  }

  injectStyles() {
    if (document.getElementById('glossary-hovercard-styles')) {
      return;
    }

    const style = document.createElement('style');
    style.id = 'glossary-hovercard-styles';
    style.textContent = `
      .glossary-term {
        font-weight: bold;
        cursor: help;
        border-bottom: 1px dotted #666;
        text-decoration: none;
      }

      .glossary-term:hover {
        color: #0066cc;
        border-bottom-color: #0066cc;
      }

      .glossary-hovercard {
        position: fixed;
        background: white;
        border: 2px solid #333;
        border-radius: 6px;
        padding: 12px 16px;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        font-size: 14px;
        line-height: 1.5;
        pointer-events: auto;
      }

      .glossary-hovercard-title {
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 8px;
        color: #222;
        border-bottom: 1px solid #ddd;
        padding-bottom: 4px;
        min-height: 24px;
      }

      .glossary-hovercard-content {
        color: #444;
      }

      .glossary-hovercard-content p {
        margin: 8px 0;
      }

      .glossary-hovercard-content p:first-child {
        margin-top: 0;
      }

      .glossary-hovercard-content p:last-child {
        margin-bottom: 0;
      }

      .glossary-hovercard .glossary-term {
        color: #0066cc;
      }
    `;
    document.head.appendChild(style);
  }
}

// Auto-initialize
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.glossaryHovercards = new GlossaryHovercards();
  });
} else {
  window.glossaryHovercards = new GlossaryHovercards();
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = GlossaryHovercards;
}
