# Argument 1: Location of SSH Key, Argument 2: Number of servers

SSH_KEY_LOC = $1
NUM_SERVERS = $2

bash pipeline/move_files.sh $1
bash pipeline/setup_servers.sh $1
bash pipeline/gen_embs_servers.sh $1 $2
bash pipeline/assign_embs_server.sh $1