"""
Markdown rendering utility for converting markdown to HTML.
Uses Python-Markdown with extensions for rich content support.
"""
import markdown


def render_markdown(markdown_text):
    """
    Convert markdown text to HTML with syntax highlighting and extensions.

    Args:
        markdown_text (str): The markdown text to convert

    Returns:
        str: HTML output
    """
    if not markdown_text:
        return ""

    md = markdown.Markdown(
        extensions=[
            'extra',              # Includes tables, footnotes, etc.
            'codehilite',        # Code syntax highlighting
            'fenced_code',       # Fenced code blocks
            'nl2br',             # Convert newlines to <br>
            'sane_lists',        # Better list handling
            'smarty',            # Smart typography
            'toc',               # Table of contents
            'attr_list',         # Add attributes to elements
            'def_list',          # Definition lists
            'abbr',              # Abbreviations
        ],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'linenums': False,
                'guess_lang': True,
            },
            'toc': {
                'permalink': True,
                'permalink_class': 'toc-link',
            }
        }
    )

    html = md.convert(markdown_text)
    return html


def get_excerpt(markdown_text, max_length=200):
    """
    Extract a plain text excerpt from markdown.

    Args:
        markdown_text (str): The markdown text
        max_length (int): Maximum length of excerpt

    Returns:
        str: Plain text excerpt
    """
    if not markdown_text:
        return ""

    # Remove markdown formatting
    plain_text = markdown_text
    plain_text = plain_text.replace('#', '')
    plain_text = plain_text.replace('*', '')
    plain_text = plain_text.replace('_', '')
    plain_text = plain_text.replace('`', '')
    plain_text = plain_text.replace('[', '')
    plain_text = plain_text.replace(']', '')
    plain_text = plain_text.replace('(', '')
    plain_text = plain_text.replace(')', '')

    # Remove extra whitespace
    plain_text = ' '.join(plain_text.split())

    # Truncate
    if len(plain_text) > max_length:
        plain_text = plain_text[:max_length].rsplit(' ', 1)[0] + '...'

    return plain_text
