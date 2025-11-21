# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Workflow
"""

from __future__ import annotations

import typing
from pathlib import Path

import digitalhub as dh
from digitalhub.entities.workflow._base.entity import Workflow

if typing.TYPE_CHECKING:
    from digitalhub.entities.project._base.entity import Project


WORKFLOW_DICTS = [
    {
        "name": "test1",
        "uuid": "d150bcca-bb64-451d-8455-dff862254b95",
        "kind": "hera",
        "code": "def pipeline(): pass",
        "handler": "pipeline",
    },
    {
        "name": "test2",
        "uuid": "31acdd2d-0c41-428c-b68b-1b133da9e97b",
        "kind": "hera",
        "code": "def pipeline(): pass",
        "handler": "pipeline",
    },
]


class TestWorkflowCRUD:
    def __init__(self, project: Project):
        self.project = project

    def test_create_delete(self):
        """Test creation and deletion via different methods."""

        for i in WORKFLOW_DICTS:
            # Test module-level create + delete by key
            w = dh.new_workflow(self.project.name, **i)
            assert isinstance(w, Workflow)
            assert w.name == i["name"]
            assert w.kind == i["kind"]
            dh.delete_workflow(w.key)

            # Test module-level create + delete by name and id
            w = dh.new_workflow(self.project.name, **i)
            dh.delete_workflow(w.name, project=self.project.name, entity_id=w.id)

            # Test project-level create + delete
            w = self.project.new_workflow(**i)
            self.project.delete_workflow(w.key)

        assert dh.list_workflows(self.project.name) == []

    def test_list(self):
        """Test listing workflows."""

        assert dh.list_workflows(self.project.name) == []

        for i in WORKFLOW_DICTS:
            dh.new_workflow(self.project.name, **i)

        l_obj = dh.list_workflows(self.project.name)
        assert isinstance(l_obj, list)
        assert len(l_obj) == len(WORKFLOW_DICTS)
        for i in l_obj:
            assert isinstance(i, Workflow)

        for obj in l_obj:
            dh.delete_workflow(
                obj.name, project=self.project.name, delete_all_versions=True
            )

        assert len(dh.list_workflows(self.project.name)) == 0

    def test_get(self):
        """Test getting workflows by different identifiers."""

        for i in WORKFLOW_DICTS:
            o1 = dh.new_workflow(self.project.name, **i)
            assert isinstance(o1, Workflow)

            # Get by name and id
            o2 = dh.get_workflow(o1.name, project=self.project.name, entity_id=o1.id)
            assert isinstance(o2, Workflow)
            assert o1.id == o2.id

            # Get by key
            o3 = dh.get_workflow(o1.key)
            assert isinstance(o3, Workflow)
            assert o1.id == o3.id

        l_obj = dh.list_workflows(self.project.name)
        for obj in l_obj:
            dh.delete_workflow(obj.key)

        assert len(dh.list_workflows(self.project.name)) == 0

    def test_update_refresh(self):
        """Test update and refresh operations."""
        assert dh.list_workflows(self.project.name) == []

        # Create workflow
        wf = dh.new_workflow(
            project=self.project.name,
            **WORKFLOW_DICTS[0],
        )

        # Update description
        desc = "Updated description"
        wf.metadata.description = desc
        wf.save(update=True)

        # Verify update
        refreshed = dh.get_workflow(wf.key)
        assert refreshed.metadata.description == desc

        # Test refresh method
        wf.refresh()
        assert wf.metadata.description == desc

        # Cleanup
        dh.delete_workflow(wf.key)

    def test_versions(self):
        """Test versioning functionality."""

        num_versions = 3
        name = WORKFLOW_DICTS[0]["name"]
        kind = WORKFLOW_DICTS[0]["kind"]
        code = WORKFLOW_DICTS[0]["code"]
        handler = WORKFLOW_DICTS[0]["handler"]

        for _ in range(num_versions):
            dh.new_workflow(
                project=self.project.name,
                name=name,
                kind=kind,
                code=code,
                handler=handler,
            )

        versions = dh.get_workflow_versions(name, project=self.project.name)
        assert len(versions) == num_versions
        assert all(isinstance(v, Workflow) for v in versions)
        assert all(v.name == name for v in versions)

        ids = [v.id for v in versions]
        assert len(set(ids)) == num_versions

        versions_via_project = self.project.get_workflow_versions(name)
        assert len(versions_via_project) == num_versions

        dh.delete_workflow(
            name,
            project=self.project.name,
            delete_all_versions=True,
        )
        assert len(dh.list_workflows(self.project.name)) == 0

    def test_import_export(self):
        """Test import/export functionality."""

        # Create workflow
        name = WORKFLOW_DICTS[0]["name"]
        kind = WORKFLOW_DICTS[0]["kind"]
        description = "Test export"
        wf = dh.new_workflow(
            project=self.project.name,
            **WORKFLOW_DICTS[0],
            description=description,
        )

        export_path = wf.export()
        assert Path(export_path).exists()

        dh.delete_workflow(wf.key)
        assert len(dh.list_workflows(self.project.name)) == 0

        imported = dh.import_workflow(file=export_path)
        assert isinstance(imported, Workflow)
        assert imported.name == name
        assert imported.kind == kind
        assert imported.metadata.description == description

        dh.delete_workflow(imported.key)
        Path(export_path).unlink()

    def test_project_integration(self):
        """Test workflow operations via project object."""
        wf = self.project.new_workflow(
            **WORKFLOW_DICTS[0],
        )
        assert isinstance(wf, Workflow)

        retrieved = self.project.get_workflow(wf.key)
        assert retrieved.id == wf.id

        workflows = self.project.list_workflows()
        assert len(workflows) == 1
        assert workflows[0].id == wf.id

        description = "Updated via project"
        wf.metadata.description = description
        updated = self.project.update_workflow(wf)
        assert updated.metadata.description == description

        self.project.delete_workflow(wf.key)
        assert len(self.project.list_workflows()) == 0
