"""Verification that compiled handbook tables in vendor/itp-ontology/handbook-tables.v1.json are up-to-date."""

import compile_handbook_tables

def test_handbook_tables_in_sync():
    assert compile_handbook_tables.main(["--check"]) == 0
