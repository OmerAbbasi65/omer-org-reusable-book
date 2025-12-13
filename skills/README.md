# Book Generation Skill

This directory contains reusable "skills" for the unified book project.

## `book_generator.py`

This script generates a markdown file from a chapter specification file.

### Usage

```bash
python skills/book_generator.py <path_to_spec.json> <path_to_output.md>
```

### Example

```bash
python skills/book_generator.py reusable-book/spec/chapters/01-introduction.spec.json reusable-book/docs/01-introduction.md
```
