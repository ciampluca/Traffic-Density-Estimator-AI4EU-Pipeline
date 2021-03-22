#!/bin/bash

cd ../protos || exit
python -m grpc_tools.protoc -I.  --python_out=. --grpc_python_out=. visualization.proto
mv ./*.py* ../src