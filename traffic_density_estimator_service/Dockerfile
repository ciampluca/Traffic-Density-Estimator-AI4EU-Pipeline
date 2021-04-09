# Define workdir folder for all stages
# Must be renewed in the beggining of each stage
ARG WORKSPACE=/workspace
ARG PROTO_FILE=traffic_density_estimator.proto

# --------------------------------------
# Builder stage to generate .proto files
# --------------------------------------

FROM python:3.8.7-slim-buster as builder
# Renew build args
ARG WORKSPACE
ARG PROTO_FILE

COPY requirements-build.txt ${WORKSPACE}/

WORKDIR ${WORKSPACE}

RUN pip install --upgrade pip && \
    pip install -r requirements-build.txt && \
    rm requirements-build.txt

# Path for the protos folder to copy
ARG PROTOS_FOLDER_DIR=proto

COPY ${PROTOS_FOLDER_DIR} ${WORKSPACE}/

# Compile proto file and remove it
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ${PROTO_FILE}

# -----------------------------
# Stage to generate final image
# -----------------------------

FROM nvidia/cuda:10.2-cudnn7-runtime

RUN apt-get -y update \
    && apt-get install -y software-properties-common \
    && apt-get -y update \
    && add-apt-repository universe
RUN apt-get -y update
RUN apt-get -y install python3
RUN apt-get -y install python3-pip


# Renew build args
ARG WORKSPACE
ARG PROTO_FILE

ARG USER=runner
ARG GROUP=runner-group
ARG SRC_DIR=src
ARG CONF_DIR=config
ARG MODEL_DIR=model

# Create non-privileged user to run
RUN addgroup --system ${GROUP} && \
    adduser --system --no-create-home --ingroup ${GROUP} ${USER} && \
    mkdir ${WORKSPACE} && \
    chown -R ${USER}:${GROUP} ${WORKSPACE}

COPY requirements.txt ${WORKSPACE}/

WORKDIR ${WORKSPACE}

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    rm requirements.txt

# COPY .proto file to root to meet ai4eu specifications
COPY --from=builder --chown=${USER}:${GROUP} ${WORKSPACE}/${PROTO_FILE} /

# Copy generated .py files to workspace
COPY --from=builder --chown=${USER}:${GROUP} ${WORKSPACE}/*.py ${WORKSPACE}/

# Copy code to workspace
COPY --chown=${USER}:${GROUP} ${SRC_DIR} ${WORKSPACE}/

# Copy config to workspace
RUN mkdir ${WORKSPACE}/${CONF_DIR}/
COPY --chown=${USER}:${GROUP} ${CONF_DIR}/ ${WORKSPACE}/${CONF_DIR}/

# Copy model to workspace
COPY --chown=${USER}:${GROUP} ${MODEL_DIR}/ ${WORKSPACE}/${MODEL_DIR}/

# Change to non-privileged user
USER ${USER}

# Expose port 8061 according to ai4eu specifications
EXPOSE 8061

CMD ["python3", "server.py"]