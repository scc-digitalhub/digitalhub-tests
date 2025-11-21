# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Secret
"""

from __future__ import annotations

import typing
from pathlib import Path

import digitalhub as dh
from digitalhub.entities.secret._base.entity import Secret

if typing.TYPE_CHECKING:
    from digitalhub.entities.project._base.entity import Project


SECRET_DICTS = [
    {"name": "test-secret-1", "secret_value": "value-1"},
    {"name": "test-secret-2", "secret_value": "value-2"},
    {"name": "test-secret-3", "secret_value": "value-3"},
]


class TestSecretCRUD:
    def __init__(self, project: Project):
        self.project = project
        for i in SECRET_DICTS:
            try:
                s = dh.get_secret(i["name"], project=self.project.name)
                dh.delete_secret(s.key)
            except Exception:
                pass

    def test_create_delete(self):
        """Test creation and deletion via different methods."""

        for i in SECRET_DICTS:
            # Test module-level create + delete by key
            s = dh.new_secret(self.project.name, **i)
            assert isinstance(s, Secret)
            assert s.name == i["name"]
            assert s.read_secret_value() == i["secret_value"]
            dh.delete_secret(s.key)

            # Test module-level create + delete by name and id
            s = dh.new_secret(self.project.name, **i)
            dh.delete_secret(s.name, project=self.project.name, entity_id=s.id)

            # Test project-level create + delete
            s = self.project.new_secret(**i)
            self.project.delete_secret(s.key)

        assert dh.list_secrets(self.project.name) == []

    def test_get(self):
        """Test getting secrets by different identifiers."""

        for i in SECRET_DICTS:
            o1 = dh.new_secret(self.project.name, **i)
            assert isinstance(o1, Secret)

            # Get by name and id
            o2 = dh.get_secret(o1.name, project=self.project.name, entity_id=o1.id)
            assert isinstance(o2, Secret)
            assert o1.id == o2.id

            # Get by key
            o3 = dh.get_secret(o1.key)
            assert isinstance(o3, Secret)
            assert o1.id == o3.id

            dh.delete_secret(o1.key)

    def test_update_refresh(self):
        """Test update and refresh operations."""
        assert dh.list_secrets(self.project.name) == []

        # Create secret
        secret = dh.new_secret(
            project=self.project.name,
            **SECRET_DICTS[0],
        )

        # Update description
        desc = "Updated description"
        secret.metadata.description = desc
        secret.save(update=True)

        # Verify update
        refreshed = dh.get_secret(secret.key)
        assert refreshed.metadata.description == desc

        # Test refresh method
        secret.refresh()
        assert secret.metadata.description == desc

        # Cleanup
        dh.delete_secret(secret.key)

    def test_import_export(self):
        """Test import/export functionality."""

        # Create secret
        name = SECRET_DICTS[0]["name"]
        description = "Test export"
        secret = dh.new_secret(
            project=self.project.name,
            **SECRET_DICTS[0],
            description=description,
        )

        export_path = secret.export()
        assert Path(export_path).exists()

        dh.delete_secret(secret.key)

        imported = dh.import_secret(file=export_path)
        assert isinstance(imported, Secret)
        assert imported.name == name
        assert imported.kind == "secret"
        assert imported.metadata.description == description

        dh.delete_secret(imported.key)
        Path(export_path).unlink()

    def test_project_integration(self):
        """Test secret operations via project object."""
        secret = self.project.new_secret(
            **SECRET_DICTS[0],
        )
        assert isinstance(secret, Secret)

        retrieved = self.project.get_secret(secret.key)
        assert retrieved.id == secret.id

        description = "Updated via project"
        secret.metadata.description = description
        updated = self.project.update_secret(secret)
        assert updated.metadata.description == description

        self.project.delete_secret(secret.key)

    def test_secret_value_operations(self):
        """Test secret value read/write operations."""
        secret = dh.new_secret(
            project=self.project.name,
            **SECRET_DICTS[0],
        )

        # Read secret value
        value = secret.read_secret_value()
        assert value == SECRET_DICTS[0]["secret_value"]

        # Update secret value
        new_value = "updated-value"
        secret.set_secret_value(new_value)
        value = secret.read_secret_value()
        assert value == new_value

        dh.delete_secret(secret.key)
