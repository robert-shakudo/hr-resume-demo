#!/bin/bash
set -e

PROJECT_DIR="/tmp/git/monorepo/hr-resume-demo"
cd "$PROJECT_DIR"

pip install -r backend/requirements.txt -q

cd backend
exec uvicorn main:app --host 0.0.0.0 --port 8787 --workers 1
