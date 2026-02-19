FROM python:3.12

ARG ver_sdk=0.15.0b9
ARG ver_python=0.15.0b7
ARG ver_container=0.15.0b3
ARG ver_modelserve=0.15.0b7
ARG ver_dbt=0.15.0b4
ARG ver_hera=0.15.0b4
ARG ver_flower=0.15.0b2
ARG ver_guardrail=0.15.0b1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_SYSTEM_PYTHON=1

RUN uv pip install "digitalhub[full]==${ver_sdk}" \
                   "digitalhub-runtime-python==${ver_python}" \
                   "digitalhub-runtime-container==${ver_container}"  \
                   "digitalhub-runtime-modelserve==${ver_modelserve}" \
                   "digitalhub-runtime-dbt==${ver_dbt}" \
                   "digitalhub-runtime-flower==${ver_flower}" \
                   "digitalhub-runtime-hera==${ver_hera}" \
                   "digitalhub-runtime-guardrail==${ver_guardrail}"

RUN useradd -r -m -u 8877 nonroot
USER 8877

WORKDIR /app
COPY --chown=8877:8877 . /app

ENTRYPOINT ["/app/execute.sh"]
