psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d "labelizer"  <<-EOSQL
     create schema if not exists labelizer;
EOSQL

