# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Project
"""

from __future__ import annotations

from pathlib import Path

import digitalhub as dh
from digitalhub.entities.project._base.entity import Project

PROJECT_DICTS = [
    {
        "name": "test-project-1",
        "description": "Test project 1",
        "labels": ["test", "project1"],
    },
    {
        "name": "test-project-2",
        "description": "Test project 2",
        "labels": ["test", "project2"],
    },
    {
        "name": "test-project-3",
        "description": "Test project 3",
    },
]

func = {
    "name": "test-function",
    "kind": "python",
    "code": "def main(): return 'test'",
    "handler": "main",
    "python_version": "PYTHON3_10",
    "embedded": True,
}
artf = {
    "name": "test-artifact",
    "kind": "artifact",
    "path": "./test.csv",
    "embedded": True,
}
modl = {
    "name": "test-model",
    "kind": "mlflow",
    "path": "./model",
    "embedded": True,
}
data = {
    "name": "test-dataitem",
    "kind": "table",
    "path": "./test.csv",
    "embedded": True,
}


class TestProjectCRUD:
    def __init__(self, _: Project):
        # Note: This class doesn't use the passed project
        # since it creates/tests its own projects
        try:
            dh.delete_project("test-project-1")
        except Exception:
            pass
        try:
            dh.delete_project("test-project-2")
        except Exception:
            pass
        try:
            dh.delete_project("test-project-3")
        except Exception:
            pass

    def test_create_delete(self):
        """Test creation and deletion via different methods."""

        for i in PROJECT_DICTS:
            # Test module-level create + delete
            p = dh.new_project(**i)
            assert isinstance(p, Project)
            assert p.name == i["name"]
            dh.delete_project(p.name)

            # Test get_or_create
            p = dh.get_or_create_project(**i)
            assert isinstance(p, Project)
            assert p.name == i["name"]
            dh.delete_project(p.name)

    def test_get_list(self):
        """Test get and list operations."""

        # Create multiple projects
        projects = []
        for i in PROJECT_DICTS:
            p = dh.new_project(**i)
            projects.append(p)

        # Test get
        for proj in projects:
            p = dh.get_project(proj.name)
            assert isinstance(p, Project)
            assert p.name == proj.name

        # Cleanup
        for proj in projects:
            dh.delete_project(proj.name)

    def test_update_refresh(self):
        """Test update and refresh operations."""

        proj_dict = PROJECT_DICTS[0]
        p = dh.new_project(**proj_dict)

        # Update description via entity
        p.metadata.description = "Updated description"
        p = dh.update_project(p)
        assert p.metadata.description == "Updated description"

        # Test refresh
        p2 = dh.get_project(p.name)
        assert p2.metadata.description == "Updated description"

        # Test save method
        p.metadata.description = "Another update"
        p.save(update=True)
        assert p.metadata.description == "Another update"

        # Test refresh method
        p2 = dh.get_project(p.name)
        p2.metadata.description = "Yet another update"
        p2.save(update=True)

        p.refresh()
        assert p.metadata.description == "Yet another update"

        # Cleanup
        dh.delete_project(p.name)

    def test_export_import(self):
        """Test export and import operations."""

        proj_dict = PROJECT_DICTS[0]
        p = dh.new_project(**proj_dict)

        # Create some entities in the project
        p.new_artifact(**artf)
        p.new_function(**func)

        # Export project
        export_path = p.export()
        assert Path(export_path).exists()

        # Delete project
        dh.delete_project(p.name)

        # Import project back
        p2 = dh.import_project(export_path, reset_id=False)
        assert isinstance(p2, Project)
        assert p2.name == p.name

        # Verify entities are imported
        artifacts = p2.list_artifacts()
        assert len(artifacts) == 1
        assert artifacts[0].name == "test-artifact"

        functions = p2.list_functions()
        assert len(functions) == 1
        assert functions[0].name == "test-function"

        # Cleanup
        dh.delete_project(p2.name)
        Path(export_path).unlink(missing_ok=True)

    def test_load(self):
        """Test load operation."""

        proj_dict = PROJECT_DICTS[1]
        p = dh.new_project(**proj_dict)

        # Export to file
        export_path = p.export()

        # Modify description in memory
        p.metadata.description = "Modified in memory"

        # Load from file (should update backend)
        p2 = dh.load_project(export_path)
        assert isinstance(p2, Project)
        assert p2.name == p.name

        # Get fresh instance to verify load updated backend
        p3 = dh.get_project(p.name)
        assert p3.metadata.description == proj_dict.get("description", "")

        # Cleanup
        dh.delete_project(p.name)
        Path(export_path).unlink(missing_ok=True)

    def test_search_entity(self):
        """Test search_entity operation."""

        proj_dict = PROJECT_DICTS[2]
        p = dh.new_project(**proj_dict)

        # Create entities of different types
        p.new_artifact(**artf)
        p.new_dataitem(**data)
        p.new_model(**modl)
        p.new_function(**func)

        # Search all entities
        all_entities, _ = p.search_entity()
        assert len(all_entities) == 4

        # Search by entity type
        artifacts, _ = p.search_entity(entity_types=["artifact"])
        assert len(artifacts) == 1
        assert artifacts[0].name == "test-artifact"

        # Search using module-level function
        results, _ = dh.search_entity(p.name, name="test-model")
        assert len(results) >= 1

        # Cleanup
        dh.delete_project(p.name)
