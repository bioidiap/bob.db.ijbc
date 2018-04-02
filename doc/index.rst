.. vim: set fileencoding=utf-8 :
.. @author: Manuel Gunther <siebenkopf@googlemail.com>
.. @date:   Mon Oct 16 18:35:14 MDT 2017

.. _bob.db.ijbc:

====================================================
 IARPA Janus Benchmark C (IJB-C) Database Interface
====================================================

This package contains the access API and descriptions for the IARPA Janus Benchmark C -- IJB-C database.
The actual raw data can be downloaded from the original web page: http://www.nist.gov/programs-projects/face-challenges (note that not everyone might be eligible for downloading the data).

Included in the database, there are list files defining verification as well as closed- and open-set identification protocols.
For verification, two different protocols are provided.
For the ``1:1`` protocol, gallery and probe templates are combined using several images and video frames for each subject.
For the ``Covariates`` protocol, gallery and probes consist of a single image or frame only.
In either protocol, compared gallery and probe templates share the same gender and skin tone -- these have been matched to make the comparisions more realistic and difficult.

For closed-set identification, the gallery of the ``1:1`` protocol is used, while probes stem from either only images, mixed images and video frames, or plain videos.
For open-set identification, the same probes are evaluated, but the gallery is split into two parts, either of which is left out to provide unknown probe templates, i.e., probe templates with no matching subject in the gallery.
In any case, scores are computed between all (active) gallery templates and all probes.

The IJB-C dataset provides additional evaluation protocols for face detection and clustering, but these are (not yet) part of this interface.

Documentation
-------------

.. toctree::
   :maxdepth: 2

   guide
   py_api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
