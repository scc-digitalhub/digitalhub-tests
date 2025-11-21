# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Dataitem
"""

from __future__ import annotations

import typing
from pathlib import Path

import digitalhub as dh
from digitalhub.entities.dataitem._base.entity import Dataitem

if typing.TYPE_CHECKING:
    from digitalhub.entities.project._base.entity import Project


DATAITEM_DICTS = [
    {
        "name": "test1",
        "uuid": "d150bcca-bb64-451d-8455-dff862254b95",
        "path": "./data/test.csv",
        "kind": "dataitem",
    },
    {
        "name": "test2",
        "uuid": "31acdd2d-0c41-428c-b68b-1b133da9e97b",
        "path": "s3://bucket/key.csv",
        "kind": "dataitem",
    },
    {
        "name": "test3",
        "uuid": "b4a3dfdc-b917-44c4-9a29-613dcf734244",
        "path": "sql://database/schema/table",
        "kind": "dataitem",
    },
    {
        "name": "test4",
        "uuid": "2618d9c4-cd61-440f-aebb-7e5761709f3b",
        "path": "https://url.com/file.csv",
        "kind": "dataitem",
    },
]


class TestDataitemCRUD:
    def __init__(self, project: Project):
        self.project = project

    def test_create_delete(self):
        """Test creation and deletion via different methods."""

        for i in DATAITEM_DICTS:
            # Test module-level create + delete by key
            d = dh.new_dataitem(self.project.name, **i)
            assert isinstance(d, Dataitem)
            assert d.name == i["name"]
            assert d.kind == i["kind"]
            dh.delete_dataitem(d.key)

            # Test module-level create + delete by name and id
            d = dh.new_dataitem(self.project.name, **i)
            dh.delete_dataitem(d.name, project=self.project.name, entity_id=d.id)

            # Test project-level create + delete
            d = self.project.new_dataitem(**i)
            self.project.delete_dataitem(d.key)

        assert dh.list_dataitems(self.project.name) == []

    def test_list(self):
        """Test listing dataitems."""

        assert dh.list_dataitems(self.project.name) == []

        for i in DATAITEM_DICTS:
            dh.new_dataitem(self.project.name, **i)

        l_obj = dh.list_dataitems(self.project.name)
        assert isinstance(l_obj, list)
        assert len(l_obj) == len(DATAITEM_DICTS)
        for i in l_obj:
            assert isinstance(i, Dataitem)

        for obj in l_obj:
            dh.delete_dataitem(
                obj.name, project=self.project.name, delete_all_versions=True
            )

        assert len(dh.list_dataitems(self.project.name)) == 0

    def test_get(self):
        """Test getting dataitems by different identifiers."""

        for i in DATAITEM_DICTS:
            o1 = dh.new_dataitem(self.project.name, **i)
            assert isinstance(o1, Dataitem)

            # Get by name and id
            o2 = dh.get_dataitem(o1.name, project=self.project.name, entity_id=o1.id)
            assert isinstance(o2, Dataitem)
            assert o1.id == o2.id

            # Get by key
            o3 = dh.get_dataitem(o1.key)
            assert isinstance(o3, Dataitem)
            assert o1.id == o3.id

        l_obj = dh.list_dataitems(self.project.name)
        for obj in l_obj:
            dh.delete_dataitem(obj.key)

        assert len(dh.list_dataitems(self.project.name)) == 0

    def test_update_refresh(self):
        """Test update and refresh operations."""
        assert dh.list_dataitems(self.project.name) == []

        # Create dataitem
        di = dh.new_dataitem(
            project=self.project.name,
            **DATAITEM_DICTS[0],
        )

        # Update description
        desc = "Updated description"
        di.metadata.description = desc
        di.save(update=True)

        # Verify update
        refreshed = dh.get_dataitem(di.key)
        assert refreshed.metadata.description == desc

        # Test refresh method
        di.refresh()
        assert di.metadata.description == desc

        # Cleanup
        dh.delete_dataitem(di.key)

    def test_versions(self):
        """Test versioning functionality."""

        num_versions = 3
        name = DATAITEM_DICTS[0]["name"]
        kind = DATAITEM_DICTS[0]["kind"]
        path = DATAITEM_DICTS[0]["path"]

        for _ in range(num_versions):
            dh.new_dataitem(
                project=self.project.name,
                name=name,
                kind=kind,
                path=path,
            )

        versions = dh.get_dataitem_versions(name, project=self.project.name)
        assert len(versions) == num_versions
        assert all(isinstance(v, Dataitem) for v in versions)
        assert all(v.name == name for v in versions)

        ids = [v.id for v in versions]
        assert len(set(ids)) == num_versions

        versions_via_project = self.project.get_dataitem_versions(name)
        assert len(versions_via_project) == num_versions

        dh.delete_dataitem(
            name,
            project=self.project.name,
            delete_all_versions=True,
        )
        assert len(dh.list_dataitems(self.project.name)) == 0

    def test_import_export(self):
        """Test import/export functionality."""

        # Create dataitem
        name = DATAITEM_DICTS[0]["name"]
        kind = DATAITEM_DICTS[0]["kind"]
        description = "Test export"
        di = dh.new_dataitem(
            project=self.project.name,
            **DATAITEM_DICTS[0],
            description=description,
        )

        export_path = di.export()
        assert Path(export_path).exists()

        dh.delete_dataitem(di.key)
        assert len(dh.list_dataitems(self.project.name)) == 0

        imported = dh.import_dataitem(file=export_path)
        assert isinstance(imported, Dataitem)
        assert imported.name == name
        assert imported.kind == kind
        assert imported.metadata.description == description

        dh.delete_dataitem(imported.key)
        Path(export_path).unlink()

    def test_project_integration(self):
        """Test dataitem operations via project object."""
        di = self.project.new_dataitem(
            **DATAITEM_DICTS[0],
        )
        assert isinstance(di, Dataitem)

        retrieved = self.project.get_dataitem(di.key)
        assert retrieved.id == di.id

        dataitems = self.project.list_dataitems()
        assert len(dataitems) == 1
        assert dataitems[0].id == di.id

        description = "Updated via project"
        di.metadata.description = description
        updated = self.project.update_dataitem(di)
        assert updated.metadata.description == description

        self.project.delete_dataitem(di.key)
        assert len(self.project.list_dataitems()) == 0
