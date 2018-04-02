#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Gunther <siebenkopf@googlemail.com>
# @date:   Mon Oct 16 18:35:14 MDT 2017

"""
This script has some sort of utility functions that parses the original database files
"""

import pkg_resources
import os

import bob.db.base
import csv
import numpy

import logging
import six

logger = logging.getLogger("bob.db.ijbc")


class Annotation:
    """
    Annotations for a File of the IJB-C dataset
    """

    def __init__(self, annots):
        # assure that we have all annotations
        assert len(annots) == 30

        # assure that a face bounding box is present
        assert not numpy.all(numpy.isnan(annots[:4]))
        self.topleft = (annots[1], annots[0])
        self.size = (annots[3], annots[2])
        self.bottomright = tuple(self.topleft[i] + self.size[i] for i in range(2))

        self.frame = None if numpy.isnan(annots[4]) else annots[4]
        self.facial_hair = None if numpy.isnan(annots[5]) else annots[5]
        self.age = None if numpy.isnan(annots[6]) else annots[6]
        self.indoor = None if numpy.isnan(annots[7]) else annots[7]
        self.skintone = None if numpy.isnan(annots[8]) else annots[8]
        self.gender = None if numpy.isnan(annots[9]) else annots[9]
        self.yaw = None if numpy.isnan(annots[10]) else annots[10]
        self.roll = None if numpy.isnan(annots[11]) else annots[11]

        self.occlusion = annots[12:30]
        self.annotation = dict(topleft=self.topleft, bottomright=self.bottomright, size=self.size)

    def __call__(self):
        return self.annotation


class File(bob.db.base.File):
    """
    IJB-C File class

    Different from its ascendant class, this one as input

    """

    @staticmethod
    def make_id(path, subject_id):
        return "%s-%s" % (path, subject_id)

    def __init__(self, subject_id, path, annotation=None):
        """**Constructor Documentation**

        Initialize the File object with the minimum required data.

        Parameters
        ----------

        subject_id : various type
          The id of the client, this file belongs to, typically the ``subject_id`` of the protocol file.

        path : str
          The path of this file, relative to the basic directory.

        annotation : :py:class:`Annotation` or ``None``
          The annotation of the file, if present
        """
        path, self.extension = os.path.splitext(path)
        super(File, self).__init__(path, self.make_id(path, subject_id))
        self.client_id = subject_id
        self.annotation = annotation

    def make_path(self, directory=None, extension=None, add_client_id=True):
        """Wraps the current path so that a complete path is formed.
        By default, the file name will be a unique file name, as there might be several ``File`` objects with the same path.
        To get the original file name, please set the ``add_client_id`` flag to ``False``.

        Keyword parameters:

        directory : str or ``None``
          An optional directory name that will be prefixed to the returned result.

        extension : str or ``None``
          An optional extension that will be suffixed to the returned filename.
          The extension normally includes the leading ``.`` character as in ``.jpg`` or ``.hdf5``.

        add_client_id : bool
          By default, the client_id is added to generate a unique path.
          If set to false, the client_id will not be added.

        Returns a string containing the newly generated file path, which by default is unique.
        """
        # assure that directory and extension are actually strings
        if directory is None: directory = ''
        if extension is None: extension = ''
        path = "%s%s" % (self.id, extension) if add_client_id else "%s%s" % (self.path, extension)
        # create the path
        return os.path.join(directory, path)


class Template:
    """A ``Template`` contains a list of :py:class:`File` objects belonging to
    the same subject (there might be several templates per subject).

    These are listed in the ``self.files`` field.

    A ``Template`` can serve for training, model enrollment, or for probing.

    Each template belongs specifically to a certain protocol, as the template_id
    in the original file lists might differ for different protocols.

    The protocol purpose can be obtained using ``self.protocol_purpose`` after
    creation of the database.

    Note that the ``template_id`` corresponds to the template_id of the file
    lists, while the ``id`` is only used as a unique key for querying the
    database.

    For convenience, the template also contains a ``path``, which is a
    concatenation of the ``File.media_id`` of the first file, and the
    ``self.template_id``, making it unique (at least per protocol).

    """

    def __init__(self, template_id, subject_id, files=None):
        self.id = template_id
        self.client_id = subject_id
        self.files = files if files is not None else []

        self.path = str(template_id)

    def __lt__(self, other):
        """This function defines the order on the Template objects. Template objects are
        always ordered by their ID, in ascending order."""
        return self.id < other.id


class Protocol:
    """The list of protocols and their according files"""

    def __init__(self):
        self.base_directory = pkg_resources.resource_filename(__name__, "protocol")
        if not os.path.isdir(self.base_directory):
            raise IOError(
                "The protocol directory %s cannot be found? Did you forget to download the protocol files with 'bob_dbmanage.py ijbc download'?" % self.base_directory)
        self._files = {}
        self._templates = {}
        self._matches = {}
        self._covariates = {}

        self.protocol_names = [
            "1:1", "Covariates"
        ]
        # TODO: Take care of other protocols
        #self.protocol_names = [
        #    "1:1", "Covariates",
        #    "1:N-G1-Image", "1:N-G2-Image", "1:N-Image",
        #    "1:N-G1-Mixed", "1:N-G2-Mixed", "1:N-Mixed",
        #    "1:N-G1-Video", "1:N-G2-Video", "1:N-Video"
        #]

        self.purpose_names = ["enroll", "probe"]

    def _read_metadata(self):
        """Reads the meta-data file if not yet done"""
        if not self._files:
            with open(os.path.join(self.base_directory, "ijbc_metadata.csv")) as p:
                reader = csv.reader(p)
                # skip header row
                six.next(reader)
                for splits in reader:
                    # generate annotations
                    annots = [float(a) for a in splits[3:]]
                    annotation = None if numpy.all(numpy.isnan(annots)) else Annotation(annots)

                    # create file
                    subject_id = None if numpy.isnan(float(splits[0])) else int(splits[0])
                    file = File(subject_id, splits[1], annotation)
                    if file.id in self._files:
                        #logger.debug("Found duplicate entry for file %s with ID %d", file.path, file.client_id)
                        x = 0
                    else:
                        self._files[file.id] = file

    def _read_template_list(self, which, protocol_file):
        if which not in self._templates:
            templates = self._templates[which] = {}
            with open(os.path.join(self.base_directory, protocol_file)) as p:
                reader = csv.reader(p)
                # skip header row
                six.next(reader)
                for splits in reader:
                    # generate file id
                    subject_id = None if numpy.isnan(float(splits[1])) else int(splits[1])
                    file_id = File.make_id(os.path.splitext(splits[2])[0], subject_id)

                    # make sure we know that file already
                    assert file_id in self._files

                    # add it to the template, or create it if not done yet
                    template_id = int(splits[0])
                    if template_id not in templates:
                        templates[template_id] = Template(template_id, subject_id)
                    templates[template_id].files.append(self._files[file_id])

                    # TODO: check that the annotations match

        return self._templates[which]

    def _read_match_file(self, protocol, protocol_file):
        if protocol not in self._matches:
            # assure that the probe is loaded
            if protocol == "1:1":
                self.get_templates(protocol, "probe")

            # read match files
            match_file = os.path.join(self.base_directory, protocol_file)
            matches = self._matches[protocol] = {}

            with open(match_file) as f:
                # read the rest of the lines
                reader = csv.reader(f)
                for splits in reader:
                    # extract basic information of the file
                    assert len(splits) == 2
                    model_id = int(splits[0])
                    probe_id = int(splits[1])
                    if model_id not in matches:
                        matches[model_id] = []
                    matches[model_id].append(probe_id)

        return self._matches[protocol]

    def get_templates(self, protocol, purpose=None):
        """Returns all :py:class:`Template`'s for the given protocol and purpose."""
        assert protocol in self.protocol_names
        assert purpose in self.purpose_names
        # read metadata if not done yet
        self._read_metadata()

        if protocol == "Covariates":
            # for the covariates, we do not use the default gallery
            if not self._covariates:
                # first, read all templates
                self._read_template_list("Covariates", "ijbc_11_covariate_probe_reference.csv")
                # and now split them into model and probe (overlapping)
                matches = self._read_match_file("Covariates", "ijbc_11_covariate_matches.csv")
                self._covariates["enroll"] = {x: self._templates["Covariates"][x] for x in matches}
                self._covariates["probe"] = {x: self._templates["Covariates"][x] for x in
                                             set(p for m in matches.keys() for p in matches[m])}
            return self._covariates[purpose]

        elif purpose == "enroll":
            # otherwise, we have the same templates for enrollment, throughout
            if "S2" not in protocol: self._read_template_list("G1", "ijbc_1N_gallery_G1.csv")
            if "S1" not in protocol: self._read_template_list("G2", "ijbc_1N_gallery_G2.csv")

            if "S1" in protocol:
                return self._templates["G1"]
            elif "S2" in protocol:
                return self._templates["G2"]
            else:
                if "S1S2" not in self._templates:
                    self._templates["G1G2"] = self._templates["G1"].copy()
                    self._templates["G1G2"].update(self._templates["G2"])
                return self._templates["G1G2"]

        else:
            # probes for 1:N protocol
            if "Image" in protocol:
                return self._read_template_list("Image", "ijbc_1N_probe_img.csv")
            elif "Video" in protocol:
                return self._read_template_list("Video", "ijbc_1N_probe_video.csv")
            else:
                # This file is used for both the 1:1 protocol (as probes) and the 1:N-Mixed protocols
                return self._read_template_list("Mixed", "ijbc_1N_probe_mixed.csv")

    def enroll_template(self, protocol, model_id):
        """Returns the enrollment template for the given model_id"""
        templates = self.get_templates(protocol=protocol, purpose="enroll")
        assert model_id in templates, "The given model id '%s' is not a gallery template ID" % model_id
        return templates[model_id]

    def probe_templates(self, protocol, model_id):
        """Returns the probe templates for the given model_id"""
        if protocol == "1:1":
            matches = self._read_match_file("1:1", "ijbc_11_G1_G2_matches.csv")[model_id]
            return [self._templates["Mixed"][m] for m in matches]
        elif protocol == "Covariates":
            matches = self._read_match_file("Covariates", "ijbc_11_covariate_matches.csv")[model_id]
            return [self._templates["Covariates"][m] for m in matches]
        else:
            # for 1:N protocols, return all probe files
            return self.get_templates(protocol, "probe").values()
