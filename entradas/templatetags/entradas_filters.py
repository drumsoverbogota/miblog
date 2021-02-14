from django import template

register = template.Library()

tag_inicio = '[youtube]'
tag_fin = '[/youtube]'

custom_tags = [
    (tag_inicio, tag_fin)
]

enlace_youtube = """
<iframe class="centered" width="560" height="315" src="https://www.youtube.com/embed/YOUTUBEID" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
</iframe>
"""

enlace_imagen = """
<div class=center-image-youtube>
<a href='https://www.youtube.com/watch?v=YOUTUBEID' target="_blank"><img src='https://img.youtube.com/vi/YOUTUBEID/maxresdefault.jpg'></a>
</div>
"""

url_imagen = 'https://img.youtube.com/vi/YOUTUBEID/maxresdefault.jpg'

@register.filter
def classname(obj):
    return obj.__class__.__name__

@register.filter
def youtube_embed(text):

    changed_text = text
    index = 0

    while index < len(text):
        pos1 = changed_text.find(tag_inicio, index)
        pos2 = changed_text.find(tag_fin, index)

        if pos1 == -1:
            break

        index = pos2 + len(tag_fin)
        youtube_id = changed_text[pos1+len(tag_inicio):pos2]
        changed_text = changed_text[0:pos1] + enlace_youtube.replace('YOUTUBEID', youtube_id) + changed_text[index:]
    return changed_text

@register.filter
def youtube_image(text):

    changed_text = text
    index = 0

    while index < len(text):
        pos1 = changed_text.find(tag_inicio, index)
        pos2 = changed_text.find(tag_fin, index)

        if pos1 == -1:
            break

        index = pos2 + len(tag_fin)
        youtube_id = changed_text[pos1+len(tag_inicio):pos2]
        changed_text = changed_text[0:pos1] + enlace_imagen.replace('YOUTUBEID', youtube_id) + changed_text[index:]
    
    return changed_text

@register.filter
def youtube_clean(text):

    changed_text = text

    for tag in custom_tags:

        index = 0
        while index < len(text):

            pos1 = changed_text.find(tag[0], index)
            pos2 = changed_text.find(tag[1], index)

            if pos1 == -1:
                break

            index = pos2 + len(tag_fin)
            changed_text = changed_text[0:pos1] + changed_text[index:]
    
    return changed_text

@register.filter
def youtube_first_image(text):

    pos1 = text.find(tag_inicio)
    pos2 = text.find(tag_fin)

    if pos1 == -1:
        return ''

    youtube_id = text[pos1+len(tag_inicio):pos2]

    return url_imagen.replace('YOUTUBEID', youtube_id)
