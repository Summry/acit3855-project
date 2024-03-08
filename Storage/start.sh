#!/bin/bash

chmod +x wait-for-it.sh

./wait-for-it.sh db:3306

if [ $? -eq 0 ]; then
  python3 create_tables_mysql.py
  python3 app.py
else
  echo "start.sh: Database is not available (could be that MySQL did not start quick enough)"
  exit 1
fi
