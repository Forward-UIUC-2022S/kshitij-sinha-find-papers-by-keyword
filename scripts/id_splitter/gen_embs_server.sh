# arg1: server count, arg2: server id
source .venv/bin/activate;
mkdir -p mag_data;
python3 src/generate_parallel_embs.py $1 $2;