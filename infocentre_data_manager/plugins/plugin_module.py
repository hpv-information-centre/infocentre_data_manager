""" plugin_modules.py

This module has the implementation of the plugin module base class from where
the rest of the plugin classes are derived.

"""

from pkg_resources import iter_entry_points

__all__ = ['PluginModule', ]


class PluginModuleMeta(type):
    """ Base metaclass to make subclasses inherit docstrings from their
    parents if empty. """
    # TODO: Check efficiency
    def __new__(mcs, classname, bases, cls_dict):
        cls = super().__new__(mcs, classname, bases, cls_dict)
        for name, member in cls_dict.items():
            if (not getattr(member, '__doc__') and
                    hasattr(bases[-1], name) and
                    hasattr(getattr(bases[-1], name), '__doc__')):
                member.__doc__ = getattr(bases[-1], name).__doc__
        return cls


class PluginModule(object, metaclass=PluginModuleMeta):
    """ Base class that implements the plugin architecture. All direct
    subclasses of this module represent different stages and they have a
    factory method that scans their directory (e.g. codecs,
    data_validators, ...) and instantiates a particular subsubclass (e.g.
    ExcelCodec) with only their name (e.g. 'excel'). For new
    plugins of a particular type this doesn't require any imports; this
    class automatically scans the directory for suitable modules and
    classes."""

    @classmethod
    def _get_default_handler(cls, **kwargs):
        """
        In case no explicit plugin is specified, each plugin type can specify
        a default plugin.

        :param dict kwargs: Parameters to decide on a default
        :returns: Default plugin
        :rtype: PluginModule
        """
        raise NotImplementedError(
            'No default handlers are available for {}'.format(cls))

    @classmethod
    def get(cls, id=None, **kwargs):
        """
        Instantiates the specified plugin.

        :param str id: plugin id (e.g. 'excel', 'mysql', ...)
        :param dict kwargs: optional arguments
        :returns: Plugin
        :rtype: PluginModule
        """
        class_dict = cls.get_plugins()
        if id:
            fetcher_id = None
            try:
                # It might be a dictionary with more info, we get the type
                # from within
                if isinstance(id, dict):
                    fetcher_id = id['type']
                elif isinstance(id, str):
                    fetcher_id = id
                else:
                    raise ValueError('"id" must be a string or a dict')
            except KeyError:
                pass  # If type is not defined we try the default plugin

            try:
                return class_dict[fetcher_id](**kwargs)
            except KeyError:
                raise NotImplementedError(
                    'Plugin "{}" is not available. Check if the plugin '
                    '(or its dependencies) are installed.'.format(
                        fetcher_id
                    ))
        try:
            return cls._get_default_handler(**kwargs)
        except NotImplementedError:
            raise NotImplementedError(
                'There is no default {} for {}'.format(
                    cls.__name__, id))

    @classmethod
    def get_plugins(cls):
        """
        Returns the plugins of cls defined on the entry_point
        'data_manager.<plugin_class>'.

        :returns: Dictionary with elements {plugin_name: plugin_class}
        :rtype: dict
        """

        entry_point_group = 'data_manager.' + cls.entry_point_group
        class_dict = {}
        for entry_point in iter_entry_points(entry_point_group):
            try:
                class_dict[entry_point.name] = entry_point.load()
            except Exception as e:
                print("'{}' from '{}' not loaded:\n  {}".format(
                    entry_point.name,
                    entry_point_group,
                    str(e)))
        return class_dict
