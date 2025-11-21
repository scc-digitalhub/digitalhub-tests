# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Run
"""

from __future__ import annotations

import typing
from pathlib import Path

import digitalhub as dh
from digitalhub.entities.run._base.entity import Run

if typing.TYPE_CHECKING:
    from digitalhub.entities.function._base.entity import Function
    from digitalhub.entities.project._base.entity import Project


RUN_DICTS = [
    {
        "local_execution": True,
        "run_kind": "python+job:run",
    }
]


class TestRunCRUD:
    def __init__(self, project: Project):
        self.project = project

    def _get_function(self) -> Function:
        return dh.new_function(
            project=self.project.name,
            name="run-function",
            kind="python",
            code="def handler(x=1): return x * 2",
            handler="handler",
            python_version="PYTHON3_12",
        )

    def test_create_delete(self):
        """Test creation and deletion via different methods."""
        f = self._get_function()

        for action in ["job", "build"]:
            task = f.new_task(action=action)

            run_dict = RUN_DICTS[0].copy()
            run_dict["run_kind"] = f"python+{action}:run"

            # Test module-level create + delete by key
            r = task.run(**run_dict)
            assert isinstance(r, Run)
            assert r.kind == f"python+{action}:run"
            dh.delete_run(r.key)

            # Test module-level create + delete by id
            r = task.run(**RUN_DICTS[0])
            dh.delete_run(r.id, project=self.project.name, entity_id=r.id)

            f.delete_task(action=action)

        dh.delete_function(f.key)
        assert dh.list_runs(self.project.name) == []

    def test_list(self):
        """Test listing runs."""
        f = self._get_function()
        task = f.new_task(action="job")

        assert dh.list_runs(self.project.name) == []

        # Create multiple runs
        for _ in range(3):
            task.run(**RUN_DICTS[0])

        l_obj = dh.list_runs(self.project.name)
        assert isinstance(l_obj, list)
        assert len(l_obj) == 3
        for i in l_obj:
            assert isinstance(i, Run)

        for obj in l_obj:
            dh.delete_run(obj.key)

        f.delete_task(action="job")
        dh.delete_function(f.key)
        assert len(dh.list_runs(self.project.name)) == 0

    def test_get(self):
        """Test getting runs by different identifiers."""
        f = self._get_function()
        task = f.new_task(action="job")

        for _ in range(2):
            o1 = task.run(**RUN_DICTS[0])
            assert isinstance(o1, Run)

            # Get by name and id
            o2 = dh.get_run(o1.name, project=self.project.name)
            assert isinstance(o2, Run)
            assert o1.id == o2.id

            # Get by key
            o3 = dh.get_run(o1.key)
            assert isinstance(o3, Run)
            assert o1.id == o3.id

        l_obj = dh.list_runs(self.project.name)
        for obj in l_obj:
            dh.delete_run(obj.key)

        f.delete_task(action="job")
        dh.delete_function(f.key)
        assert dh.list_runs(self.project.name) == []

    def test_update_refresh(self):
        """Test update and refresh operations."""
        f = self._get_function()
        task = f.new_task(action="job")
        assert dh.list_runs(self.project.name) == []

        # Create run
        run = task.run(**RUN_DICTS[0])

        # Update labels
        labels = ["test", "update"]
        run.metadata.labels = labels
        run.save(update=True)

        # Verify update
        refreshed = dh.get_run(run.key)
        assert refreshed.metadata.labels == labels

        # Test refresh method
        run.refresh()
        assert run.metadata.labels == labels

        # Cleanup
        dh.delete_run(run.key)
        f.delete_task(action="job")
        dh.delete_function(f.key)

    def test_import_export(self):
        """Test import/export functionality."""
        f = self._get_function()
        task = f.new_task(action="job")

        # Create run
        run = task.run(**RUN_DICTS[0])

        export_path = run.export()
        assert Path(export_path).exists()

        dh.delete_run(run.key)
        assert len(dh.list_runs(self.project.name)) == 0

        imported = dh.import_run(file=export_path)
        assert isinstance(imported, Run)
        assert imported.kind == "python+job:run"

        dh.delete_run(imported.key)
        Path(export_path).unlink()

        f.delete_task(action="job")
        dh.delete_function(f.key)
