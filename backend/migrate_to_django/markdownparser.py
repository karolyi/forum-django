import html

from html2text import html2text


def markdown_smilies(img_tag):
    img_src = img_tag.get('src', '')
    if img_src.startswith('/static/images/smiliereplace/'):
        img_alt = img_tag.get('alt', '')
        img_tag.replace_with(img_alt)
        return
    if img_src.startswith('/static/images/smilies/'):
        img_tag.replace_with('[SMIL:%s]' % img_src[22:])
        return


def replace_images(content):
    for img_tag in content.select('img'):
        markdown_smilies(img_tag)


def parse_to_markdown(content, comment_item, md_property):

    replace_images(content)

    for embed_item in content.select('div.embedded-player'):
        embed_item.replace_with(embed_item.md_url)

    content_md_html = content.body.encode_contents()\
        .decode('utf-8')\
        .replace('></source>', '/>')\
        .replace('\r\n', '\n')
    md_content = html2text(content_md_html, bodywidth=0)
    # Convert 2 BRs to Ps
    md_content = html.unescape(md_content).replace('  \n  \n', '\n\n')
    setattr(comment_item, md_property, md_content)
