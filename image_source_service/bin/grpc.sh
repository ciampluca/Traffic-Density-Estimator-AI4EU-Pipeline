#!/bin/bash

cd ../proto || exit
python -m grpc_tools.protoc -I.  --python_out=. --grpc_python_out=. source.proto
mv ./*.py* ../src