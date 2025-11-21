# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Function
"""

from __future__ import annotations

import typing
from pathlib import Path

import digitalhub as dh
from digitalhub.entities.function._base.entity import Function

if typing.TYPE_CHECKING:
    from digitalhub.entities.project._base.entity import Project


FUNCTION_DICTS = [
    {
        "name": "test1",
        "uuid": "d150bcca-bb64-451d-8455-dff862254b95",
        "kind": "python",
        "code": "def main(): return 'Hello, World!'",
        "python_version": "PYTHON3_12",
        "handler": "main",
    },
    {
        "name": "test2",
        "uuid": "31acdd2d-0c41-428c-b68b-1b133da9e97b",
        "kind": "python",
        "code": "def main(): return 'Hello, World!'",
        "python_version": "PYTHON3_12",
        "handler": "main",
    },
    {
        "name": "test3",
        "uuid": "b4a3dfdc-b917-44c4-9a29-613dcf734244",
        "kind": "container",
        "image": "hello-world:latest",
    },
]


class TestFunctionCRUD:
    def __init__(self, project: Project):
        self.project = project

    def test_create_delete(self):
        """Test creation and deletion via different methods."""

        for i in FUNCTION_DICTS:
            # Test module-level create + delete by key
            f = dh.new_function(self.project.name, **i)
            assert isinstance(f, Function)
            assert f.name == i["name"]
            assert f.kind == i["kind"]
            dh.delete_function(f.key)

            # Test module-level create + delete by name and id
            f = dh.new_function(self.project.name, **i)
            dh.delete_function(f.name, project=self.project.name, entity_id=f.id)

            # Test project-level create + delete
            f = self.project.new_function(**i)
            self.project.delete_function(f.key)

        assert dh.list_functions(self.project.name) == []

    def test_list(self):
        """Test listing functions."""

        assert dh.list_functions(self.project.name) == []

        for i in FUNCTION_DICTS:
            dh.new_function(self.project.name, **i)

        l_obj = dh.list_functions(self.project.name)
        assert isinstance(l_obj, list)
        assert len(l_obj) == len(FUNCTION_DICTS)
        for i in l_obj:
            assert isinstance(i, Function)

        for obj in l_obj:
            dh.delete_function(
                obj.name, project=self.project.name, delete_all_versions=True
            )

        assert len(dh.list_functions(self.project.name)) == 0

    def test_get(self):
        """Test getting functions by different identifiers."""

        for i in FUNCTION_DICTS:
            o1 = dh.new_function(self.project.name, **i)
            assert isinstance(o1, Function)

            # Get by name and id
            o2 = dh.get_function(o1.name, project=self.project.name, entity_id=o1.id)
            assert isinstance(o2, Function)
            assert o1.id == o2.id

            # Get by key
            o3 = dh.get_function(o1.key)
            assert isinstance(o3, Function)
            assert o1.id == o3.id

        l_obj = dh.list_functions(self.project.name)
        for obj in l_obj:
            dh.delete_function(obj.key)

        assert len(dh.list_functions(self.project.name)) == 0

    def test_update_refresh(self):
        """Test update and refresh operations."""
        assert dh.list_functions(self.project.name) == []

        # Create function
        func = dh.new_function(
            project=self.project.name,
            **FUNCTION_DICTS[0],
        )

        # Update description
        desc = "Updated description"
        func.metadata.description = desc
        func.save(update=True)

        # Verify update
        refreshed = dh.get_function(func.key)
        assert refreshed.metadata.description == desc

        # Test refresh method
        func.refresh()
        assert func.metadata.description == desc

        # Cleanup
        dh.delete_function(func.key)

    def test_versions(self):
        """Test versioning functionality."""

        num_versions = 3
        name = FUNCTION_DICTS[0]["name"]
        kind = FUNCTION_DICTS[0]["kind"]
        code = FUNCTION_DICTS[0]["code"]
        python_version = FUNCTION_DICTS[0]["python_version"]
        handler = FUNCTION_DICTS[0]["handler"]

        for _ in range(num_versions):
            dh.new_function(
                project=self.project.name,
                name=name,
                kind=kind,
                code=code,
                python_version=python_version,
                handler=handler,
            )

        versions = dh.get_function_versions(name, project=self.project.name)
        assert len(versions) == num_versions
        assert all(isinstance(v, Function) for v in versions)
        assert all(v.name == name for v in versions)

        ids = [v.id for v in versions]
        assert len(set(ids)) == num_versions

        versions_via_project = self.project.get_function_versions(name)
        assert len(versions_via_project) == num_versions

        dh.delete_function(
            name,
            project=self.project.name,
            delete_all_versions=True,
        )
        assert len(dh.list_functions(self.project.name)) == 0

    def test_import_export(self):
        """Test import/export functionality."""

        # Create function
        name = FUNCTION_DICTS[0]["name"]
        kind = FUNCTION_DICTS[0]["kind"]
        description = "Test export"
        func = dh.new_function(
            project=self.project.name,
            **FUNCTION_DICTS[0],
            description=description,
        )

        export_path = func.export()
        assert Path(export_path).exists()

        dh.delete_function(func.key)
        assert len(dh.list_functions(self.project.name)) == 0

        imported = dh.import_function(file=export_path)
        assert isinstance(imported, Function)
        assert imported.name == name
        assert imported.kind == kind
        assert imported.metadata.description == description

        dh.delete_function(imported.key)
        Path(export_path).unlink()

    def test_project_integration(self):
        """Test function operations via project object."""
        func = self.project.new_function(
            **FUNCTION_DICTS[0],
        )
        assert isinstance(func, Function)

        retrieved = self.project.get_function(func.key)
        assert retrieved.id == func.id

        functions = self.project.list_functions()
        assert len(functions) == 1
        assert functions[0].id == func.id

        description = "Updated via project"
        func.metadata.description = description
        updated = self.project.update_function(func)
        assert updated.metadata.description == description

        self.project.delete_function(func.key)
        assert len(self.project.list_functions()) == 0
