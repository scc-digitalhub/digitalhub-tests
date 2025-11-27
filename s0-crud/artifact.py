# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Artifact
"""

from __future__ import annotations

import typing
from pathlib import Path

import digitalhub as dh
from digitalhub.entities.artifact._base.entity import Artifact

if typing.TYPE_CHECKING:
    from digitalhub.entities.project._base.entity import Project


ARTIFACT_DICTS = [
    {
        "name": "test1",
        "uuid": "d150bcca-bb64-451d-8455-dff862254b95",
        "path": "./data/test.csv",
        "kind": "artifact",
    },
    {
        "name": "test2",
        "uuid": "31acdd2d-0c41-428c-b68b-1b133da9e97b",
        "path": "s3://bucket/key.csv",
        "kind": "artifact",
    },
    {
        "name": "test4",
        "uuid": "2618d9c4-cd61-440f-aebb-7e5761709f3b",
        "path": "https://url.com/file.csv",
        "kind": "artifact",
    },
]


class TestArtifactCRUD:
    def __init__(self, project: Project):
        self.project = project

    def test_create_delete(self):
        """Test creation and deletion via different methods."""

        # Create and delete artifacts using different approaches
        for i in ARTIFACT_DICTS:
            # Test module-level create + delete by key
            d = dh.new_artifact(self.project.name, **i)
            assert isinstance(d, Artifact)
            assert d.name == i["name"]
            assert d.kind == i["kind"]
            dh.delete_artifact(d.key, cascade=False)

            # Test module-level create + delete by name and id
            d = dh.new_artifact(self.project.name, **i)
            dh.delete_artifact(
                d.name,
                project=self.project.name,
                entity_id=d.id,
                cascade=False,
            )

            # Test project-level create + delete
            d = self.project.new_artifact(**i)
            self.project.delete_artifact(
                d.key,
                cascade=False,
            )

        assert dh.list_artifacts(self.project.name) == []

    def test_list(self):
        assert dh.list_artifacts(self.project.name) == []

        for i in ARTIFACT_DICTS:
            dh.new_artifact(self.project.name, **i)

        # List artifacts
        l_obj = dh.list_artifacts(self.project.name)
        assert isinstance(l_obj, list)
        assert len(l_obj) == len(ARTIFACT_DICTS)
        for i in l_obj:
            assert isinstance(i, Artifact)

        # Delete all artifacts - test delete_all_versions
        for obj in l_obj:
            dh.delete_artifact(
                obj.key,
                delete_all_versions=True,
                cascade=False,
            )

        assert len(dh.list_artifacts(self.project.name)) == 0

    def test_update_refresh(self):
        """Test update and refresh operations."""
        assert dh.list_artifacts(self.project.name) == []

        # Create artifact
        art = dh.new_artifact(
            project=self.project.name,
            **ARTIFACT_DICTS[0],
        )

        # Update description
        desc = "Updated description"
        art.metadata.description = desc
        art.save(update=True)

        # Verify update
        refreshed = dh.get_artifact(art.key)
        assert refreshed.metadata.description == desc

        # Test refresh method
        art.refresh()
        assert art.metadata.description == desc

        # Cleanup
        dh.delete_artifact(art.key, cascade=False)

    def test_versions(self):
        """Test versioning functionality."""

        num_versions = 3
        name = ARTIFACT_DICTS[0]["name"]
        kind = ARTIFACT_DICTS[0]["kind"]
        path = ARTIFACT_DICTS[0]["path"]
        for _ in range(num_versions):
            dh.new_artifact(
                project=self.project.name,
                name=name,
                kind=kind,
                path=path,
            )

        # Get all versions
        versions = dh.get_artifact_versions(
            name,
            project=self.project.name,
        )
        assert len(versions) == num_versions
        assert all(isinstance(v, Artifact) for v in versions)
        assert all(v.name == name for v in versions)

        # Verify different IDs
        ids = [v.id for v in versions]
        assert len(set(ids)) == num_versions

        # Test project method
        versions_via_project = self.project.get_artifact_versions(name)
        assert len(versions_via_project) == num_versions

        # Cleanup - delete all versions
        dh.delete_artifact(
            name,
            project=self.project.name,
            delete_all_versions=True,
            cascade=False,
        )
        assert len(dh.list_artifacts(self.project.name)) == 0

    def test_import_export(self):
        """Test import/export functionality."""

        # Create artifact
        name = ARTIFACT_DICTS[0]["name"]
        kind = ARTIFACT_DICTS[0]["kind"]
        description = "Test export"
        art = dh.new_artifact(
            project=self.project.name,
            **ARTIFACT_DICTS[0],
            description=description,
        )

        # Export to YAML
        export_path = art.export()
        assert Path(export_path).exists()

        # Delete original
        dh.delete_artifact(art.key, cascade=False)
        assert len(dh.list_artifacts(self.project.name)) == 0

        # Import back
        imported = dh.import_artifact(file=export_path)
        assert isinstance(imported, Artifact)
        assert imported.name == name
        assert imported.kind == kind
        assert imported.metadata.description == description

        # Cleanup
        dh.delete_artifact(imported.key)
        Path(export_path).unlink()

    def test_project_integration(self):
        """Test artifact operations via project object."""
        # Test all project methods
        art = self.project.new_artifact(
            **ARTIFACT_DICTS[0],
        )
        assert isinstance(art, Artifact)

        # Get via project
        retrieved = self.project.get_artifact(art.key)
        assert retrieved.id == art.id

        # List via project
        artifacts = self.project.list_artifacts()
        assert len(artifacts) == 1
        assert artifacts[0].id == art.id

        # Update via project
        description = "Updated via project"
        art.metadata.description = description
        updated = self.project.update_artifact(art)
        assert updated.metadata.description == description

        # Delete via project
        self.project.delete_artifact(art.key, cascade=False)
        assert len(self.project.list_artifacts()) == 0

    def test_get(self):
        for i in ARTIFACT_DICTS:
            o1 = dh.new_artifact(self.project.name, **i)
            assert isinstance(o1, Artifact)

            # Get by name and id
            o2 = dh.get_artifact(o1.name, project=self.project.name, entity_id=o1.id)
            assert isinstance(o2, Artifact)
            assert o1.id == o2.id

            # Get by key
            o3 = dh.get_artifact(o1.key)
            assert isinstance(o3, Artifact)
            assert o1.id == o3.id

        # delete listed objects
        l_obj = dh.list_artifacts(self.project.name)
        for obj in l_obj:
            dh.delete_artifact(obj.key, cascade=False)

        assert len(dh.list_artifacts(self.project.name)) == 0
