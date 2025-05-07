#!/bin/bash

sleep 5 #Esperar o banco iniciar

alembic revision --autogenerate
alembic upgrade head

uvicorn api.main:api --host 0.0.0.0