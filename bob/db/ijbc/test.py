#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Gunther <siebenkopf@googlemail.com>
# @date:   Mon Oct 16 18:35:14 MDT 2017

"""A few checks for the IJB-C database.
"""
import pkg_resources
import os, sys
import bob.db.ijbc
import nose.tools
import random

# we create only a single instance of the database, to avoid loading file-lists over and over
db = bob.db.ijbc.Database()


# all the numbers from below have been estimated from the original protocol files using an external script

def test_clients():
    # The number of groups
    assert len(db.groups(protocol='1:1')) == 1
    assert len(db.protocol_names()) == 2
    #assert len(db.protocol_names()) == 11

    # test that the expected number of clients/client_ids is returned; the values are according to the Protocol Description
    for protocol in db.protocol_names():
        #import ipdb; ipdb.set_trace();
        # number of clients differ between protocols
        #client_ids = 931 if "G1" in protocol else 914 if "G2" in protocol else 1817 if protocol == "Covariates" else 3531
        #client_ids = 1817 if protocol == "Covariates" else 3531
        client_ids = 3531
        assert len(db.client_ids(protocol=protocol)) == client_ids
        # number of models is only different for the covariates protocol
        assert len(db.model_ids(protocol=protocol)) == (140739 if protocol == "Covariates" else client_ids)


def test_verification():
    # protocol 1:1
    # .. number of probe templates
    assert len(db.object_sets(protocol="1:1")) == 19593

    # .. number of scores, i.e., number of lines in ijbc_11_S1_S2_matches.csv
    assert sum(len(db.object_sets(protocol="1:1", model_ids=model_id, purposes='probe')) for model_id in
               db.model_ids()) == 15658489

    # .. maximum number of enroll files per model < 58
    assert all(len(db.objects(protocol="1:1", model_ids=model_id, purposes='enroll')) < 58 for model_id in
               db.model_ids(protocol="1:1"))

    # .. all probe files
    assert len(db.objects(protocol="1:1", purposes='probe')) == 128876


def test_covariates():
    # protocol Covariates
    # .. number of unique probe templates (by accident identical to number of models)
    assert len(db.objects(protocol="Covariates")) == 140739

    # .. number of scores, i.e., number of lines in ijbc_11_covariate_matches.csv
    assert sum(len(db.objects(protocol="Covariates", model_ids=model_id, purposes='probe')) for model_id in
               db.model_ids(protocol="Covariates")) == 47404001

    # .. number of enroll files per model is exactly 1
    assert all(len(db.objects(protocol="Covariates", model_ids=model_id, purposes='enroll')) == 1 for model_id in
               db.model_ids(protocol="Covariates"))


"""
def test_identification():
    # 1:N protocols
    for protocol in ("1:N-S1-Image", "1:N-S2-Image", "1:N-Image"):
        # .. number of probes is identical for all models
        assert all(len(db.objects(protocol=protocol, model_ids=model_id, purposes="probe")) == 5999 for model_id in
                   random.sample(db.model_ids(protocol=protocol), 100))
        assert all(len(db.object_sets(protocol=protocol, model_ids=model_id, purposes="probe")) == 8104 for model_id in
                   db.model_ids(protocol=protocol))

    for protocol in ("1:N-S1-Mixed", "1:N-S2-Mixed", "1:N-Mixed"):
        assert all(len(db.objects(protocol=protocol, model_ids=model_id, purposes="probe")) == 61494 for model_id in
                   random.sample(db.model_ids(protocol=protocol), 100))
        assert all(len(db.object_sets(protocol=protocol, model_ids=model_id, purposes="probe")) == 10270 for model_id in
                   db.model_ids(protocol=protocol))

    for protocol in ("1:N-S1-Video", "1:N-S2-Video", "1:N-Video"):
        assert all(len(db.objects(protocol=protocol, model_ids=model_id, purposes="probe")) == 7110 for model_id in
                   random.sample(db.model_ids(protocol=protocol), 100))
        assert all(len(db.object_sets(protocol=protocol, model_ids=model_id, purposes="probe")) == 7110 for model_id in
                   db.model_ids(protocol=protocol))

"""

def test_annotations():
    # Tests that the annotations are available for all files
    all_keys = set(['topleft', 'size', 'bottomright', 'nose'])

    # we test only one of the protocols
    for protocol in db.protocol_names():
        # ...and some of the files
        for file in random.sample(db.objects(protocol=protocol), 1000):
            annotations = db.annotations(file)
            if annotations is None:
                assert "nonface" in file.path
            else:
                assert 'topleft' in annotations and 'size' in annotations and 'bottomright' in annotations, "Annotations '%s' of file '%s' are incomplete" % (
                annotations, file.path)
                assert len(annotations['topleft']) == 2
                assert len(annotations['bottomright']) == 2
                assert set(annotations.keys()).issubset(all_keys)


def notest_driver_api():
    # Tests the bob_dbmanage.py driver interface
    from bob.db.base.script.dbmanage import main
    assert main(('ijbc dumplist --database-directory %s --protocol-directory %s --self-test' % (
    database_directory, protocol_directory)).split()) == 0
    assert main((
                'ijbc dumplist --database-directory %s --protocol-directory %s --purpose=probe --template-id=11068 --protocol=1:N-Mixed --self-test' % (
                database_directory, protocol_directory)).split()) == 0
    assert main(('ijbc checkfiles --database-directory %s --protocol-directory %s --self-test' % (
    database_directory, protocol_directory)).split()) == 0
