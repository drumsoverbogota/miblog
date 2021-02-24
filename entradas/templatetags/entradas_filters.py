from django import template
from .custom_tags import custom_tags_dictionary

register = template.Library()

url_imagen = 'https://img.youtube.com/vi/YOUTUBEID/maxresdefault.jpg'

first_tag = lambda tag: "[TAG]".replace("TAG", tag)
last_tag = lambda tag: "[/TAG]".replace("TAG", tag)


@register.filter
def replace_custom_tags(text):

    changed_text = text

    for tag in custom_tags_dictionary:
        
        replace_value = custom_tags_dictionary[tag]
        open_tag = first_tag(tag)
        close_tag = last_tag(tag)

        index = 0
        while index < len(text):

            pos1 = changed_text.find(open_tag, index)
            pos2 = changed_text.find(close_tag, index)

            if pos1 == -1:
                break

            index = pos2 + len(close_tag)
            tag_content = changed_text[pos1+len(open_tag):pos2]
            changed_text = changed_text[0:pos1] + replace_value.replace("TAGTEXT", tag_content) + changed_text[index:]
    
    return changed_text

@register.filter
def classname(obj):
    return obj.__class__.__name__


@register.filter
def youtube_first_image(text):

    tag_inicio = first_tag("youtube")
    tag_fin = last_tag("youtube")

    pos1 = text.find(tag_inicio)
    pos2 = text.find(tag_fin)

    if pos1 == -1:
        return ''

    youtube_id = text[pos1+len(tag_inicio):pos2]

    return url_imagen.replace('YOUTUBEID', youtube_id)

@register.filter
def youtube_clean(text):

    changed_text = text

    index = 0

    tag_inicio = first_tag("youtube")
    tag_fin = last_tag("youtube")

    pos1 = text.find(tag_inicio)
    pos2 = text.find(tag_fin)

    if pos1 == -1:
        return ''

    while index < len(text):

        pos1 = changed_text.find(tag_inicio, index)
        pos2 = changed_text.find(tag_fin, index)

        if pos1 == -1:
            break

        index = pos2 + len(tag_fin)
        changed_text = changed_text[0:pos1] + changed_text[index:]
    
    return changed_text
