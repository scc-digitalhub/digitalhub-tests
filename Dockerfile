FROM python:3.12

ARG ver_sdk=0.14.7
ARG ver_python=0.14.2
ARG ver_container=0.14.2
ARG ver_modelserve=0.14.4
ARG ver_dbt=0.14.2
ARG ver_hera=0.14.1
ARG ver_flower=0.14.0

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN useradd -r -m -u 8877 nonroot && \
    chown -R nonroot /app
USER 8877

WORKDIR /app
COPY . /app

ENV UV_SYSTEM_PYTHON=1

RUN uv pip install "digitalhub[full]==${ver_sdk}" \
                   "digitalhub-runtime-python==${ver_python}" \
                   "digitalhub-runtime-container==${ver_container}"  \
                   "digitalhub-runtime-modelserve==${ver_modelserve}" \
                   "digitalhub-runtime-dbt==${ver_dbt}" \
                   "digitalhub-runtime-flower==${ver_flower}" \
                   "digitalhub-runtime-hera==${ver_hera}"

ENTRYPOINT ["/app/execute.sh"]
