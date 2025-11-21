# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Task
"""

from __future__ import annotations

import typing
from pathlib import Path

import digitalhub as dh
from digitalhub.entities.task._base.entity import Task

if typing.TYPE_CHECKING:
    from digitalhub.entities.function._base.entity import Function
    from digitalhub.entities.project._base.entity import Project


class TestTaskCRUD:
    def __init__(self, project: Project):
        self.project = project

    def _get_function(self) -> Function:
        return dh.new_function(
            project=self.project.name,
            name="task-function",
            kind="container",
            image="hello-world:latest",
        )

    def test_create_delete(self):
        """Test creation and deletion via different methods."""
        f = self._get_function()

        for action in ["job", "serve"]:
            # Test module-level create + delete by key
            t = f.new_task(action=action)
            assert isinstance(t, Task)
            assert t.kind == f"container+{action}"
            assert t.spec.function == f._get_executable_string()
            dh.delete_task(t.key)

            # Test module-level create + delete by name and id
            t = f.new_task(action=action)
            dh.delete_task(t.key)

        dh.delete_function(f.key)
        assert dh.list_tasks(self.project.name) == []

    def test_list(self):
        """Test listing tasks."""
        f = self._get_function()

        assert dh.list_tasks(self.project.name) == []

        for action in ["job", "serve"]:
            f.new_task(action=action)

        l_obj = dh.list_tasks(self.project.name)
        assert isinstance(l_obj, list)
        assert len(l_obj) == 2
        for i in l_obj:
            assert isinstance(i, Task)

        for obj in l_obj:
            dh.delete_task(obj.key)

        dh.delete_function(f.key)
        assert dh.list_tasks(self.project.name) == []

    def test_get(self):
        """Test getting tasks by different identifiers."""
        f = self._get_function()

        for action in ["job", "serve"]:
            o1 = f.new_task(action=action)
            assert isinstance(o1, Task)

            # Get by name and id
            o2 = dh.get_task(o1.name, project=self.project.name)
            assert isinstance(o2, Task)
            assert o1.id == o2.id

            # Get by key
            o3 = dh.get_task(o1.key)
            assert isinstance(o3, Task)
            assert o1.id == o3.id

        l_obj = dh.list_tasks(self.project.name)
        for obj in l_obj:
            dh.delete_task(obj.key)

        dh.delete_function(f.key)
        assert dh.list_tasks(self.project.name) == []

    def test_update_refresh(self):
        """Test update and refresh operations."""
        f = self._get_function()
        assert dh.list_tasks(self.project.name) == []

        # Create task
        task = f.new_task(action="job")

        # Update labels
        labels = ["test", "update"]
        task.metadata.labels = labels
        task.save(update=True)

        # Verify update
        refreshed = dh.get_task(task.key)
        assert refreshed.metadata.labels == labels

        # Test refresh method
        task.refresh()
        assert task.metadata.labels == labels

        # Cleanup
        dh.delete_task(task.key)
        dh.delete_function(f.key)

    def test_import_export(self):
        """Test import/export functionality."""
        f = self._get_function()

        # Create task
        action = "job"
        task = f.new_task(
            action=action,
            labels=["test", "export"],
        )

        export_path = task.export()
        assert Path(export_path).exists()

        dh.delete_task(task.key)
        assert len(dh.list_tasks(self.project.name)) == 0

        imported = dh.import_task(file=export_path)
        assert isinstance(imported, Task)
        assert imported.spec.function == f._get_executable_string()
        assert imported.kind == f"container+{action}"

        dh.delete_task(imported.key)
        Path(export_path).unlink()

        dh.delete_function(f.key)
