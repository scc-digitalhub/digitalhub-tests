# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Trigger
"""

from __future__ import annotations

import typing
from pathlib import Path

import digitalhub as dh
from digitalhub.entities.trigger._base.entity import Trigger

if typing.TYPE_CHECKING:
    from digitalhub.entities.function._base.entity import Function
    from digitalhub.entities.project._base.entity import Project


TRIGGER_DICTS = [
    {
        "name": "test1",
        "uuid": "d150bcca-bb64-451d-8455-dff862254b95",
        "kind": "scheduler",
        "schedule": "0 0 * * *",
    },
    {
        "name": "test2",
        "uuid": "31acdd2d-0c41-428c-b68b-1b133da9e97b",
        "kind": "scheduler",
        "schedule": "0 12 * * *",
    },
    {
        "name": "test3",
        "uuid": "b4a3dfdc-b917-44c4-9a29-613dcf734244",
        "kind": "lifecycle",
        "key": "store://test/artifacts/*",
        "states": ["READY"],
    },
]


class TestTriggerCRUD:
    def __init__(self, project: Project):
        self.project = project
        try:
            names = [i["name"] for i in TRIGGER_DICTS]
            for t in dh.list_triggers(self.project.name):
                if t.name in names:
                    dh.delete_trigger(t.key)
        except Exception:
            pass

    def _get_function(self) -> Function:
        return dh.new_function(
            project=self.project.name,
            name="trigger-function",
            kind="python",
            code="def handler(): return 'test'",
            handler="handler",
            python_version="PYTHON3_12",
        )

    def test_create_delete(self):
        """Test creation and deletion via different methods."""
        f = self._get_function()
        task = f.new_task(action="job")

        for i in TRIGGER_DICTS:
            # Test module-level create + delete by key
            t = dh.new_trigger(
                project=self.project.name,
                task=task._get_task_string(),
                function=f._get_executable_string(),
                **i,
            )
            assert isinstance(t, Trigger)
            assert t.name == i["name"]
            assert t.kind == i["kind"]
            dh.delete_trigger(t.key)

            # Test module-level create + delete by name and id
            t = dh.new_trigger(
                project=self.project.name,
                task=task.key,
                function=f.key,
                **i,
            )
            dh.delete_trigger(t.name, project=self.project.name, entity_id=t.id)

            # Test function-level create + delete
            t = f.trigger(action="job", **i)
            dh.delete_trigger(t.key)

        dh.delete_function(f.key)
        assert dh.list_triggers(self.project.name) == []

    def test_list(self):
        """Test listing triggers."""
        f = self._get_function()
        task = f.new_task(action="job")

        assert dh.list_triggers(self.project.name) == []

        for i in TRIGGER_DICTS:
            dh.new_trigger(
                project=self.project.name,
                task=task.key,
                function=f.key,
                **i,
            )

        l_obj = dh.list_triggers(self.project.name)
        assert isinstance(l_obj, list)
        assert len(l_obj) == len(TRIGGER_DICTS)
        for i in l_obj:
            assert isinstance(i, Trigger)

        for obj in l_obj:
            dh.delete_trigger(obj.key)

        dh.delete_function(f.key)
        assert len(dh.list_triggers(self.project.name)) == 0

    def test_get(self):
        """Test getting triggers by different identifiers."""
        f = self._get_function()
        task = f.new_task(action="job")

        for i in TRIGGER_DICTS:
            o1 = dh.new_trigger(
                project=self.project.name,
                task=task._get_task_string(),
                function=f._get_executable_string(),
                **i,
            )
            assert isinstance(o1, Trigger)

            # Get by name and id
            o2 = dh.get_trigger(o1.name, project=self.project.name, entity_id=o1.id)
            assert isinstance(o2, Trigger)
            assert o1.id == o2.id

            # Get by key
            o3 = dh.get_trigger(o1.key)
            assert isinstance(o3, Trigger)
            assert o1.id == o3.id

        l_obj = dh.list_triggers(self.project.name)
        for obj in l_obj:
            dh.delete_trigger(obj.key)

        dh.delete_function(f.key)
        assert dh.list_triggers(self.project.name) == []

    def test_update_refresh(self):
        """Test update and refresh operations."""
        f = self._get_function()
        task = f.new_task(action="job")
        assert dh.list_triggers(self.project.name) == []

        # Create trigger
        trigger = dh.new_trigger(
            project=self.project.name,
            task=task._get_task_string(),
            function=f._get_executable_string(),
            **TRIGGER_DICTS[0],
        )

        # Update description
        desc = "Updated description"
        trigger.metadata.description = desc
        trigger.save(update=True)

        # Verify update
        refreshed = dh.get_trigger(trigger.key)
        assert refreshed.metadata.description == desc

        # Test refresh method
        trigger.refresh()
        assert trigger.metadata.description == desc

        # Cleanup
        dh.delete_trigger(trigger.key)
        dh.delete_function(f.key)

    def test_import_export(self):
        """Test import/export functionality."""
        f = self._get_function()
        task = f.new_task(action="job")

        # Create trigger
        name = TRIGGER_DICTS[0]["name"]
        kind = TRIGGER_DICTS[0]["kind"]
        description = "Test export"
        trigger = dh.new_trigger(
            project=self.project.name,
            task=task._get_task_string(),
            function=f._get_executable_string(),
            **TRIGGER_DICTS[0],
            description=description,
        )

        export_path = trigger.export()
        assert Path(export_path).exists()

        dh.delete_trigger(trigger.key)
        assert len(dh.list_triggers(self.project.name)) == 0

        imported = dh.import_trigger(file=export_path)
        assert isinstance(imported, Trigger)
        assert imported.name == name
        assert imported.kind == kind
        assert imported.metadata.description == description

        dh.delete_trigger(imported.key)
        Path(export_path).unlink()

        dh.delete_function(f.key)
