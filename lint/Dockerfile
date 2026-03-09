FROM rust:1.93 AS builder
WORKDIR /app
COPY Cargo.toml Cargo.lock* ./
COPY src ./src
RUN cargo build --release

FROM builder AS test
RUN rustup component add rustfmt clippy
RUN cargo fmt -- --check
RUN cargo clippy -- -D warnings
RUN cargo test
RUN cargo run --release -- check --help

FROM debian:stable-slim AS production
COPY --from=builder /app/target/release/kk-lint /usr/local/bin/kk-lint
EXPOSE 3000
ENTRYPOINT ["kk-lint", "--processed", "/media/processed"]
CMD ["serve", "--host", "0.0.0.0", "--port", "3000"]
