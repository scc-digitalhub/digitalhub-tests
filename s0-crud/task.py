# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Task
"""

from __future__ import annotations

import time
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

    def _cleanup_tasks(self) -> None:
        for obj in self.project.list_tasks():
            dh.delete_task(obj.key)
            time.sleep(2)

    def _get_function(self) -> Function:
        return dh.new_function(
            project=self.project.name,
            name="task-function",
            kind="container",
            image="hello-world:latest",
        )

    def test_create_delete(self):
        """Test creation and deletion via different methods."""
        self._cleanup_tasks()
        f = self._get_function()

        for action in ["job", "serve"]:
            t = f.new_task(action=action)
            assert isinstance(t, Task)
            assert t.kind == f"container+{action}"
            assert t.spec.function == f._get_executable_string()
            time.sleep(2)
            dh.delete_task(t.key)
            time.sleep(2)

            t = f.new_task(action=action)
            time.sleep(2)
            dh.delete_task(t.key)
            time.sleep(2)

        dh.delete_function(f.key)
        time.sleep(2)
        self._cleanup_tasks()
        assert dh.list_tasks(self.project.name) == []

    def test_list(self):
        """Test listing tasks."""
        self._cleanup_tasks()
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
            time.sleep(2)

        dh.delete_function(f.key)
        time.sleep(2)
        self._cleanup_tasks()
        assert dh.list_tasks(self.project.name) == []

    def test_get(self):
        """Test getting tasks by different identifiers."""
        self._cleanup_tasks()
        f = self._get_function()

        for action in ["job", "serve"]:
            o1 = f.new_task(action=action)
            assert isinstance(o1, Task)

            o2 = dh.get_task(o1.name, project=self.project.name)
            assert isinstance(o2, Task)
            assert o1.id == o2.id

            o3 = dh.get_task(o1.key)
            assert isinstance(o3, Task)
            assert o1.id == o3.id

        l_obj = dh.list_tasks(self.project.name)
        for obj in l_obj:
            dh.delete_task(obj.key)
            time.sleep(2)

        dh.delete_function(f.key)
        time.sleep(2)
        self._cleanup_tasks()
        assert dh.list_tasks(self.project.name) == []

    def test_update_refresh(self):
        """Test update and refresh operations."""
        self._cleanup_tasks()
        f = self._get_function()
        task = f.new_task(action="job")

        description = "Test update"
        task.metadata.description = description
        updated = dh.update_task(task)
        assert updated.metadata.description == description

        updated_project = self.project.update_task(task)
        assert updated_project.metadata.description == description

        refreshed = dh.get_task(task.key)
        assert refreshed.metadata.description == description

        task.refresh()
        assert task.metadata.description == description

        dh.delete_task(task.key)
        time.sleep(2)

        f.delete_task(action="job")
        dh.delete_function(f.key)
        time.sleep(2)
        self._cleanup_tasks()

    def test_import_load(self):
        """Test import/load functionality."""
        self._cleanup_tasks()
        f = self._get_function()

        action = "job"
        task = f.new_task(
            action=action,
            labels=["test", "export"],
        )

        export_path = task.export()
        assert Path(export_path).exists()

        dh.delete_task(task.key)
        time.sleep(2)
        assert len(dh.list_tasks(self.project.name)) == 0

        imported = dh.import_task(file=export_path)
        assert isinstance(imported, Task)
        assert imported.spec.function == f._get_executable_string()
        assert imported.kind == f"container+{action}"

        dh.delete_task(imported.key)
        time.sleep(2)

        loaded = dh.load_task(export_path)
        assert isinstance(loaded, Task)
        assert loaded.spec.function == f._get_executable_string()
        assert loaded.kind == f"container+{action}"

        dh.delete_task(loaded.key)
        time.sleep(2)
        Path(export_path).unlink()

        f.delete_task(action="job")
        dh.delete_function(f.key)
        time.sleep(2)
        self._cleanup_tasks()
