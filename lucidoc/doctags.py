""" Handling the tags in docstrings """

import abc

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"

__all__ = ["DocTag", "ErrTag", "ParTag", "RetTag", "TagRenderer", "MdTagRenderer"]


class DocTag(object):
    """ Representation of a tag within a docstring """
    __metaclass__ = abc.ABCMeta

    def __init__(self, typename, description):
        self._tn = typename
        self._desc = description

    @property
    def typename(self):
        """
        Get the name of the type(s) associated with the tag

        :return str: Text of either single type name or union of several
        """
        return self._tn

    @property
    def description(self):
        """
        Described value to which this tag pertains

        :return str: description of value being tagged
        """
        return self._desc

    def __str__(self):
        return "{cn}({tn}: {d})".format(
            cn=self.__class__.__name__, tn=self.typename, d=self.description)


class ParTag(DocTag):
    """ Representation of a parameter tag in docstring """

    def __init__(self, name, typename, description):
        """
        Create a parameter tag with a name, typename, and description.

        :param str name: the formal parameter name
        :param typename: text describing valid argument types
        :param description: detail about the parameter and/or accepted args
        """
        super(ParTag, self).__init__(typename, description)
        self._name = name

    @property
    def name(self):
        """
        Get the parameter name.

        :return str: The parameter name for this tag
        """
        return self._name

    def __str__(self):
        return "{cn}({tn} {n}: {d})".format(
            cn=self.__class__.__name__, tn=self.typename, n=self.name,
            d=self.description)


class RetTag(DocTag):
    """ Tag for type and description of return value """
    pass


class ErrTag(DocTag):
    """ Tag for type and description of a potential Exception """
    pass


class TagRenderer(object):
    """ Strategy for rendering a tag. """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self, t, *args, **kwargs):
        """
        Render the given tag.

        :param lucidoc.DocTag t: tag to render
        :return str: rendition of the given tag
        """
        pass


class MdTagRenderer(TagRenderer):
    """ Render tag for Markdown """

    def __call__(self, t, *args, **kwargs):
        """
        Render the given tag.

        :param lucidoc.DocTag t: tag to render
        :return str: rendition of the given tag
        """
        if isinstance(t, ParTag):
            return "- `{}` (`{}`): {}".format(t.name, t.typename, t.description)
        elif isinstance(t, RetTag):
            return "- `{}`: {}".format(t.typename, t.description)
        elif isinstance(t, ErrTag):
            return "- `{}`: {}".format(t.typename, t.description)
        else:
            raise TypeError("Invalid tag type: {}".format(type(t)))
