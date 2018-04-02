#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Gunther <siebenkopf@googlemail.com>
# @date:   Mon Oct 16 18:35:14 MDT 2017

"""This module provides the Database interface allowing the user to query the JANUS database.
"""

from .reader import *
import bob.db.base


class Database(bob.db.base.Database):
    """The database class opens and maintains a connection opened to the Database.

    It provides many different ways to probe for the characteristics of the data
    and for the data itself inside the database.
    """

    def __init__(self,
                 original_directory=None,
                 check_valid=True
                 ):
        # call base class constructor
        super(Database, self).__init__(original_directory=original_directory, original_extension=None)

        self.protocol = Protocol()

    def provides_file_set_for_protocol(self, protocol):
        """Returns ``True`` for 1:1 and 1:N-... protocols, otherwise ``False``

        Keyword Parameters:

        protocol
          The protocol to evaluate.
        """
        return protocol.startswith("1:")

    def groups(self, protocol=None):
        return ("dev",)

    def client_ids(self, groups='dev', protocol=None):
        """Returns a list of client ids (aka. subject_id) for the specific query by the user.

        Keyword Parameters:

        groups
          Ignored; `'dev'` is asssumed.

        protocol
          One of the protocols of the dataset; identical for all protocols starting with ``1:``

        Returns: A list containing all the client ids which have the desired properties.
        """
        # retrieve enroll templates
        templates = self.protocol.get_templates(protocol, purpose="enroll")
        client_ids = set(template.client_id for template in templates.values())
        return sorted(client_ids)

    def model_ids(self, groups='dev', protocol="1:1"):
        """Returns a list of model ids for the specific query by the user.

        Keyword Parameters:

        groups
          Ignored; ``'dev'`` is assumed

        protocol
          One of the protocols of the dataset; identical for all protocols starting with ``1:``

        Returns: A list containing all the model ids.
        """
        protocol = self.check_parameter_for_validity(protocol, "protocol", self.protocol_names())

        # retrieve templates
        templates = self.protocol.get_templates(protocol, "enroll")
        # get keys of templates, which are the template ids
        return sorted(list(templates.keys()))

    def get_client_id_from_model_id(self, protocol, model_id):
        """Returns the client_id attached to the given model_id

        Keyword Parameters:

        protocol
          One of the protocols of the dataset; identical for all protocols starting with ``1:``

        model_id
          The model id (i.e., the template id of a gallery template) to consider

        Returns: The client_id attached to the given model_id
        """
        # try to find the client id for the given model id in any previously read file
        protocol = self.check_parameter_for_validity(protocol, "protocol", self.protocol_names())
        return self.protocol.enroll_template(protocol, model_id).client_id

    def get_model_ids_from_client_id(self, protocol, purpose, client_id):
        """Returns the model ids (templates) for the given client_id

        Keyword Parameters:

        client_id
          The client id

        Returns: The list of model ids (template ids) of the client
        """
        # try to find the client id for the given model id in any previously read file
        protocol = self.check_parameter_for_validity(protocol, "protocol", self.protocol_names())
        purpose = self.check_parameter_for_validity(purpose, "purpose", ("enroll", "probe"))

        return self.uniquify(
            t.id for t in self.protocol.get_templates(protocol, purpose).values() if t.client_id == client_id)

    def objects(self, groups='dev', protocol=None, purposes=None, model_ids=None):
        """Using the specified restrictions, this function returns a list of :py:class:`File` objects.

        Keyword Parameters:

        groups
          Ignored; ``'dev'`` is assumed

        protocol : str or ``None``
          One or more of the available protocol names, see :py:meth:`protocol_names`.
          If not specified, all protocols will be assumed.

        purposes : str or [str] or ``None``
          One or several purposes for which files should be retrieved ('enroll', 'probe').
          Note: this field is ignored for group 'world'.

        model_ids : int or [int] or ``None``
          If given (as a list of model id's or a single one), only the files belonging to the specified model id is returned.
          For 'probe' purposes, the probe images belonging to the given model ids are returned.
        """

        # check that every parameter is as expected
        protocols = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names())
        purposes = self.check_parameters_for_validity(purposes, "purpose", ("enroll", "probe"))

        # assure that the given model ids are in an iterable container
        if isinstance(model_ids, int): model_ids = (model_ids,)

        # collect the templates, and filter them by the given criteria
        templates = set()
        if 'enroll' in purposes:
            for protocol in protocols:
                if model_ids:
                    for model_id in model_ids:
                        templates.add(self.protocol.enroll_template(protocol, model_id))
                else:
                    templates.update(self.protocol.get_templates(protocol, "enroll").values())

        if 'probe' in purposes:
            for protocol in protocols:
                if model_ids:
                    for model_id in model_ids:
                        templates.update(self.protocol.probe_templates(protocol, model_id))
                else:
                    templates.update(self.protocol.get_templates(protocol, "probe").values())

        # get a unique set of files
        files = set(file for template in templates for file in template.files)

        # now, collect all files and return them
        return files

    def object_sets(self, groups='dev', protocol=None, purposes='probe', model_ids=None):
        """Using the specified restrictions, this function returns a list of :py:class:`Template` objects.

        Keyword Parameters:

        groups : str or [str]
          Only the 'dev' group is accepted.

        protocol : str
          One of the available protocol names, see :py:meth:`protocol_names`.

        purposes
          Ignored; ``'probe'`` is assumed.

        model_ids : int or [int] or ``None``
          If given, the probe templates belonging to the given model ids are returned.
        """

        # check that every parameter is as expected
        protocol = self.check_parameter_for_validity(protocol, "protocol",
                                                     [p for p in self.protocol_names() if p != "Covariates"])
        groups = self.check_parameters_for_validity(groups, "group", self.groups(protocol))

        # assure that the given model ids are in an iteratable container
        if isinstance(model_ids, int): model_ids = (model_ids,)

        # collect the templates, and filter them by the given criteria
        templates = set()
        if model_ids:
            for model_id in model_ids:
                templates.update(self.protocol.probe_templates(protocol, model_id))
        else:
            templates.update(self.protocol.get_templates(protocol, "probe").values())

        # return list of all templates
        return templates

    def templates(self, groups='dev', protocol=None):
        """Returns all templates (enrollment and probe) for the given protocol """
        templates = {}
        templates.update(self.protocol.get_templates(protocol, "enroll"))
        templates.update(self.protocol.get_templates(protocol, "probe"))
        return templates.values()

    def annotations(self, file):
        """Returns the annotations for the given :py:class:`File` object as a dictionary, see :py:class:`Annotation` for details."""
        return None if file.annotation is None else file.annotation()

    def protocol_names(self):
        """Returns all registered protocol names, including ``['1:1', 'Covariates', '1:N-Mixed']``"""
        return self.protocol.protocol_names

    def original_file_name(self, file, check_existence=True):
        """Returns the original image file name with the correct file name extension.
        To be able to call this function, the ``original_directory`` must have been specified in the :py:class:`Database` constructor.

        Keyword parameters:

        file : :py:class:`File`
          The ``File`` object to get the original file name from.

        check_existence : bool
          If set to True (the default), the existence of the original image file is checked, prior to returning the files name.
        """
        if not self.original_directory:
            raise ValueError("The original_directory was not specified in the constructor.")
        # extract file name
        file_name = file.make_path(self.original_directory, file.extension, add_client_id=False)
        if not check_existence or os.path.exists(file_name):
            return file_name
        raise ValueError("The file '%s' was not found. Please check the original directory '%s'?" % (
        file_name, self.original_directory))
