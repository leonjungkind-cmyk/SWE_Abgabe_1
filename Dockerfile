# syntax=docker.io/docker/dockerfile-upstream:1.22.0
# check=error=true

# Copyright (C) 2023 - present, Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# Aufruf:   docker build --tag juergenzimmermann/patient:2026.4.1-hardened .
#               ggf. --no-cache
#
#           Windows:   Get-Content Dockerfile | docker run --rm --interactive hadolint/hadolint:v2.14.0-debian
#           macOS:     cat Dockerfile | docker run --rm --interactive hadolint/hadolint:v2.14.0-debian
#
#           docker debug juergenzimmermann/patient:2026.4.1-hardened
#           docker scout sbom juergenzimmermann/patient:2026.4.1-hardened
#           docker scout cves juergenzimmermann/patient:2026.4.1-hardened
#           docker save juergenzimmermann/patient:2026.4.1-hardened > patient.tar
#           docker scout attest get dhi.io/python:3.14.3-debian13 --predicate-type https://slsa.dev/provenance/v0.2 --verify
#               https://docs.docker.com/dhi/core-concepts/slsa

# https://docs.docker.com/engine/reference/builder/#syntax
# https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/reference.md
# https://hub.docker.com/r/docker/dockerfile
# https://docs.docker.com/build/building/multi-stage
# https://docs.docker.com/dhi
# https://testdriven.io/blog/docker-best-practices
# https://containers.gitbook.io/build-containers-the-hard-way
# https://wiki.debian.org/DebianReleases
# https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile
# https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile
# https://www.saaspegasus.com/guides/uv-deep-dive

# ARG: "build-time" Variable
# ENV: "build-time" und "runtime" Variable
ARG PYTHON_MAIN_VERSION=3.14
ARG PYTHON_VERSION=${PYTHON_MAIN_VERSION}.3
ARG UV_VERSION=0.10.11

# ------------------------------------------------------------------------------
# S t a g e   b u i l d e r
# ------------------------------------------------------------------------------
# dhi.io/uv:0.10.10-debian13
FROM ghcr.io/astral-sh/uv:${UV_VERSION}-python${PYTHON_MAIN_VERSION}-dhi AS builder

WORKDIR /opt/app

# Enable bytecode compilation
# Copy from the cache instead of linking since it's a mounted volume
# Kein Python-Download erforderlich
# https://github.com/astral-sh/uv/issues/8635#issuecomment-2759670742
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_NO_MANAGED_PYTHON=true \
    UV_SYSTEM_PYTHON=true

# .venv erstellen
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    ["/usr/local/bin/uv", "venv"]
# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    ["/usr/local/bin/uv", "sync", "--frozen", "--no-install-project", "--no-default-groups", "--no-editable"]

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY LICENSE README.md pyproject.toml ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    ["/usr/local/bin/uv", "sync", "--frozen", "--no-default-groups", "--no-editable"]

# ------------------------------------------------------------------------------
# S t a g e   f i n a l
# ------------------------------------------------------------------------------
FROM dhi.io/python:${PYTHON_VERSION}-debian13 AS final

# Anzeige bei "docker inspect ..."
# https://specs.opencontainers.org/image-spec/annotations
# https://spdx.org/licenses
# MAINTAINER ist deprecated https://docs.docker.com/engine/reference/builder/#maintainer-deprecated
LABEL org.opencontainers.image.title="patient" \
    org.opencontainers.image.description="Appserver patient mit Basis-Image Trixie hardened" \
    org.opencontainers.image.version="2026.4.1-hardened" \
    org.opencontainers.image.licenses="GPL-3.0-or-later" \
    org.opencontainers.image.authors="Juergen.Zimmermann@h-ka.de"

# "working directory" fuer die Docker-Kommandos RUN, ENTRYPOINT, CMD, COPY und ADD
WORKDIR /opt/app

# User "nonroot" statt User "root"
USER nonroot

COPY --from=builder --chown=nonroot:nonroot /opt/app ./

# Place executables in the environment at the front of the path
ENV PATH="/opt/app/.venv/bin:$PATH"

EXPOSE 8000

STOPSIGNAL SIGINT

ENTRYPOINT ["python", "-m", "patient"]
