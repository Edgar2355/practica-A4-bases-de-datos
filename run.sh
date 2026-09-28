#!/bin/bash

export PATH=$PATH:"/c/Users/edgar/AppData/Local/com.tinyapp.DBngin/Binaries/postgresql/18.4/bin"

echo "=========================================================="
echo " INICIANDO ORQUESTACIÓN DE LA BASE DE DATOS               "
echo "=========================================================="

if ! command -v psql &> /dev/null; then
    echo "[ERROR FATAL] Git Bash no encuentra psql. Revisa la ruta."
    exit 1
fi

echo "Verificando base de datos..."
createdb -U postgres ecommerce_logistica 2>/dev/null

echo -e "\n--- EJECUCIÓN DE DDL.sql ---"
psql -U postgres -d ecommerce_logistica -f DDL.sql

echo -e "\n--- EJECUCIÓN DE PYTHON ---"
python seeder.py

echo -e "\n--- EJECUCIÓN DE DML.sql ---"
psql -U postgres -d ecommerce_logistica -f DML.sql

echo -e "\n--- EJECUCIÓN DE DCL.sql ---"
psql -U postgres -d ecommerce_logistica -f DCL.sql

echo -e "\n=========================================================="
echo " ORQUESTACIÓN FINALIZADA CON ÉXITO                        "
echo "=========================================================="