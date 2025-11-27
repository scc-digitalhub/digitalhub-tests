# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Models
"""

from __future__ import annotations

import typing
from pathlib import Path

import digitalhub as dh
from digitalhub.entities.model._base.entity import Model

if typing.TYPE_CHECKING:
    from digitalhub.entities.project._base.entity import Project


MODEL_DICTS = [
    {
        "name": "test1",
        "uuid": "d150bcca-bb64-451d-8455-dff862254b95",
        "path": "./data/my_random_forest_model.pkl",
        "kind": "model",
    },
    {
        "name": "test2",
        "uuid": "31acdd2d-0c41-428c-b68b-1b133da9e97b",
        "path": "s3://bucket/model.pkl",
        "kind": "model",
    },
]


class TestModelCRUD:
    def __init__(self, project: Project):
        self.project = project

    def test_create_delete(self):
        """Test creation and deletion via different methods."""

        for i in MODEL_DICTS:
            # Test module-level create + delete by key
            d = dh.new_model(self.project.name, **i)
            assert isinstance(d, Model)
            assert d.name == i["name"]
            assert d.kind == i["kind"]
            dh.delete_model(d.key)

            # Test module-level create + delete by name and id
            d = dh.new_model(self.project.name, **i)
            dh.delete_model(
                d.name, project=self.project.name, entity_id=d.id, cascade=False
            )

            # Test project-level create + delete
            d = self.project.new_model(**i)
            self.project.delete_model(d.key, cascade=False)

        assert dh.list_models(self.project.name) == []

    def test_list(self):
        """Test listing models."""

        assert dh.list_models(self.project.name) == []

        for i in MODEL_DICTS:
            dh.new_model(self.project.name, **i)

        l_obj = dh.list_models(self.project.name)
        assert isinstance(l_obj, list)
        assert len(l_obj) == len(MODEL_DICTS)
        for i in l_obj:
            assert isinstance(i, Model)

        for obj in l_obj:
            dh.delete_model(
                obj.name,
                project=self.project.name,
                delete_all_versions=True,
                cascade=False,
            )

        assert len(dh.list_models(self.project.name)) == 0

    def test_get(self):
        """Test getting models by different identifiers."""

        for i in MODEL_DICTS:
            o1 = dh.new_model(self.project.name, **i)
            assert isinstance(o1, Model)

            # Get by name and id
            o2 = dh.get_model(o1.name, project=self.project.name, entity_id=o1.id)
            assert isinstance(o2, Model)
            assert o1.id == o2.id

            # Get by key
            o3 = dh.get_model(o1.key)
            assert isinstance(o3, Model)
            assert o1.id == o3.id

        l_obj = dh.list_models(self.project.name)
        for obj in l_obj:
            dh.delete_model(obj.key, cascade=False)

        assert len(dh.list_models(self.project.name)) == 0

    def test_update_refresh(self):
        """Test update and refresh operations."""
        assert dh.list_models(self.project.name) == []

        # Create model
        mdl = dh.new_model(
            project=self.project.name,
            **MODEL_DICTS[0],
        )

        # Update description
        desc = "Updated description"
        mdl.metadata.description = desc
        mdl.save(update=True)

        # Verify update
        refreshed = dh.get_model(mdl.key)
        assert refreshed.metadata.description == desc

        # Test refresh method
        mdl.refresh()
        assert mdl.metadata.description == desc

        # Cleanup
        dh.delete_model(mdl.key, cascade=False)

    def test_versions(self):
        """Test versioning functionality."""

        num_versions = 3
        name = MODEL_DICTS[0]["name"]
        kind = MODEL_DICTS[0]["kind"]
        path = MODEL_DICTS[0]["path"]

        for _ in range(num_versions):
            dh.new_model(
                project=self.project.name,
                name=name,
                kind=kind,
                path=path,
            )

        versions = dh.get_model_versions(name, project=self.project.name)
        assert len(versions) == num_versions
        assert all(isinstance(v, Model) for v in versions)
        assert all(v.name == name for v in versions)

        ids = [v.id for v in versions]
        assert len(set(ids)) == num_versions

        versions_via_project = self.project.get_model_versions(name)
        assert len(versions_via_project) == num_versions

        dh.delete_model(
            name,
            project=self.project.name,
            delete_all_versions=True,
            cascade=False,
        )
        assert len(dh.list_models(self.project.name)) == 0

    def test_import_export(self):
        """Test import/export functionality."""

        # Create model
        name = MODEL_DICTS[0]["name"]
        kind = MODEL_DICTS[0]["kind"]
        description = "Test export"
        mdl = dh.new_model(
            project=self.project.name,
            **MODEL_DICTS[0],
            description=description,
        )

        export_path = mdl.export()
        assert Path(export_path).exists()

        dh.delete_model(mdl.key, cascade=False)
        assert len(dh.list_models(self.project.name)) == 0

        imported = dh.import_model(file=export_path)
        assert isinstance(imported, Model)
        assert imported.name == name
        assert imported.kind == kind
        assert imported.metadata.description == description

        dh.delete_model(imported.key, cascade=False)
        Path(export_path).unlink()

    def test_project_integration(self):
        """Test model operations via project object."""
        mdl = self.project.new_model(
            **MODEL_DICTS[0],
        )
        assert isinstance(mdl, Model)

        retrieved = self.project.get_model(mdl.key)
        assert retrieved.id == mdl.id

        models = self.project.list_models()
        assert len(models) == 1
        assert models[0].id == mdl.id

        description = "Updated via project"
        mdl.metadata.description = description
        updated = self.project.update_model(mdl)
        assert updated.metadata.description == description

        self.project.delete_model(mdl.key, cascade=False)
        assert len(self.project.list_models()) == 0
