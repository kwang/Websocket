# Multi-stage build for Java gRPC Server
FROM maven:3.9.5-openjdk-17 AS builder

# Set working directory
WORKDIR /app

# Copy pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy source code
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests

# Runtime stage
FROM openjdk:17-jre-slim

# Install FFmpeg for video processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy the built JAR from builder stage
COPY --from=builder /app/target/interview-grpc-server-1.0.0.jar app.jar

# Create directories for recordings
RUN mkdir -p recordings backups && chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Expose ports
EXPOSE 9090 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"] 