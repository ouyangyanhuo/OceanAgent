import argparse

from app.core.json_store import read_json, write_json
from app.core.paths import GRAPH_FILE


DEFAULT_GRAPH = {
    "graph_id": "ocean_kg_demo_v1",
    "version": 1,
    "nodes": [],
    "edges": [],
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize seed graph JSON file.")
    parser.add_argument("--force", action="store_true", help="Overwrite graph.json")
    parser.add_argument("--llm", action="store_true", help="Reserved for future LLM seed generation")
    args = parser.parse_args()

    if GRAPH_FILE.exists() and not args.force:
        graph = read_json(GRAPH_FILE, DEFAULT_GRAPH)
        print(f"graph.json already exists: {len(graph.get('nodes', []))} nodes")
        return

    write_json(GRAPH_FILE, DEFAULT_GRAPH)
    print("graph.json initialized")


if __name__ == "__main__":
    main()
