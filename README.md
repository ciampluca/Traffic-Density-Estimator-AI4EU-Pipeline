# Traffic Density Estimator Pipeline

## Overview

This repository provides a pipeline that, given an image describing urban traffic scenarios, outputs
 an associated traffic density map as well as the estimated number of vehicles present in the scene.

The results are displayed with a web visualization interface.


## Getting Started

The different stages of the pipeline are executed as docker containers, so you need to install [Docker](https://docs.docker.com/get-docker/) to run it.

The pipeline uses Docker-Compose *(installed by default with Docker)* to run the multiple containers.
The Docker images are built using the Docker files and will be soon published on DockerHub.

To run the pipeline, execute the following instructions:

* Start the pipeline *(all images will be built using the Docker files)*:
 
 ```
 $ docker-compose up
 ```


