from typing import List, Tuple, Union

from bs4.element import Tag
from django.test import TestCase
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _


class SimpleFormElementBase(object):
    """
    Tester base for elements for form elements provided by
    `render-form-simple.html`.
    """
    _tag_name = ''
    _attrs = {}

    def __init__(self, test: TestCase, soup: Tag, name: str, attrs: dict=None):
        """
        Initialize defaults for the element parser.
        """
        self._my_name = type(self).__name__
        self._create_attrs(attrs)
        self.attrs['name'] = name
        self.test = test
        self.element = \
            soup.find(name=self._tag_name, attrs=self.attrs)  # type: Tag
        self.test.assertIsInstance(obj=self.element, cls=Tag, msg=_(
            '\'{name}\' HTML element not found. Passed attributes were: '
            '\'{attrs}\'').format(name=self._tag_name, attrs=self.attrs))

    def __str__(self):
        """
        Return our type and name.
        """
        return _('Simple form element: <{_my_name}: {name}>').format(
            _my_name=self._my_name, name=self.attrs['name'])

    def _create_attrs(self, attrs: dict):
        """
        Update passed attributes to mix the the one in we already have.
        """
        self.attrs = self._attrs.copy()
        if attrs is None:
            # Nothing to update with
            return
        for key, value_new in attrs.items():
            value_old = self.attrs.get(key)
            if value_old is None:
                self.attrs[key] = value_new
                continue
            self.attrs[key] = '{value_old} {value_new}'.format(
                value_old=value_old, value_new=value_new)

    @cached_property
    def label(self) -> Tag:
        """
        Return the element's HTML label tag.
        """
        return self.element.parent.parent.label

    @cached_property
    def label_content(self) -> str:
        """
        Return the element label's text content.
        """
        return self.label.decode_contents()

    @cached_property
    def help_text(self) -> str:
        """
        Return the generated element's help text.
        """
        return self.element.parent.find(
            name='span', class_='help-text').decode_contents()

    @cached_property
    def widget_wrapper(self) -> Tag:
        """
        Return the wrapper for the input element.
        """
        wrapper = self.element.find_parent(class_='widget-wrapper')
        self.test.assertIsInstance(obj=wrapper, cls=Tag, msg=_(
            'Widget wrapper for {_my_name} \'{name}\' not found.').format(
            _my_name=self._my_name, name=self.attrs['name']))
        return wrapper

    def _assert_attribute(self, name: str, value: str):
        """
        Assert that the element has a certain attribute set with a
        certain value.
        """
        self.test.assertEqual(self.element.get(name), value, msg=(
            '{my_name} does not have the expected {attribute} attribute.'
        ).format(my_name=self._my_name, attribute=name))

    def assert_label_content(self, text: str):
        """
        Assert that the rendered label for the element is the passed
        string in the parameter.
        """
        self.test.assertEqual(
            self.label_content, text, msg=_(
                'Label for {_my_name} \'{name_attr}\' differs from expected.'
            ).format(_my_name=self._my_name, name_attr=self.attrs['name']))

    def assert_help_text(self, text: str):
        """
        Assert that the rendered element's help text (in whatever way
        it's rendered) is the same as the passed text.
        """
        self.test.assertEqual(self.help_text, text, msg=_(
            'Help text for {_my_name} \'{name_attr}\' differs from expected.'
        ).format(_my_name=self._my_name, name_attr=self.attrs['name']))

    def assert_has_error(self):
        """
        Assert that the rendered element has an error.
        """
        wrapper_classes = self.widget_wrapper.attrs['class']
        self.test.assertIn(
            member='has-danger', container=wrapper_classes, msg=_(
                'Expected the {_my_name} \'{name_attr}\' to have an error but '
                'it doesn\'t have any.').format(
                _my_name=self._my_name, name_attr=self.attrs['name']))
        widget_error = self.widget_wrapper.find(
            name='div', class_='widget-error')  # type: Tag
        self.test.assertIsInstance(obj=widget_error, cls=Tag, msg=_(
            'Expected the {_my_name} \'{name_attr}\' to have an error alert '
            'but found none').format(
            _my_name=self._my_name, name_attr=self.attrs['name']))
        error_classes = widget_error.attrs['class']
        self.test.assertIn(
            member='text-danger', container=error_classes, msg=_(
                'Expected the {_my_name} \'{name_attr}\' to have an error '
                'with error class text-danger but it doesn\'t have any.'
            ).format(
                _my_name=self._my_name, name_attr=self.attrs['name']))

    def assert_has_no_error(self):
        """
        Assert that the rendered element has an error.
        """
        wrapper_classes = self.widget_wrapper.attrs['class']
        self.test.assertNotIn(
            member='has-danger', container=wrapper_classes, msg=_(
                'Expected the {_my_name} \'{name_attr}\' NOT to have an error '
                'but it has errors.').format(
                _my_name=self._my_name, name_attr=self.attrs['name']))


class TextAreaInput(SimpleFormElementBase):
    """
    A textarea input tester for the simple form.
    """
    _tag_name = 'textarea'
    _attrs = {
        'class': 'form-control'}

    @cached_property
    def help_text(self):
        """
        Return the help text that is the placeholder of the
        `TextAreaInput`.
        """
        return self.element.get(key='placeholder')

    def assert_content(self, text: str):
        """
        Assert that the `TextAreaInput` has specific content.
        """
        self.test.assertEqual(
            self.element.decode_contents().strip(), text, msg=(
                '{my_name} does not contain the expected string.').format(
                my_name=self._my_name))


class TextInput(SimpleFormElementBase):
    """
    A simple text input tester.
    """
    _tag_name = 'input'
    _attrs = {
        'type': 'text',
        'class': 'form-control'}

    @cached_property
    def help_text(self):
        """
        Return the help text that is the placeholder of the `TextInput`.
        """
        return self.element.get(key='placeholder')

    def assert_value(self, text: str):
        """
        Assert that the widget has the given value.
        """
        self._assert_attribute(name='value', value=text)


class CheckBoxInput(SimpleFormElementBase):
    """
    Tester for a checkbox input.
    """

    _tag_name = 'input'
    _attrs = {
        'type': 'checkbox'}

    @cached_property
    def label(self) -> Tag:
        """
        Return the element's HTML label tag.
        """
        return self.element.parent.parent.label

    def assert_is_checked(self):
        """
        Assert that the element's state is checked.
        """
        self.test.assertTrue(self.element.has_attr('checked'), msg=_(
            '{_my_name} \'{name}\' is not checked.').format(
            _my_name=self._my_name, name=self.attrs['name']))

    def assert_is_not_checked(self):
        """
        Assert that the element's state is checked.
        """
        self.test.assertFalse(self.element.has_attr('checked'), msg=_(
            '{_my_name} \'{name}\' is checked.').format(
            _my_name=self._my_name, name=self.attrs['name']))


class SelectInput(SimpleFormElementBase):
    """
    Tester for the select input.
    """

    _tag_name = 'select'
    _attrs = {
        'style': 'width: 100%'}

    @cached_property
    def options(self) -> List[Tuple[str, str]]:
        """
        Get the options of the select menu.
        """
        result = []
        options = self.element.find_all(name='option')
        for option in options:  # type: Tag
            result.append((option['value'], option.decode_contents()))
        return result

    @cached_property
    def selected_values(self) -> List[Tuple[str, str]]:
        """
        Return the selected options.
        """
        result = []
        options = self.element.find_all(
            name='option', attrs={'selected': True})
        for option in options:  # type: Tag
            result.append((option['value'], option.decode_contents()))
        return result

    def assert_is_multiple(self):
        """
        Assert that the select menu is a multiple select.
        """
        self.test.assertTrue(self.element.has_attr('multiple'), msg=_(
            'Select menu is not multiple selectable.'))

    def assert_is_not_multiple(self):
        """
        Assert that the select menu is a NOT multiple select.
        """
        self.test.assertFalse(self.element.has_attr('multiple'), msg=_(
            'Select menu is multiple selectable.'))

    def assert_one_selected(self, value: str, content: str=None):
        """
        Assert that the select menu has ONE option selected, and its
        value (and content) is the one passed.
        """
        if not self.selected_values:
            self.test.fail(msg=_(
                'Expected the select menu to have at least one selected '
                'option, but found none.'))
        if content is None:
            self.test.assertEqual(self.selected_values[0][0], value, msg=_(
                'Selected option differs from expected.'))
            return
        self.test.assertTupleEqual(
            tuple1=self.selected_values[0], tuple2=(value, content), msg=_(
                'Selected option differs from expected'))

    def assert_none_selected(self):
        """
        Assert that the selection in the select menu is empty.
        """
        self.test.assertListEqual(list1=self.selected_values, list2=[], msg=_(
            'Expected empty selection.'))

    def assert_multiple_selected(self, option_list: list):
        """
        Assert that the select menu has the
        """
        self.assert_is_multiple()
        self.test.assertListEqual(
            list1=self.selected_values, list2=option_list, msg=_(
                'Selection is different than what\'s expected.'))

    def assert_rendered_options(self, option_list: list):
        """
        Assert that the element has the passed options selected.
        """
        self.test.assertListEqual(list1=self.options, list2=option_list, msg=_(
            'Option list differs from expected.'))


AllWidgetTypes = Union[CheckBoxInput, TextAreaInput, TextInput, SelectInput]


class RenderFormSimpleParserBase(object):
    """
    Parse a rendered form by `render-form.html`.
    """

    def __init__(self, soup: Tag, class_: str, test: TestCase):
        """
        Find a rendered form wrapper and do assertions on its elements.
        """
        self.test = test
        classnames = 'forum-form-simple-wrapper {class_}'.format(class_=class_)
        self.soup = soup.find(name='section', class_=classnames)  # type: Tag
        self.test.assertIsInstance(obj=self.soup, cls=Tag)

    def assert_no_more_widgets(self, widgets: List[AllWidgetTypes]):
        """
        Assert that no more widgets exists in the form than the passed
        ones.
        """
        items = set()
        items.update(self.soup.find_all(name='input'))
        items.update(self.soup.find_all(name='textarea'))
        items.update(self.soup.find_all(name='select'))
        for widget in widgets:
            for item in items:  # type: Tag
                if item['name'] == widget.attrs['name']:
                    items.remove(item)
                    break
            else:
                self.test.fail(msg=_(
                    'Widget not found in rendered simple form: {widget}'
                )).format(widget=widget)
        if items:
            # There's some items remaining
            self.test.fail(msg=_(
                'After form checks, the following form names remained '
                'unchecked: {items}').format(
                items=' '.join(map(lambda x: x['name'], items))))
