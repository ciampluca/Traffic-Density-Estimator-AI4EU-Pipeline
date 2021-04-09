#!/bin/bash

cd ../proto || exit
python -m grpc_tools.protoc -I.  --python_out=. --grpc_python_out=. traffic_density_estimator.proto
mv ./*.py* ../src