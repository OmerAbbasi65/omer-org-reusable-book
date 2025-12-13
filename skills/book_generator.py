import json
import argparse
import os

def generate_markdown_from_spec(spec_path, output_path):
    """
    Generates a markdown file from a chapter spec file.

    Args:
        spec_path (str): The path to the chapter spec file (JSON).
        output_path (str): The path to write the generated markdown file.
    """
    try:
        with open(spec_path, 'r') as f:
            spec = json.load(f)
    except FileNotFoundError:
        print(f"Error: Spec file not found at {spec_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in spec file at {spec_path}")
        return

    title = spec.get('title', 'Untitled Chapter')
    content = spec.get('content', [])

    markdown_content = f"# {title}\n\n"

    for item in content:
        item_type = item.get('type')
        if item_type == 'paragraph':
            markdown_content += f"{item.get('text', '')}\n\n"
        elif item_type == 'code':
            lang = item.get('language', '')
            markdown_content += f"```{lang}\n{item.get('code', '')}\n```\n\n"
        # Add more content types here as needed (e.g., images, lists)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(markdown_content)

    print(f"Successfully generated markdown file at {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a markdown file from a chapter spec.')
    parser.add_argument('spec_path', help='The path to the chapter spec file (JSON).')
    parser.add_argument('output_path', help='The path to write the generated markdown file.')
    args = parser.parse_args()

    generate_markdown_from_spec(args.spec_path, args.output_path)
