# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the entity Artifact
"""

from __future__ import annotations

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
        try:
            self.project.delete_artifact(name, delete_all_versions=True, cascade=False)
        except Exception:
            pass
        try:
            self.project.delete_dataitem(name, delete_all_versions=True, cascade=False)
        except Exception:
            pass
        try:
            self.project.delete_model(name, delete_all_versions=True, cascade=False)
        except Exception:
            pass

        # Log artifacts
        common_artifact_kwargs = {
            "source": self.path,
            "description": "Test artifact",
            "labels": ["test", "artifact"],
        }
        dh.log_artifact(self.project.name, name, "artifact", **common_artifact_kwargs)
        dh.log_generic_artifact(self.project.name, name, **common_artifact_kwargs)
        self.project.log_artifact(name, "artifact", **common_artifact_kwargs)
        self.project.log_generic_artifact(name, **common_artifact_kwargs)
        assert len(dh.get_artifact_versions(name, project=self.project.name)) == 4
        self.project.delete_artifact(name, delete_all_versions=True, cascade=False)

        # Log dataitems
        common_dataitem_kwargs = {
            "description": "Test dataitem",
            "labels": ["test", "dataitem"],
        }
        dh.log_table(
            self.project.name, name, source=self.path, **common_dataitem_kwargs
        )
        dh.log_table(self.project.name, name, data=self.dfpl, **common_dataitem_kwargs)
        dh.log_table(self.project.name, name, data=self.dfpd, **common_dataitem_kwargs)
        dh.log_dataitem(
            self.project.name,
            name,
            "dataitem",
            source=self.path,
            **common_dataitem_kwargs,
        )
        dh.log_dataitem(
            self.project.name, name, "table", data=self.dfpl, **common_dataitem_kwargs
        )
        dh.log_croissant(
            self.project.name, name, source=self.cr_path, **common_dataitem_kwargs
        )
        dh.log_generic_dataitem(
            self.project.name, name, source=self.path, **common_dataitem_kwargs
        )
        self.project.log_table(name, source=self.path, **common_dataitem_kwargs)
        self.project.log_table(name, data=self.dfpl, **common_dataitem_kwargs)
        self.project.log_table(name, data=self.dfpd, **common_dataitem_kwargs)
        self.project.log_dataitem(
            name, "dataitem", source=self.path, **common_dataitem_kwargs
        )
        self.project.log_dataitem(
            name, "table", data=self.dfpl, **common_dataitem_kwargs
        )
        self.project.log_generic_dataitem(
            name, source=self.path, **common_dataitem_kwargs
        )
        self.project.log_croissant(name, source=self.cr_path, **common_dataitem_kwargs)
        assert len(dh.get_dataitem_versions(name, project=self.project.name)) == 14
        self.project.delete_dataitem(name, delete_all_versions=True, cascade=False)

        # Log models
        common_model_kwargs = {
            "source": self.path,
            "description": "Test model",
            "labels": ["test", "model"],
        }
        dh.log_model(self.project.name, name, "model", **common_model_kwargs)
        dh.log_model(self.project.name, name, "huggingface", **common_model_kwargs)
        dh.log_model(self.project.name, name, "sklearn", **common_model_kwargs)
        dh.log_model(self.project.name, name, "mlflow", **common_model_kwargs)
        dh.log_generic_model(self.project.name, name, **common_model_kwargs)
        dh.log_huggingface(self.project.name, name, **common_model_kwargs)
        dh.log_sklearn(self.project.name, name, **common_model_kwargs)
        dh.log_mlflow(self.project.name, name, **common_model_kwargs)
        self.project.log_model(name, "model", **common_model_kwargs)
        self.project.log_model(name, "huggingface", **common_model_kwargs)
        self.project.log_model(name, "sklearn", **common_model_kwargs)
        self.project.log_model(name, "mlflow", **common_model_kwargs)
        self.project.log_generic_model(name, **common_model_kwargs)
        self.project.log_huggingface(name, **common_model_kwargs)
        self.project.log_sklearn(name, **common_model_kwargs)
        self.project.log_mlflow(name, **common_model_kwargs)
        assert len(dh.get_model_versions(name, project=self.project.name)) == 16
        self.project.delete_model(name, delete_all_versions=True, cascade=False)

    def test_drop_existing(self):
        """Test overwrite functionality for log methods."""
        name = "test"

        entities = [
            (
                "dataitem",
                self.project.log_dataitem,
                dh.get_dataitem_versions,
                self.project.delete_dataitem,
            ),
            (
                "artifact",
                self.project.log_artifact,
                dh.get_artifact_versions,
                self.project.delete_artifact,
            ),
            (
                "model",
                self.project.log_model,
                dh.get_model_versions,
                self.project.delete_model,
            ),
        ]

        for kind, log_fn, get_versions_fn, delete_fn in entities:
            log_fn(name, kind, source=self.path)
            log_fn(name, kind, source=self.path)
            assert len(get_versions_fn(name, project=self.project.name)) == 2
            log_fn(name, kind, source=self.path, drop_existing=True)
            assert len(get_versions_fn(name, project=self.project.name)) == 1
            delete_fn(name, delete_all_versions=True, cascade=False)
