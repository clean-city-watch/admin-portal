#!/bin/bash

uvicorn main:app --port 8010 --host 0.0.0.0 --root-path /ccwdev-admin-backend
