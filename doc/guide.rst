.. vim: set fileencoding=utf-8 :
.. @author: Manuel Gunther <siebenkopf@googlemail.com>
.. @date:   Mon Oct 16 18:35:14 MDT 2017

==============
 User's Guide
==============

The Database Interface
----------------------

The :py:class:`bob.db.ijbc.Database` complies with the standard biometric verification database as described in `bob.db.base <bob.db.base>`.


The Database Protocols
----------------------

So far we provide 2 evaluation protocols.
The protocols ``1:1`` and the ``Covariates`` represent verification protocols.

The **identification protocols** are not implemented yet.

All of these protocols define only a ``dev`` set, while neither ``world`` not ``eval`` sets are present.
Hence, this dataset can only be used to evalaute pre-trained algorithms, or algorithms that do not require any training.



Verification Protocols
======================

In a similar manner as previous benchmarks, the protocols specify precisely which genuine and impostor comparisons should be performed.
For the ``1:1`` protocol, the number of genuine comparisons will be equal to the number of probe templates, as a single gallery template exists for each subject.
The impostor comparisons are sampled between probe templates and non-mated gallery templates under the following restriction: the two subjects represented in the gallery and probe templates have the same gender, and their skin color differs by no more than one of the six possible levels.

To fetch the object files using some protocol (let's say ``1:1``), use the following piece of code:

.. code-block:: python

   >>> import bob.db.ijbc
   >>> db = bob.db.ijbc.Database()
   >>>
   >>> # Fetching the gallery for the template '226'
   >>> dev_enroll = db.objects(protocol='1:1', groups='dev', purposes="enroll", model_ids=["226"])
   >>> # Fetching the probes that should be matched with gallery template '226'
   >>> dev_probe = db.objects(protocol='1:1', groups='dev', purposes="probe", model_ids=["226"])
   >>>

.. warning::
   As mentioned in the beginning of this subsection, each template has their own probes.
   Hence, it is mandatory to set the keyword ```model_ids``` when fetch files from this protocol.
