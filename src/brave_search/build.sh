#!/bin/bash
pip install --target ./package -r requirements.txt
cd package
zip -r ../deployment_brave_search.zip .
cd ..
zip deployment_brave_search.zip lambda_function.py   
