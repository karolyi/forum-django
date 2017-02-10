import re

from markdown2 import Markdown


class ForumMarkdownParser(Markdown):
    """
    Subclassing the markdown parser for local adjustments.
    """

    _strike_re = re.compile(r'~~(?=\S)(.+?)(?<=\S)~~', re.DOTALL)

    def _do_italics_and_bold(self, text):
        """
        Override the original `_do_italics_and_bold`, so that we can
        insert our `strikethrough` logic in here.
        """
        text = super(ForumMarkdownParser, self)._do_italics_and_bold(text)
        text = self._strike_re.sub(r'<s>\1</s>', text)
        return text

    # def preprocess(self, text):
    #     print('preprocess', text)
    #     return text

    # def postprocess(self, text):
    #     print('postprocess', text)
    #     return text
