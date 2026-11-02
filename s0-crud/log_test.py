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
        self.entity_names = {
            "artifact": "test-artifact",
            "dataitem": "test-dataitem",
            "table": "test-table",
            "croissant": "test-croissant",
            "model": "test-model",
            "mlflow": "test-mlflow",
            "sklearn": "test-sklearn",
            "huggingface": "test-huggingface",
            "tvm-ir": "test-tvm-ir",
            "tvm-so": "test-tvm-so",
        }

    def _cleanup_entities(self):
        cleanup_steps = [
            (
                ("artifact",),
                self.project.list_artifacts,
                self.project.delete_artifact,
            ),
            (
                ("dataitem", "table", "croissant"),
                self.project.list_dataitems,
                self.project.delete_dataitem,
            ),
            (
                ("model", "mlflow", "sklearn", "huggingface", "tvm-ir", "tvm-so"),
                self.project.list_models,
                self.project.delete_model,
            ),
        ]
        for kinds, list_fn, delete_fn in cleanup_steps:
            existing_names = {entity.name for entity in list_fn()}
            for kind in kinds:
                name = self.entity_names[kind]
                if name in existing_names:
                    delete_fn(name, delete_all_versions=True, cascade=False)
                    time.sleep(4)

    def test_log_methods(self):
        """Test all log methods for different entities."""

        self._cleanup_entities()

        common_artifact_kwargs = {
            "source": self.path,
            "description": "Test artifact",
            "labels": ["test", "artifact"],
        }
        common_dataitem_kwargs = {
            "description": "Test dataitem",
            "labels": ["test", "dataitem"],
        }
        common_model_kwargs = {
            "source": self.path,
            "description": "Test model",
            "labels": ["test", "model"],
        }

        log_methods = [
            (
                "artifact",
                dh.log_artifact,
                self.project.log_artifact,
                dh.get_artifact_versions,
                self.project.delete_artifact,
                [common_artifact_kwargs, common_artifact_kwargs],
                4,
            ),
            (
                "table",
                dh.log_table,
                self.project.log_table,
                dh.get_dataitem_versions,
                self.project.delete_dataitem,
                [
                    {"source": self.path, **common_dataitem_kwargs},
                    {"data": self.dfpl, **common_dataitem_kwargs},
                    {"data": self.dfpd, **common_dataitem_kwargs},
                ],
                6,
            ),
            (
                "dataitem",
                dh.log_dataitem,
                self.project.log_dataitem,
                dh.get_dataitem_versions,
                self.project.delete_dataitem,
                [{"source": self.path, **common_dataitem_kwargs}],
                2,
            ),
            (
                "croissant",
                dh.log_croissant,
                self.project.log_croissant,
                dh.get_dataitem_versions,
                self.project.delete_dataitem,
                [{"source": self.cr_path, **common_dataitem_kwargs}],
                2,
            ),
            (
                "model",
                dh.log_model,
                self.project.log_model,
                dh.get_model_versions,
                self.project.delete_model,
                [common_model_kwargs, common_model_kwargs],
                4,
            ),
            (
                "sklearn",
                dh.log_sklearn,
                self.project.log_sklearn,
                dh.get_model_versions,
                self.project.delete_model,
                [common_model_kwargs],
                2,
            ),
            (
                "mlflow",
                dh.log_mlflow,
                self.project.log_mlflow,
                dh.get_model_versions,
                self.project.delete_model,
                [common_model_kwargs],
                2,
            ),
        ]

        for (
            entity_type,
            log_fn,
            project_log_fn,
            get_versions_fn,
            delete_fn,
            kwargs_list,
            expected_versions,
        ) in log_methods:
            name = self.entity_names[entity_type]
            for kwargs in kwargs_list:
                log_fn(self.project.name, name=name, **kwargs)
                project_log_fn(name=name, **kwargs)
            assert (
                len(get_versions_fn(name, project=self.project.name))
                == expected_versions
            )
            delete_fn(name, delete_all_versions=True, cascade=False)
        time.sleep(4)

    def test_register_methods(self):
        """Test all register methods for different entities."""
        self._cleanup_entities()

        register_methods = [
            (
                "artifact",
                dh.register_artifact,
                self.project.register_artifact,
                dh.get_artifact_versions,
                self.project.delete_artifact,
                self.path,
                {},
            ),
            (
                "dataitem",
                dh.register_dataitem,
                self.project.register_dataitem,
                dh.get_dataitem_versions,
                self.project.delete_dataitem,
                self.path,
                {},
            ),
            (
                "table",
                dh.register_table,
                self.project.register_table,
                dh.get_dataitem_versions,
                self.project.delete_dataitem,
                self.path,
                {},
            ),
            (
                "croissant",
                dh.register_croissant,
                self.project.register_croissant,
                dh.get_dataitem_versions,
                self.project.delete_dataitem,
                self.cr_path,
                {},
            ),
            (
                "model",
                dh.register_model,
                self.project.register_model,
                dh.get_model_versions,
                self.project.delete_model,
                self.path,
                {},
            ),
            (
                "mlflow",
                dh.register_mlflow,
                self.project.register_mlflow,
                dh.get_model_versions,
                self.project.delete_model,
                self.path,
                {},
            ),
            (
                "sklearn",
                dh.register_sklearn,
                self.project.register_sklearn,
                dh.get_model_versions,
                self.project.delete_model,
                self.path,
                {},
            ),
            (
                "huggingface",
                dh.register_huggingface,
                self.project.register_huggingface,
                dh.get_model_versions,
                self.project.delete_model,
                "hf://myorg/textclassifier",
                {},
            ),
            (
                "tvm-ir",
                dh.register_tvm_ir,
                self.project.register_tvm_ir,
                dh.get_model_versions,
                self.project.delete_model,
                self.path,
                {},
            ),
            (
                "tvm-so",
                dh.register_tvm_so,
                self.project.register_tvm_so,
                dh.get_model_versions,
                self.project.delete_model,
                self.path,
                {},
            ),
        ]

        for (
            entity_type,
            register_fn,
            project_register_fn,
            get_versions_fn,
            delete_fn,
            source,
            kwargs,
        ) in register_methods:
            name = self.entity_names[entity_type]
            register_fn(self.project.name, source=source, name=name, **kwargs)
            project_register_fn(source=source, name=name, **kwargs)
            assert len(get_versions_fn(name, project=self.project.name)) == 2
            delete_fn(name, delete_all_versions=True, cascade=False)
            time.sleep(4)

    def test_drop_existing(self):
        """Test overwrite functionality for log methods."""
        self._cleanup_entities()

        entities = [
            (
                self.entity_names["dataitem"],
                self.project.log_dataitem,
                dh.get_dataitem_versions,
                self.project.delete_dataitem,
            ),
            (
                self.entity_names["artifact"],
                self.project.log_artifact,
                dh.get_artifact_versions,
                self.project.delete_artifact,
            ),
            (
                self.entity_names["model"],
                self.project.log_model,
                dh.get_model_versions,
                self.project.delete_model,
            ),
        ]

        for name, log_fn, get_versions_fn, delete_fn in entities:
            log_fn(source=self.path, name=name)
            log_fn(source=self.path, name=name)
            assert len(get_versions_fn(name, project=self.project.name)) == 2
            log_fn(source=self.path, name=name, drop_existing=True)
            assert len(get_versions_fn(name, project=self.project.name)) == 1
            delete_fn(name, delete_all_versions=True, cascade=False)
            time.sleep(4)
