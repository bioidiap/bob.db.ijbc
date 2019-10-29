.. vim: set fileencoding=utf-8 :
.. Thu 18 Aug 13:44:41 CEST 2016

.. image:: http://img.shields.io/badge/docs-v1.0.2-yellow.svg
   :target: http://pythonhosted.org/bob.db.ijbc/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.svg
   :target: http://beatubulatest.lab.idiap.ch/private/docs/bob/bob.db.ijbc/master/index.html
.. image:: https://gitlab.idiap.ch/bob/bob.db.ijbc/badges/v1.0.2/build.svg
   :target: https://gitlab.idiap.ch/bob/bob.db.ijbc/commits/v1.0.2
.. image:: https://img.shields.io/badge/gitlab-project-0000c0.svg
   :target: https://gitlab.idiap.ch/bob/bob.db.ijbc


==================================
 IJB-C Database Interface for Bob
==================================

This package is part of the signal-processing and machine learning toolbox
Bob_.  This package contains an interface for the evaluation protocols of the
`IARPA Janus Benchmark C (IJB-C) database`_ and does not contain the original
image data for the database.  The original data should be obtained using the
link above.

The IJB-C database is a mixture of frontal and non-frontal images and videos
(provided as single frames) from 1845 different identities.  In many of the
images and video frames, there are several people visible, but only the ones
that are annotated with a bounding box should be taken into consideration. For
both model enrollment as well as for probing, images and video frames of one
person are combined into so-called Templates. For some of the protocols, probe
templates are also generated from raw video data.

This package implements the database interface including all its
particularities:

- First, it implements the FileSet protocol, since for some probes, several
  files (a mixture of images and/or video frames) are defined. In the
  Database.object_sets() function, FileSet objects are only returned for probe
  purposes.
- Second, some images contain several identities. Therefore, every physical
  image file can be stored in several File objects. Also, the File.make_path()
  function can create two different styles of file names: the original file
  name (to read original images), or a unique filename (to define a unique name
  for each extracted face).


Installation
------------

Follow our `installation`_ instructions. Then, using the Python interpreter
provided by the distribution and buildout this package::

  $ buildout


Contact
-------

For questions or reporting issues to this software package, contact our
development `mailing list`_.


.. Place your references here:
.. _bob: https://www.idiap.ch/software/bob
.. _installation: https://www.idiap.ch/software/bob/install
.. _mailing list: https://www.idiap.ch/software/bob/discuss
.. _iarpa janus benchmark c (ijb-c) database: https://www.nist.gov/programs-projects/face-challenges
