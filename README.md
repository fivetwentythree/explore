### **Gemini Concept Explorer: User Manual & Guide**

#### **1. Overview**

The Gemini Concept Explorer is an interactive command-line tool designed for creative thinking, brainstorming, and learning. It allows you to start with a single idea (the "root concept") and build a visual web of interconnected concepts by leveraging the creative power of Google's Gemini API.

Instead of a simple list of related terms, the tool generates surprising, cross-domain connections, encouraging you to explore novel paths of thought. It's a partner for writers, researchers, students, artists, and anyone looking to break out of conventional thinking patterns.

#### **2. Core Features**

*   **Interactive Exploration:** You are in the driver's seat. At each step, you choose which concept to expand, guiding the exploration in the direction that interests you most.
*   **Powered by Gemini 1.5 Flash:** Utilizes a fast and highly capable AI model to generate context-aware, creative, and diverse conceptual links.
*   **Visual ASCII Tree:** See your concept web grow in real-time in your terminal with a color-coded tree structure that's easy to understand.
*   **Advanced Exporting:** Your final concept web is saved in two formats:
    *   `_tree.txt`: A simple, easy-to-share plain text file.
    *   `_graph.graphml`: A rich, structured file you can open in professional graph visualization software like **Gephi** or **Cytoscape** for deeper analysis and high-quality visuals.
*   **In-Session Controls:** Use simple commands to `prune` uninteresting branches, `save` your progress, and `exit` cleanly.
*   **Secure & Simple Setup:** Uses a standard `.env` file to keep your API key safe and requires only a few common Python libraries.

#### **3. Setup and Installation**

Before you begin, ensure you have Python 3.8+ and a package manager like `uv` or `pip` installed.

**Step 1: Install Libraries**
Open your terminal and install the necessary Python packages.

```bash
# Using uv (recommended for speed)
uv pip install google-generativeai python-dotenv networkx colorama

# Or using standard pip
pip install google-generativeai python-dotenv networkx colorama
```

**Step 2: Configure Your Gemini API Key**
The tool requires a Google Gemini API key to function.

1.  Obtain your free API key from **[Google AI Studio](https://aistudio.google.com/app/apikey)**.
2.  In the same directory where you saved `explorer.py`, create a file named exactly `.env`.
3.  Open the `.env` file and add your API key in the following format:

    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```
    Replace `"YOUR_API_KEY_HERE"` with the key you obtained. The quotes are important.

Your project is now ready to run!

#### **4. How to Use the Tool**

##### **a. Starting an Exploration**

You can start the explorer in two ways: with a default concept or with one of your own.

**Default Start:**
To begin exploring from the default root concept ("Creativity"), simply run the script:

```bash
python explorer.py
```

**Custom Start:**
To start with your own concept, use the `--root` command-line argument. If your concept contains spaces, enclose it in quotes.

```bash
# Example with a single word
python explorer.py --root="Metaphor"

# Example with multiple words
python explorer.py --root="The Nature of Consciousness"
```

You can also limit the maximum depth of any single branch with the `--depth` argument:

```bash
# Start with "Time" and don't let any branch go deeper than 5 steps
python explorer.py --root="Time" --depth=5
```

##### **b. Interactive Commands**

Once the explorer is running, you will see the tree view and a prompt `>`. This is where you control the exploration.

**1. Choosing a Concept to Expand**
A numbered list of "leaf" nodes (concepts at the end of a branch) will be displayed. These are your choices for the next exploration step.

*   **Syntax:** `[number]`
*   **Action:** Type the number corresponding to the concept you want to explore and press Enter. The tool will then query Gemini, and the tree will update with 4-5 new, related concepts branching off your selection.
*   **Example:** If you see `[1] Aesthetic Experience`, typing `1` will generate concepts related to it.

**2. Pruning a Branch**
If an exploration path becomes uninteresting, you can remove it completely.

*   **Syntax:** `prune [Concept Name]`
*   **Action:** This command removes the specified concept *and all concepts that branch from it* (its descendants). The concept name must be typed exactly as it appears in the tree.
*   **Example:** `prune Uncanny Valley`

**3. Saving Your Progress**
You can save the current state of your concept web at any time without ending the session.

*   **Syntax:** `save`
*   **Action:** Exports the current graph to both `_tree.txt` and `_graph.graphml` files. This is useful for creating backups during a long exploration.
*   **Example:** `save`

**4. Exiting the Tool**
When you are finished with your exploration, you can exit cleanly.

*   **Syntax:** `exit` or `Ctrl+C`
*   **Action:** Ends the interactive session and automatically performs a final save of your concept web.

#### **5. Understanding the Output Files**

Upon exiting, the tool generates two files named after your root concept (e.g., `creativity_tree.txt` and `creativity_graph.graphml`).

*   **`_tree.txt` (Text File):**
    This is a simple, plain-text representation of your final concept web. It's perfect for quick viewing, copying into notes, or sharing in emails.

*   **`_graph.graphml` (GraphML File):**
    This is the most powerful output. GraphML is a standard format for storing graph structures. You can open this file with free, powerful software to:
    *   **Visualize:** Create beautiful, high-resolution diagrams of your concept web.
    *   **Analyze:** Run algorithms to find the most central concepts, identify clusters of related ideas, and measure the "distance" between two concepts.
    *   **Customize:** Change colors, layouts, font sizes, and export the result as an image (PNG/SVG) or PDF for presentations and reports.

    **Recommended Software:** **[Gephi](https://gephi.org/)** is an excellent, user-friendly tool for opening and analyzing `.graphml` files.

#### **6. Usage Scenarios & Creative Strategies**

*   **Brainstorming for Projects:** Start with your project's central theme (e.g., `--root="Sustainable Cities"`) and explore until you discover novel features, marketing angles, or research directions.

*   **Learning a New Topic:** Are you new to a complex subject? Start with a core term (e.g., `--root="General Relativity"`) and use the explorer to build a mind map of key related principles, people, and implications.

*   **Breaking Writer's Block:** If you're stuck on a story, start with a core emotion or object (`--root="Nostalgia"` or `--root="The Empty Train Station"`). Follow the most surprising paths to find unexpected narrative threads and metaphors.

*   **Forced Connections:** Intentionally `prune` the most obvious branches to force the exploration into more abstract and unusual territory, sparking truly unique ideas.

#### **7. Troubleshooting**

*   **Problem:** The script exits immediately with a `FATAL: GOOGLE_API_KEY not found...` error.
    *   **Solution:** Ensure you have created the `.env` file in the correct directory, that it is named exactly `.env` (not `env.txt`), and that the content is `GOOGLE_API_KEY="YOUR_KEY"`.

*   **Problem:** The tool prints an "Error querying Gemini API" message.
    *   **Solution:** This could be a temporary issue with your internet connection or with the API itself. Check your connection and try again. If it persists, check the status of the Google AI Platform.