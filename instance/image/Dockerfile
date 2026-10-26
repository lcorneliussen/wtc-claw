# check=skip=InvalidDefaultArgInFrom
# Instance image: the core image plus this deployment's tools. Instance-owned.
#
# `bin/claw build` builds core/image first and passes it in as CORE_IMAGE, so
# this file only adds what this deployment needs — a language runtime, a
# vault CLI, a patch. Keep checksums on every download. The build context is
# the repository root.
#
# This claw drives worktree collections: it carries wtc and its OpenClaw
# collection plugin (the Control UI's "Collection" panel), embedded in a pinned
# wtc release. OpenClaw verifies Git attributes with `git var
# GIT_ATTR_GLOBAL` before it publishes, which needs Git 2.42; the upstream image
# ships 2.39.
ARG CORE_IMAGE

FROM debian:bookworm-slim AS git
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ca-certificates curl xz-utils build-essential libssl-dev libcurl4-gnutls-dev libexpat1-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
ARG GIT_VERSION=2.47.3
ARG GIT_SHA256=9c2eb1250781b3e5bfef098572d07fdf132d67e6c065e4307332ade9819a1501
RUN set -eu; \
    curl --fail --silent --show-error --location --output /tmp/git.tar.xz \
      "https://mirrors.edge.kernel.org/pub/software/scm/git/git-${GIT_VERSION}.tar.xz"; \
    echo "${GIT_SHA256}  /tmp/git.tar.xz" | sha256sum --check --strict; \
    tar -xf /tmp/git.tar.xz -C /tmp; \
    make -C "/tmp/git-${GIT_VERSION}" -j"$(nproc)" prefix=/usr/local DESTDIR=/out \
      NO_TCLTK=1 NO_GETTEXT=1 NO_PERL=1 NO_PYTHON=1 install >/tmp/git-build.log 2>&1 || { tail -20 /tmp/git-build.log; exit 1; }

# dekit runs a collection's services (wtc svc). Statically linked builds.
FROM debian:bookworm-slim AS dekit
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*
ARG TARGETARCH
ARG DEKIT_VERSION=0.10.0
ARG DEKIT_SHA256_AMD64=330753d26feb9f96b79a388e730f8bd4414564520257f37bfc997c626b450f44
ARG DEKIT_SHA256_ARM64=35b2ae81a23a1b67c3f2fb95f993b26257af23270f651cc44cc1f64eba23d5fe
RUN set -eu; \
    case "${TARGETARCH:-amd64}" in \
      amd64) triple=x86_64-unknown-linux-musl; sum="$DEKIT_SHA256_AMD64" ;; \
      arm64) triple=aarch64-unknown-linux-musl; sum="$DEKIT_SHA256_ARM64" ;; \
      *) echo "unsupported arch: $TARGETARCH" >&2; exit 1 ;; \
    esac; \
    curl --fail --silent --show-error --location --output /tmp/dekit.tar.gz \
      "https://github.com/pvolok/dekit/releases/download/v${DEKIT_VERSION}/dekit-${triple}.tar.gz"; \
    echo "${sum}  /tmp/dekit.tar.gz" | sha256sum --check --strict; \
    mkdir -p /tmp/dekit && tar -xzf /tmp/dekit.tar.gz -C /tmp/dekit; \
    install -D -m 0755 "$(find /tmp/dekit -type f -name dekit | head -1)" /out/dekit

# A released wtc, checksum-pinned. Its OpenClaw plugin is embedded in the
# binary and installed by `wtc openclaw install` (configure.d/60-wtc.sh).
FROM debian:bookworm-slim AS wtc
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*
ARG TARGETARCH
ARG WTC_VERSION=0.1.54
ARG WTC_SHA256_AMD64=29e00fa9c13d80ce0a27c5ab3bd56b8ffe7fb96afc931655785f1976377f73fa
ARG WTC_SHA256_ARM64=27e76b724836b8d21c4afd8ed2d03a12e89ecee4f2e6fa6fb794eab790f43af1
RUN set -eu; \
    case "${TARGETARCH:-amd64}" in \
      amd64) sum="$WTC_SHA256_AMD64" ;; \
      arm64) sum="$WTC_SHA256_ARM64" ;; \
      *) echo "unsupported arch: $TARGETARCH" >&2; exit 1 ;; \
    esac; \
    curl --fail --silent --show-error --location --output /tmp/wtc.tar.gz \
      "https://github.com/lcorneliussen/wtc-cli/releases/download/v${WTC_VERSION}/wtc_${WTC_VERSION}_linux_${TARGETARCH:-amd64}.tar.gz"; \
    echo "$sum  /tmp/wtc.tar.gz" | sha256sum -c -; \
    mkdir -p /out/usr/local/bin; tar -xzf /tmp/wtc.tar.gz -C /tmp wtc; \
    install -m 755 /tmp/wtc /out/usr/local/bin/wtc

FROM ${CORE_IMAGE}
USER root
COPY --from=git /out/usr/local/ /usr/local/
COPY --from=wtc /out/usr/local/bin/wtc /usr/local/bin/wtc
COPY --from=dekit /out/dekit /usr/local/bin/dekit
USER node
RUN git --version && wtc host >/dev/null && dekit --version
