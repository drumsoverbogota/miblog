youtube_embed = """
<div class=center-image-youtube>
<a href='https://www.youtube.com/watch?v=TAGTEXT' target="_blank"><img src='https://img.youtube.com/vi/TAGTEXT/hqdefault.jpg'></a>
</div>
<p class="center">
Esta imagen contiene un enlace a Youtube, al hacer click en ella se abrirá en una pestaña nueva el enlace.
</p>
"""

bold_text = """
<strong>TAGTEXT</strong>
"""

italic_text = """
<i>TAGTEXT</i>
"""

center_text = """
<p class="center">TAGTEXT</p>
"""
custom_tags_dictionary = {
    'youtube': youtube_embed,
    'bold': bold_text,
    'it': italic_text,
    'center': center_text,
}