# ==============================================================================
# Multi-stage Dockerfile for Core API (Rust + rdkafka + axum)
# ==============================================================================

# Stage 1: Build binary
FROM rust:bookworm AS builder

WORKDIR /usr/src/core-api

# Install build dependencies for librdkafka and cmake
RUN apt-get update && apt-get install -y --no-install-recommends \
    cmake \
    build-essential \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy manifests
COPY Cargo.toml Cargo.lock* ./

# Dummy build to cache dependencies
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release || true
RUN rm -rf src

# Copy real source code
COPY src ./src

# Invalidate dummy binary artifacts and update timestamps to force full recompilation of core-api
RUN touch src/main.rs && rm -f target/release/deps/core_api* target/release/core-api*

# Build release artifact
RUN cargo build --release

# Stage 2: Runtime image
FROM debian:bookworm-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/src/core-api/target/release/core-api /app/core-api

ENV PORT=3000
ENV SERVER_HOST=0.0.0.0
ENV KAFKA_BROKERS=kafka:9092
ENV TRANSACTIONS_TOPIC=transactions
ENV FRAUD_ALERTS_TOPIC=fraud-alerts

EXPOSE 3000

CMD ["/app/core-api"]
