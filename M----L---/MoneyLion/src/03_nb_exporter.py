"""
 Script Metadata

- Script Name: 03_nb_exporter.py
- Title: MoneyLion DS Assessment
- Author: Khoon Ching Wong
- Created: 2024-09-24
- Last Modified: 2025-09-25
- Repository Link: https://github.com/wongkhoon/DS-Assessment/tree/main/MoneyLion/src

Description:
  What this script does:
 - Converts Jupyter notebooks (.ipynb) into HTML files
 - Adds a transparent text watermark in the background
 - Changes the appearance of the HTML using CSS (styling)
 - Adds interactivity using JavaScript (JS)
 - Numbers lines inside code cells for easier reading
 - Makes notebook headings collapsible and numbered
 - Adds small floating buttons for toggling features
 - Puts the current date and time in both the filename and at the bottom (footer) of the HTML page

  How to run this script:
 - On Linux or macOS (or Windows with GNU Make installed):
       make export
   (This assumes a Makefile is already set up.)

   On all systems (including Windows without Make):
       python 03_notebook_exporter.py "01_eda.ipynb" "02_model.ipynb"
       python 03_notebook_exporter.py "1. EDA.ipynb" Miscellaneous.ipynb

Makefile example:
    # Pass NOTEBOOKS="file1.ipynb file2.ipynb" to override
    NOTEBOOKS ?= "01_eda.ipynb" "02_model.ipynb"

    export:
        python 03_nb_exporter.py $(NOTEBOOKS)

Tip:
 If on Windows and don’t have "make", just use the Python command directly as shown above.

"""

import pathlib # For handling file system paths
import subprocess # For running shell commands (nbconvert)
import urllib.parse # For safely embedding SVG in HTML
from datetime import datetime # For timestamped filenames

def export_notebook(notebook_name):
    
    # https://docs.python.org/3/library/pathlib.html

    # Convert notebook to HTML
    notebook = pathlib.Path(notebook_name).resolve() # Creates a path object, resolve() gets absolute path

    # Timestamp for unique filenames
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create a new filename with timestamp (e.g. notebook_YYYYMMDD_HHMMSS.html)
    html_file = notebook.with_name(f'{notebook.stem}_{timestamp_str}.html')

    # Run nbconvert with explicit output filename
    # https://docs.python.org/3/library/subprocess.html#subprocess.run
    subprocess.run(
        ["jupyter", "nbconvert", "--to", "html", str(notebook), "--output", html_file.name],
        cwd = notebook.parent, # Run from the same directory as the notebook
        check = True, # Raise CalledProcessError if command fails (non-zero exit code)
        capture_output = True, text = True # Capture logs in readable text format
    )

    # Scalable Vector Graphics(SVG) watermark design (gray, rotated text)
    # https://www.w3.org/TR/SVG2/struct.html#SVGElement
    # ==============================================
    # SVG: xmlns defines XML namespace, width/height set canvas size, viewBox defines coordinate system (x-min y-min width height)
    # text element: x/y position coordinates, font-size in pixels, fill is text color, fill-opacity is transparency (0 = invisible, 1 = opaque)
    # text-anchor = "middle" centers text horizontally at x position, dominant-baseline = "middle" centers vertically at y position
    # transform = "rotate(-30 150 100)" rotates text -30 degrees around point (150, 100)
    # ==============================================
    svg_code = '''
                <svg xmlns="http://www.w3.org/2000/svg" width = "300" height = "200" viewBox = "0 0 300 200">
                <text x = "150" y = "100" font-size = "20" fill = "gray" fill-opacity = "0.15"
                text-anchor = "middle" dominant-baseline = "middle"
                transform = "rotate(-30 150 100)">
                Khoon Ching Wong
                </text>
                </svg>
                '''

    # Make the SVG displayable in the browser by embedding it safely in a link
    svg = "data:image/svg+xml;utf8," + urllib.parse.quote(svg_code)

    # CSS + JS injection (kept unchanged, plus footer timestamp added at the end)
    timestamp_footer = f'''
                <!-- ===== Timestamp Footer ===== -->
                <footer style="position: fixed; bottom: 5px; right: 10px; font-size: 12px; color: gray; opacity: 0.7;">
                  Exported on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                </footer>
                '''

    html_injection = f'''<style>
                /* ===== Watermark ===== */
                body::before {{ /* Creates pseudo-element as first child of body */
                  content: " "; /* Content property required for pseudo-elements, space prevents collapse */
                  position: fixed; /* Fixed positioning relative to viewport, stays in place when scrolling */
                  inset: 0; /* Shorthand for top: 0 right: 0 bottom: 0 left: 0  */
                  z-index: 9999; /* Always stays on top of content */
                  pointer-events: none; /* Doesn’t block clicks or interaction */
                  display: block; /* Makes element fill available width */
                  background: url("{svg}") repeat; /* Fills with the SVG watermark repeatedly */
                  background-size: max(300px, 30vw) max(200px, 20vh); /* Responsive scaling: width is 30% of viewport (minimum 300px), height is 20% of viewport (minimum 200px) */
                }}
                
                /* ===== Code line numbers ===== */
                .line-numbered {{ /* Class selector for pre elements that will have line numbers */
                  counter-reset: line; /* Initializes CSS counter named "line" to 0 */
                }}
                .line-numbered > span {{ /* > is child selector: targets span elements that are direct children */
                  counter-increment: line; /* Increases "line" counter by 1 for each span */
                  display: block; /* Block display puts each span on new line */
                  position: relative; /* Relative positioning allows absolute positioning of children */
                  padding-left: 3em; /* Adds space inside element on left side, em is relative to font size */
                }}
                .line-numbered > span::before {{ /* ::before pseudo-element for line number display */
                  content: counter(line); /* counter() function returns current value of "line" counter */
                  position: absolute; /* Absolute positioning relative to parent span */
                  left: 0; /* Positions element at left edge of parent */
                  width: 2.5em; /* Sets element width, em scales with font */
                  color: #888; /* Hex color code for medium gray */
                  text-align: right; /* Aligns text to right edge within element */
                  display: inline-block; /* Allows width setting while staying in text flow */
                }}
                
                /* Hide line numbers */
                .hide-lines > span::before {{ /* Targets ::before pseudo-elements when parent has hide-lines class */
                  display: none; /* Completely removes element from layout */
                }}
                .hide-lines > span {{ /* Targets spans when parent has hide-lines class */
                  padding-left: 0; /* Removes the indentation when numbers hidden */
                }}
                
                /* ===== Toggle heading numbers ===== */
                .hide-headings .heading-number {{ /* Space selector: .heading-number inside .hide-headings ancestor */
                  display: none; /* Removes heading numbers from view */
                }}
                
                /* ===== Collapsible headings ===== */
                .collapsible {{ /* Class for clickable heading elements */
                  cursor: pointer; /* Shows hand cursor on hover */
                  user-select: none; /* Prevents text selection on click/drag */
                }}
                .collapsible.collapsed {{ /* Combined selector: element with both classes */
                  color: #888; /* Gray color indicates collapsed state */
                }}
                </style>
                
                <script>
                document.addEventListener("DOMContentLoaded", () => {{ /* DOMContentLoaded event fires when HTML parsing complete, () => is arrow function */
                  // === Add line-number spans in code cells ===
                  document.querySelectorAll("div.input_area pre, div.highlight pre").forEach(pre => {{ /* Returns NodeList of all matching elements, comma separates multiple selectors */
                    if (!pre.classList.contains("line-numbered")) {{ /* Checks if element has specific class, ! negates boolean */
                      // Get the text content preserving whitespace
                      let codeElement = pre.querySelector("code"); /* Returns first matching child element or null */
                      let textContent = codeElement ? codeElement.textContent : pre.textContent; /* ternary operator: if codeElement exists use its textContent, else use pre's textContent */
                     
                      // Split into lines, preserving empty lines
                      let lines = textContent.split("\\n"); /* Divides string at each newline character into array */
                      
                      // Create new structure preserving original formatting
                      if (codeElement) {{ /* if statement checks if code element exists (truthy) */
                        // Clear the code element
                        codeElement.innerHTML = ""; /* Removes all child elements and content */
                        
                        // Add each line as a span
                        lines.forEach((line, index) => {{ /* forEach iterates array, line is current item, index is position */
                          let span = document.createElement("span"); /* Creates new DOM element */
                          span.textContent = line + (index < lines.length - 1 ? "\\n" : "");  /* textContent sets text, ternary adds newline except for last line */
                          codeElement.appendChild(span); /* Adds span as last child of code element */
                        }});
                      }} else {{ /* else block executes when codeElement is null/undefined */
                        // Clear the pre element
                        pre.innerHTML = ""; /* Empties the pre element */
                        
                        // Add each line as a span
                        lines.forEach((line, index) => {{ /* forEach loop for each line in array */
                          let span = document.createElement("span"); /* Makes new span element */
                          span.textContent = line + (index < lines.length - 1 ? "\\n" : ""); /* Set text with conditional newline */
                          pre.appendChild(span); /* Adds span to pre element */
                        }});
                      }}
                      
                      pre.classList.add("line-numbered"); /* Adds CSS class to element */
                    }}
                  }});
                
                  // === Number + collapsible headings ===
                  let counters = [0,0,0,0,0,0]; /* Array literal with 6 zeros for h1-h6 counters, let declares block-scoped variable */
                  let allHeadings = document.querySelectorAll( /* Returns all matching elements */
                    ".text_cell_render h1, .text_cell_render h2, .text_cell_render h3, .text_cell_render h4, .text_cell_render h5, .text_cell_render h6, \
                     .jp-RenderedHTMLCommon h1, .jp-RenderedHTMLCommon h2, .jp-RenderedHTMLCommon h3, .jp-RenderedHTMLCommon h4, .jp-RenderedHTMLCommon h5, .jp-RenderedHTMLCommon h6"
                  ); /* Selectors target h1-h6 inside two different parent classes, backslash continues line */
                
                  allHeadings.forEach(h => {{ /* forEach iterates NodeList, h is current heading element */
                    let level = parseInt(h.tagName.substring(1)); /* tagName is "H1", "H2" etc., substring(1) removes "H", parseInt converts to number */
                    counters[level-1]++; /* Increment counter at index level-1 (arrays are 0-indexed) */
                    counters.fill(0, level); /* Sets array elements to 0 starting at index 'level' */
                    let numbering = counters.slice(0, level).join(".");  /* Copies first 'level' elements, join(".") concatenates with dots */
                
                    if (!h.querySelector(".heading-number")) {{ /* Check if heading already has number span */
                      let span = document.createElement("span"); /* Create new span element */
                      span.className = "heading-number"; /* className property sets class attribute */
                      span.textContent = numbering + " "; /* textContent sets text with space after number */
                      h.insertBefore(span, h.firstChild); /* insertBefore adds span before first child of heading */
                    }}
                
                    h.classList.add("collapsible"); /* Add collapsible class to heading */
                    let section = document.createElement("div"); /* Create div to hold section content */
                    section.classList.add("section-content"); /* Add class to section div */
                
                    let parentCell = h.closest(".cell, .jp-Cell");  /* closest() finds nearest ancestor matching selector */
                    let next = parentCell.nextElementSibling; /* nextElementSibling gets next element node (skips text nodes) */

                   /* Collect all cells belonging to this section */
                    while (next) {{ /* while loop continues as long as next is truthy (not null) */
                      let headingInNext = next.querySelector( /* querySelector searches for heading in next cell */
                        ".text_cell_render h1, .text_cell_render h2, .text_cell_render h3, .text_cell_render h4, .text_cell_render h5, .text_cell_render h6, \
                         .jp-RenderedHTMLCommon h1, .jp-RenderedHTMLCommon h2, .jp-RenderedHTMLCommon h3, .jp-RenderedHTMLCommon h4, .jp-RenderedHTMLCommon h5, .jp-RenderedHTMLCommon h6"
                      );
                      if (headingInNext) {{ /* If finds a heading in next cell */
                        let nextLevel = parseInt(headingInNext.tagName.substring(1)); /* Extract heading level number */
                        if (nextLevel <= level) break; /* break exits while loop if same or higher level heading found */
                      }}
                      let temp = next.nextElementSibling; /* Store reference to following element before moving current */
                      section.appendChild(next); /* Moves 'next' element into section (removes from original location) */
                      next = temp; /* Update next to the stored reference for next iteration */
                    }}
                
                    parentCell.parentNode.insertBefore(section, next); /* parentNode gets parent element, insertBefore adds section before 'next' element (or at end if next is null) */

                    /* Make heading clickable to collapse/expand section */
                    h.addEventListener("click", () => {{ /* Attaches click event handler, arrow function defines handler */
                      if (section.style.display === "none") {{ /* Accesses inline CSS display property, === checks strict equality */
                        section.style.display = ""; /* Removes inline display style, reverts to CSS default */
                        h.classList.remove("collapsed"); /* Removes the collapsed class */
                      }} else {{ /* else block runs when section is currently visible */
                        section.style.display = "none"; /* Hides element completely */
                        h.classList.add("collapsed"); /* Adds the collapsed class */
                      }}
                    }});
                  }});
                }});
                
                // ===== Toggle functions =====
                function toggleLines() {{ /* function keyword declares named function */
                  document.querySelectorAll("pre.line-numbered").forEach(pre => {{ /* Select all pre elements with line-numbered class */
                    pre.classList.toggle("hide-lines"); /* toggle() adds class if absent, removes if present */
                  }});
                }}
                function toggleHeadings() {{ /* Function to toggle heading numbering */
                  document.body.classList.toggle("hide-headings"); /* document.body references <body> element, toggle adds/removes class */
                }}
                function toggleAll() {{ /* Function to toggle both features */
                  toggleLines(); /* Call toggleLines function */
                  toggleHeadings(); /* Call toggleHeadings function */
                }}
                function resetView() {{ /* Function to reset all toggles */
                  document.body.classList.remove("hide-headings"); /* Removes class if present, does nothing if absent */
                  document.querySelectorAll("pre.line-numbered").forEach(pre => {{ /* Select all numbered pre elements */
                    pre.classList.remove("hide-lines"); /* Remove hide-lines class from each */
                  }});
                }}
                </script>
                
                <!-- ===== Floating buttons ===== -->
                <div style="position: fixed; top: 10px; right: 10px; z-index: 10000;"> <!-- position:fixed attaches to viewport, top/right position from edges, z-index ensures above other content -->
                  <button onclick="toggleLines()" style="padding:5px 10px; margin-right:5px;"> <!-- onclick attribute sets click handler inline, padding adds internal space, margin-right adds space between buttons --> 
                    Toggle Line Numbers
                  </button>
                  <button onclick="toggleHeadings()" style="padding:5px 10px; margin-right:5px;"> <!-- Each button calls its respective function on click -->
                    Toggle Heading Numbers
                  </button>
                  <button onclick="toggleAll()" style="padding:5px 10px; margin-right:5px;">
                    Toggle All Numbers
                  </button>
                  <button onclick="resetView()" style="padding:5px 10px;"> <!-- Last button has no margin-right -->
                    Reset View
                  </button>
                </div>
                {timestamp_footer}
                '''

    # Inject into HTML file
    html_file.write_text(
        html_file.read_text(encoding = "utf-8") # Read the entire HTML file content as a string (UTF-8 encoding ensures proper character handling)
        .replace("</head>", html_injection + "</head>"), # Replace the closing </head> tag with our injected CSS+JS + the </head> tag again
        encoding = "utf-8" # Write the modified string back into the same HTML file (again using UTF-8 encoding)
    )

    # Print a timestamped log message showing which notebook was exported and the name of the generated HTML file
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} [INFO] Export completed for {notebook_name} -> {html_file.name}')


def export_all_notebooks(notebooks):
    # Iterate through each notebook filename in the provided list
    for nb in notebooks:
        # Call the export_notebook function for each notebook
        export_notebook(nb)

# Ensures the script only runs when executed directly, not when imported as a module into another Python script
if __name__ == "__main__":
    import sys
    notebooks = sys.argv[1:]  # Accept multiple notebooks from command line 
    if not notebooks: # Check if any notebooks not passed
        # Print helpful usage instructions when no arguments are given
        print("Usage: python notebook_exporter.py notebook1.ipynb notebook2.ipynb ...")
    else:
        # Call the batch export function with the provided list of notebooks
        export_all_notebooks(notebooks)