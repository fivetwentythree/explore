import argparse
import json
import os
import sys
import textwrap
import time
import shutil
from collections import deque

import networkx as nx
from colorama import Back, Fore, Style, init
from dotenv import load_dotenv
import google.generativeai as genai

# Initialize colorama for colored terminal output
init(autoreset=True)

# Load environment variables from .env file
load_dotenv()

# --- Configuration Constants ---
DEFAULT_ROOT_CONCEPT = "Creativity"
DEFAULT_MAX_DEPTH = 10
SLEEP_DURATION = 0.2  # Small delay for better UX

def clear_terminal():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

class ConceptExplorer:
    """
    An interactive tool to visually explore conceptual connections using the Gemini API.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self.seen_concepts = set()
        self.term_width, self.term_height = shutil.get_terminal_size((80, 24))
        
        # Configure the Gemini client
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print(f"{Fore.RED}FATAL: GOOGLE_API_KEY not found in environment or .env file.")
            print(f"{Fore.YELLOW}Please get a key from Google AI Studio and add it to a .env file.{Style.RESET_ALL}")
            sys.exit(1)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def query_gemini(self, prompt: str) -> str:
        """
        Queries the Gemini API with a specific prompt, requesting a JSON response.
        Returns the raw text of the response.
        """
        print(f"{Fore.LIGHTBLACK_EX} 🧠 Thinking with Gemini...{Style.RESET_ALL}", end="\r")
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            sys.stdout.write("\033[K")  # Clear the "Thinking..." line
            return response.text
        except Exception as e:
            sys.stdout.write("\033[K")
            print(f"{Fore.RED}Error querying Gemini API: {e}{Style.RESET_ALL}")
            return '{"concepts": []}'

    def get_related_concepts(self, concept: str, path: list) -> list:
        """
        Generates a prompt and queries Gemini for related concepts.
        """
        self.seen_concepts.add(concept.lower())
        full_path_str = ' → '.join(path + [concept])

        prompt = textwrap.dedent(f"""
            You are a creative agent that generates unexpected conceptual connections.
            Your goal is to build a web of ideas spanning diverse intellectual domains.

            The exploration path so far is: {full_path_str}
            The current concept to explore is: "{concept}"

            Generate 4-5 fascinating and unexpected concepts related to the current concept and the overall path.

            Guidelines:
            1.  **Intellectual Diversity**: Connect across science, art, philosophy, technology, and culture.
            2.  **Concise**: Each concept should be 1-5 words.
            3.  **Surprising**: Avoid obvious associations. Find thought-provoking links.
            4.  **Context-Aware**: The new concepts must be relevant to BOTH the immediate concept ("{concept}") and the entire path.
            5.  **Avoid Repeats**: Do not suggest any concepts already in the path or previously seen.

            Return your response as a JSON object with a single key "concepts" which contains a list of strings.
            Example: {{"concepts": ["Quantum Foam", "Aesthetic Experience", "Cognitive Scaffolding", "Emergent Systems"]}}
        """).strip()

        response_text = self.query_gemini(prompt)
        
        try:
            data = json.loads(response_text)
            related_concepts = data.get("concepts", [])
            
            filtered = [
                rc for rc in related_concepts 
                if rc.strip() and rc.lower() not in self.seen_concepts
            ]
            print(f"{Fore.GREEN}✓ Found {len(filtered)} new concepts.{Style.RESET_ALL}")
            return filtered
        except json.JSONDecodeError:
            print(f"{Fore.RED}✗ Could not parse JSON from Gemini response.{Style.RESET_ALL}")
            return []

    def display_ui(self, focus_node=None, leaf_nodes=None):
        """Clears the screen and renders the complete user interface."""
        clear_terminal()
        self.term_width, self.term_height = shutil.get_terminal_size((80, 24))

        # --- Header ---
        print(f"{Fore.GREEN}🌳 {Fore.YELLOW}GEMINI CONCEPT EXPLORER {Fore.GREEN}🌳")
        print(f"{Fore.CYAN}{'═' * min(50, self.term_width - 2)}{Style.RESET_ALL}")

        # --- Tree View ---
        tree_text = self.generate_ascii_tree(focus_node)
        print(tree_text)

        # --- Footer & Stats ---
        print(f"\n{Fore.CYAN}{'═' * min(50, self.term_width - 2)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📊 Concepts: {len(self.graph.nodes)} | Connections: {len(self.graph.edges)}{Style.RESET_ALL}")
        
        # --- Interactive Prompt ---
        if leaf_nodes:
            print(f"\n{Style.BRIGHT}Choose a concept to explore:{Style.RESET_ALL}")
            for i, node in enumerate(leaf_nodes, 1):
                print(f"  {Fore.CYAN}[{i}]{Style.RESET_ALL} {node}")
        
        print(f"\n{Fore.YELLOW}Commands: {Style.RESET_ALL}prune [name], save, exit")

    def generate_ascii_tree(self, focus_node=None) -> str:
        """Recursively generates a colorful ASCII tree representation of the graph."""
        roots = [n for n in self.graph.nodes if self.graph.in_degree(n) == 0]
        if not roots:
            return f"{Fore.RED}Graph is empty.{Style.RESET_ALL}"

        tree_lines = []
        
        # Determine the path to the focused node to keep it in view
        path_to_focus = []
        if focus_node and focus_node in self.graph:
            path_to_focus = list(reversed(list(nx.ancestors(self.graph, focus_node)))) + [focus_node]

        def _build_tree_recursive(node, prefix="", is_last=True, visited=None):
            if visited is None: visited = set()
            if node in visited: return
            visited.add(node)
            
            # --- Node Coloring ---
            connector = "└── " if is_last else "├── "
            color = Fore.YELLOW
            style = Style.NORMAL
            if node == focus_node:
                color = Back.BLUE + Fore.WHITE
            elif self.graph.out_degree(node) == 0 and self.graph.in_degree(node) > 0:
                color = Fore.GREEN # Leaf node
            elif self.graph.in_degree(node) == 0:
                color = Fore.MAGENTA # Root node
                style = Style.BRIGHT

            tree_lines.append(f"{prefix}{Fore.CYAN}{connector}{color}{style}{node}{Style.RESET_ALL}")
            
            children = list(self.graph.successors(node))
            # If there's a focus path, prioritize drawing it
            if path_to_focus:
                children.sort(key=lambda x: x not in path_to_focus)

            next_prefix = prefix + ("    " if is_last else "│   ")
            for i, child in enumerate(children):
                _build_tree_recursive(child, next_prefix, i == len(children) - 1, visited.copy())

        _build_tree_recursive(roots[0])
        return "\n".join(tree_lines)
    
    def prune_branch(self, node_to_prune: str):
        """Removes a node and all its descendants from the graph."""
        if node_to_prune not in self.graph:
            print(f"{Fore.RED}Concept '{node_to_prune}' not found.{Style.RESET_ALL}")
            time.sleep(1.5)
            return

        try:
            descendants = nx.descendants(self.graph, node_to_prune)
            nodes_to_remove = {node_to_prune} | descendants
            self.graph.remove_nodes_from(nodes_to_remove)
            
            # Clean up the seen_concepts set as well
            for node in nodes_to_remove:
                self.seen_concepts.discard(node.lower())
                
            print(f"{Fore.YELLOW}Pruned branch starting from '{node_to_prune}'.{Style.RESET_ALL}")
            time.sleep(1)
        except nx.NetworkXError:
            print(f"{Fore.RED}Could not find concept '{node_to_prune}' to prune.{Style.RESET_ALL}")
            time.sleep(1.5)

    def save_files(self, root_concept: str):
        """Exports the graph to both a plain text ASCII file and a GraphML file."""
        if not self.graph:
            print(f"{Fore.YELLOW}Graph is empty, nothing to save.{Style.RESET_ALL}")
            return
            
        filename_base = root_concept.lower().replace(" ", "_")
        
        # 1. Export ASCII Tree
        ascii_filename = f"{filename_base}_tree.txt"
        plain_tree = self.generate_ascii_tree().encode('utf-8', 'ignore').decode('utf-8')
        # Simple regex to strip ANSI color codes for plain text file
        plain_tree = '\n'.join([s.split(' ')[-1] for s in plain_tree.split('\n')])
        
        def _plain_ascii_tree(node, prefix="", is_last=True, visited=None):
            if visited is None: visited = set()
            if node in visited: return f"{prefix}{'└── ' if is_last else '├── '}{node} (...)\n"
            visited.add(node)
            result = f"{prefix}{'└── ' if is_last else '├── '}{node}\n"
            children = list(self.graph.successors(node))
            if not children: return result
            next_prefix = prefix + ("    " if is_last else "│   ")
            for i, child in enumerate(children):
                is_last_child = (i == len(children) - 1)
                result += _plain_ascii_tree(child, next_prefix, is_last_child, visited.copy())
            return result
        
        roots = [n for n in self.graph.nodes if self.graph.in_degree(n) == 0]
        tree_text = _plain_ascii_tree(roots[0])
        with open(ascii_filename, 'w', encoding='utf-8') as f:
            f.write(tree_text)
        print(f"{Fore.GREEN}📝 Plain text tree saved to {ascii_filename}{Style.RESET_ALL}")

        # 2. Export GraphML for professional tools
        graphml_filename = f"{filename_base}_graph.graphml"
        nx.write_graphml(self.graph, graphml_filename)
        print(f"{Fore.GREEN}📊 GraphML file saved to {graphml_filename} (open with Gephi/Cytoscape){Style.RESET_ALL}")

    def run_exploration(self, root_concept: str, max_depth: int):
        """The main interactive exploration loop."""
        self.graph.add_node(root_concept)
        
        current_focus = root_concept
        path_to_current = {root_concept: []}

        while True:
            # Find all nodes that can be explored (leaf nodes)
            leaf_nodes = [n for n in self.graph.nodes if self.graph.out_degree(n) == 0 and nx.shortest_path_length(self.graph, root_concept, n) < max_depth]
            
            self.display_ui(current_focus, leaf_nodes)

            if not leaf_nodes:
                print(f"\n{Fore.GREEN}🎉 No more concepts to explore (or max depth reached). Exploration complete!{Style.RESET_ALL}")
                break

            try:
                user_input = input(f"{Style.BRIGHT}> {Style.RESET_ALL}").strip()
                
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'save':
                    self.save_files(root_concept)
                    time.sleep(2)
                    continue
                elif user_input.lower().startswith('prune '):
                    node_to_prune = user_input[6:].strip()
                    self.prune_branch(node_to_prune)
                    current_focus = root_concept # Reset focus after pruning
                    continue
                elif user_input.isdigit() and 1 <= int(user_input) <= len(leaf_nodes):
                    choice_index = int(user_input) - 1
                    concept_to_explore = leaf_nodes[choice_index]
                    current_focus = concept_to_explore
                    
                    # Get new concepts from Gemini
                    path = nx.shortest_path(self.graph, source=root_concept, target=concept_to_explore)
                    related_concepts = self.get_related_concepts(concept_to_explore, path)

                    # Add new concepts to the graph
                    for rel_concept in related_concepts:
                        if rel_concept not in self.graph:
                            self.graph.add_node(rel_concept)
                        self.graph.add_edge(concept_to_explore, rel_concept)
                    
                    time.sleep(SLEEP_DURATION)
                else:
                    print(f"{Fore.RED}Invalid command. Please enter a number from the list or a valid command.{Style.RESET_ALL}")
                    time.sleep(1.5)

            except KeyboardInterrupt:
                break # Exit loop on Ctrl+C

        # --- Cleanup and Save ---
        print(f"\n{Fore.YELLOW}Exploration ended.{Style.RESET_ALL}")
        self.save_files(root_concept)

def main():
    """Main function to parse arguments and start the explorer."""
    parser = argparse.ArgumentParser(
        description="An interactive tool to visually explore conceptual connections using the Gemini API.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--root", 
        default=DEFAULT_ROOT_CONCEPT, 
        help="The root concept to start exploration with.\n(default: %(default)s)"
    )
    parser.add_argument(
        "--depth", 
        type=int, 
        default=DEFAULT_MAX_DEPTH,
        help="Maximum exploration depth for any branch.\n(default: %(default)s)"
    )
    args = parser.parse_args()

    try:
        explorer = ConceptExplorer()
        explorer.run_exploration(args.root, args.depth)
    except SystemExit as e:
        # Intercept sys.exit from API key check
        pass
    except Exception as e:
        print(f"\n{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
    finally:
        print(f"\n{Style.RESET_ALL}Thank you for using the Gemini Concept Explorer!")

if __name__ == "__main__":
    main()