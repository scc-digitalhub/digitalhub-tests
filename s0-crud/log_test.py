# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Artifact
"""

from __future__ import annotations

import time
import typing
from pathlib import Path

import digitalhub as dh
import pandas as pd
import polars as pl

if typing.TYPE_CHECKING:
    from digitalhub.entities.project._base.entity import Project


class TestLogCRUD:
    def __init__(self, project: Project):
        self.project = project
        self.path = str(Path(__file__).parent / "data" / "sample.csv")
        self.dfpl = pl.read_csv(self.path)
        self.dfpd = pd.read_csv(self.path)
        self.cr_path = str(
            Path(__file__).parent / "data" / "croissant" / "metadata.json"
        )

    def test_log_methods(self):
        """Test all log methods for different entities."""

        name = "test"
        cleanup_steps = [
            (self.project.list_artifacts, self.project.delete_artifact),
            (self.project.list_dataitems, self.project.delete_dataitem),
            (self.project.list_models, self.project.delete_model),
        ]
        for list_fn, delete_fn in cleanup_steps:
            if any(entity.name == name for entity in list_fn()):
                delete_fn(name, delete_all_versions=True, cascade=False)
                time.sleep(2)

        # Log artifacts
        common_artifact_kwargs = {
            "source": self.path,
            "description": "Test artifact",
            "labels": ["test", "artifact"],
        }
        dh.log_artifact(self.project.name, name=name, **common_artifact_kwargs)
        dh.log_artifact(self.project.name, name=name, **common_artifact_kwargs)
        self.project.log_artifact(name=name, **common_artifact_kwargs)
        self.project.log_artifact(name=name, **common_artifact_kwargs)
        assert len(dh.get_artifact_versions(name, project=self.project.name)) == 4
        self.project.delete_artifact(name, delete_all_versions=True, cascade=False)
        time.sleep(2)

        # Log generic artifacts
        dh.log_generic_artifact(
            self.project.name, "artifact", name=name, **common_artifact_kwargs
        )
        dh.log_generic_artifact(
            self.project.name, "artifact", name=name, **common_artifact_kwargs
        )
        self.project.log_generic_artifact(
            "artifact", name=name, **common_artifact_kwargs
        )
        self.project.log_generic_artifact(
            "artifact", name=name, **common_artifact_kwargs
        )
        assert len(dh.get_artifact_versions(name, project=self.project.name)) == 4
        self.project.delete_artifact(name, delete_all_versions=True, cascade=False)
        time.sleep(2)

        # Log dataitems
        common_dataitem_kwargs = {
            "description": "Test dataitem",
            "labels": ["test", "dataitem"],
        }
        dh.log_table(
            self.project.name, source=self.path, name=name, **common_dataitem_kwargs
        )
        dh.log_table(
            self.project.name, data=self.dfpl, name=name, **common_dataitem_kwargs
        )
        dh.log_table(
            self.project.name, data=self.dfpd, name=name, **common_dataitem_kwargs
        )
        dh.log_dataitem(
            self.project.name, source=self.path, name=name, **common_dataitem_kwargs
        )
        dh.log_croissant(
            self.project.name, name, source=self.cr_path, **common_dataitem_kwargs
        )
        self.project.log_table(name=name, source=self.path, **common_dataitem_kwargs)
        self.project.log_table(name=name, data=self.dfpl, **common_dataitem_kwargs)
        self.project.log_table(name=name, data=self.dfpd, **common_dataitem_kwargs)
        self.project.log_dataitem(name=name, **common_dataitem_kwargs)
        self.project.log_croissant(name, source=self.cr_path, **common_dataitem_kwargs)
        assert len(dh.get_dataitem_versions(name, project=self.project.name)) == 10
        self.project.delete_dataitem(name, delete_all_versions=True, cascade=False)
        time.sleep(2)

        # Log generic dataitems
        dh.log_generic_dataitem(
            self.project.name,
            name,
            "dataitem",
            source=self.path,
            **common_dataitem_kwargs,
        )
        dh.log_generic_dataitem(
            self.project.name,
            name,
            "dataitem",
            source=self.path,
            **common_dataitem_kwargs,
        )
        self.project.log_generic_dataitem(
            name,
            "dataitem",
            source=self.path,
            **common_dataitem_kwargs,
        )
        self.project.log_generic_dataitem(
            name,
            "dataitem",
            source=self.path,
            **common_dataitem_kwargs,
        )
        assert len(dh.get_dataitem_versions(name, project=self.project.name)) == 4
        self.project.delete_dataitem(name, delete_all_versions=True, cascade=False)
        time.sleep(2)

        # Log models
        common_model_kwargs = {
            "source": self.path,
            "description": "Test model",
            "labels": ["test", "model"],
        }
        dh.log_model(self.project.name, name=name, **common_model_kwargs)
        dh.log_huggingface(self.project.name, name=name, **common_model_kwargs)
        dh.log_sklearn(self.project.name, name=name, **common_model_kwargs)
        dh.log_mlflow(self.project.name, name=name, **common_model_kwargs)
        dh.log_model(self.project.name, name=name, **common_model_kwargs)
        self.project.log_model(name=name, **common_model_kwargs)
        self.project.log_huggingface(name=name, **common_model_kwargs)
        self.project.log_sklearn(name=name, **common_model_kwargs)
        self.project.log_mlflow(name=name, **common_model_kwargs)
        self.project.log_model(name=name, **common_model_kwargs)
        assert len(dh.get_model_versions(name, project=self.project.name)) == 16
        self.project.delete_model(name, delete_all_versions=True, cascade=False)
        time.sleep(2)

        # Log generic models
        dh.log_generic_model(
            self.project.name, "model", name=name, **common_model_kwargs
        )
        dh.log_generic_model(
            self.project.name, "model", name=name, **common_model_kwargs
        )
        self.project.log_generic_model("model", name=name, **common_model_kwargs)
        self.project.log_generic_model("model", name=name, **common_model_kwargs)
        assert len(dh.get_model_versions(name, project=self.project.name)) == 4
        self.project.delete_model(name, delete_all_versions=True, cascade=False)
        time.sleep(2)

    def test_drop_existing(self):
        """Test overwrite functionality for log methods."""
        name = "test"

        entities = [
            (
                self.project.log_dataitem,
                dh.get_dataitem_versions,
                self.project.delete_dataitem,
                False,
            ),
            (
                self.project.log_generic_dataitem,
                dh.get_dataitem_versions,
                self.project.delete_dataitem,
                True,
            ),
            (
                self.project.log_artifact,
                dh.get_artifact_versions,
                self.project.delete_artifact,
                False,
            ),
            (
                self.project.log_generic_artifact,
                dh.get_artifact_versions,
                self.project.delete_artifact,
                True,
            ),
            (
                self.project.log_model,
                dh.get_model_versions,
                self.project.delete_model,
                False,
            ),
            (
                self.project.log_generic_model,
                dh.get_model_versions,
                self.project.delete_model,
                True,
            ),
        ]

        for log_fn, get_versions_fn, delete_fn, is_generic in entities:
            if is_generic:
                kind = (
                    "artifact"
                    if log_fn is self.project.log_generic_artifact
                    else "dataitem"
                    if log_fn is self.project.log_generic_dataitem
                    else "model"
                )
                log_fn(
                    kind,
                    source=self.path,
                    name=name,
                )
                log_fn(
                    kind,
                    source=self.path,
                    name=name,
                )
                assert len(get_versions_fn(name, project=self.project.name)) == 2
                log_fn(
                    kind,
                    source=self.path,
                    name=name,
                    drop_existing=True,
                )
            else:
                log_fn(source=self.path, name=name)
                log_fn(source=self.path, name=name)
                assert len(get_versions_fn(name, project=self.project.name)) == 2
                log_fn(source=self.path, name=name, drop_existing=True)
            assert len(get_versions_fn(name, project=self.project.name)) == 1
            delete_fn(name, delete_all_versions=True, cascade=False)
            time.sleep(2)
