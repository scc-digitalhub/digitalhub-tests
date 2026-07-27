# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Containerimage
"""

from __future__ import annotations

import time
import typing
from pathlib import Path

import digitalhub as dh
from digitalhub.entities.containerimage._base.entity import Containerimage

if typing.TYPE_CHECKING:
    from digitalhub.entities.project._base.entity import Project


CONTAINERIMAGE_DICTS = [
    {
        "name": "test1",
        "kind": "container-image",
        "image": "hello-world:latest",
    },
    {
        "name": "test2",
        "kind": "container-image",
        "image": "python:3.12-slim",
    },
]


class TestContainerimageCRUD:
    def __init__(self, project: Project):
        self.project = project

    def test_create_delete(self):
        """Test creation and deletion via different methods."""

        for i in CONTAINERIMAGE_DICTS:
            d = dh.new_containerimage(self.project.name, **i)
            assert isinstance(d, Containerimage)
            assert d.name == i["name"]
            assert d.kind == i["kind"]
            dh.delete_containerimage(d.key, cascade=False)
            time.sleep(2)

            d = dh.new_containerimage(self.project.name, **i)
            dh.delete_containerimage(
                d.name,
                project=self.project.name,
                entity_id=d.id,
                cascade=False,
            )
            time.sleep(2)

            d = self.project.new_containerimage(
                name=i["name"],
                image=i["image"],
            )
            self.project.delete_containerimage(d.key, cascade=False)
            time.sleep(2)

        assert dh.list_containerimages(self.project.name) == []

    def test_list(self):
        """Test listing containerimages."""

        assert dh.list_containerimages(self.project.name) == []

        for i in CONTAINERIMAGE_DICTS:
            dh.new_containerimage(self.project.name, **i)

        l_obj = dh.list_containerimages(self.project.name)
        assert isinstance(l_obj, list)
        assert len(l_obj) == len(CONTAINERIMAGE_DICTS)
        for i in l_obj:
            assert isinstance(i, Containerimage)

        for obj in l_obj:
            dh.delete_containerimage(
                obj.name,
                project=self.project.name,
                delete_all_versions=True,
                cascade=False,
            )
            time.sleep(2)

        assert len(dh.list_containerimages(self.project.name)) == 0

    def test_get(self):
        """Test getting containerimages by different identifiers."""

        for i in CONTAINERIMAGE_DICTS:
            o1 = dh.new_containerimage(self.project.name, **i)
            assert isinstance(o1, Containerimage)

            o2 = dh.get_containerimage(
                o1.name, project=self.project.name, entity_id=o1.id
            )
            assert isinstance(o2, Containerimage)
            assert o1.id == o2.id

            o3 = dh.get_containerimage(o1.key)
            assert isinstance(o3, Containerimage)
            assert o1.id == o3.id

        l_obj = dh.list_containerimages(self.project.name)
        for obj in l_obj:
            dh.delete_containerimage(obj.key, cascade=False)
            time.sleep(2)

        assert len(dh.list_containerimages(self.project.name)) == 0

    def test_update_refresh(self):
        """Test update and refresh operations."""
        assert dh.list_containerimages(self.project.name) == []

        ci = dh.new_containerimage(
            project=self.project.name,
            **CONTAINERIMAGE_DICTS[0],
        )

        description = "Updated description"
        ci.metadata.description = description
        updated = dh.update_containerimage(ci)
        assert updated.metadata.description == description

        updated_project = self.project.update_containerimage(ci)
        assert updated_project.metadata.description == description

        refreshed = dh.get_containerimage(ci.key)
        assert refreshed.metadata.description == description

        ci.refresh()
        assert ci.metadata.description == description

        dh.delete_containerimage(ci.key, cascade=False)
        time.sleep(2)

    def test_versions(self):
        """Test versioning functionality."""

        num_versions = 3
        name = CONTAINERIMAGE_DICTS[0]["name"]
        kind = CONTAINERIMAGE_DICTS[0]["kind"]
        image = CONTAINERIMAGE_DICTS[0]["image"]

        for _ in range(num_versions):
            dh.new_containerimage(
                project=self.project.name,
                name=name,
                kind=kind,
                image=image,
            )

        versions = dh.get_containerimage_versions(name, project=self.project.name)
        assert len(versions) == num_versions
        assert all(isinstance(v, Containerimage) for v in versions)
        assert all(v.name == name for v in versions)

        ids = [v.id for v in versions]
        assert len(set(ids)) == num_versions

        versions_via_project = self.project.get_containerimage_versions(name)
        assert len(versions_via_project) == num_versions

        dh.delete_containerimage(
            name,
            project=self.project.name,
            delete_all_versions=True,
            cascade=False,
        )
        time.sleep(2)
        assert len(dh.list_containerimages(self.project.name)) == 0

    def test_import_load(self):
        """Test import/load functionality."""

        name = CONTAINERIMAGE_DICTS[0]["name"]
        kind = CONTAINERIMAGE_DICTS[0]["kind"]
        description = "Test export"
        ci = dh.new_containerimage(
            project=self.project.name,
            **CONTAINERIMAGE_DICTS[0],
            description=description,
        )

        export_path = ci.export()
        assert Path(export_path).exists()

        dh.delete_containerimage(ci.key, cascade=False)
        time.sleep(2)
        assert len(dh.list_containerimages(self.project.name)) == 0

        imported = dh.import_containerimage(file=export_path)
        assert isinstance(imported, Containerimage)
        assert imported.name == name
        assert imported.kind == kind
        assert imported.metadata.description == description

        dh.delete_containerimage(imported.key)
        time.sleep(2)

        loaded = dh.load_containerimage(export_path)
        assert isinstance(loaded, Containerimage)
        assert loaded.name == name
        assert loaded.kind == kind
        assert loaded.metadata.description == description

        dh.delete_containerimage(loaded.key)
        time.sleep(2)
        Path(export_path).unlink()
