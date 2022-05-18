# Argument 1: Location of SSH Key, Argument 2: Number of servers

SSH_KEY_LOC=$1
NUM_SERVERS=$2

bash src/parallel_setup/pipeline/move_files.sh $SSH_KEY_LOC
bash src/parallel_setup/setup_servers.sh $SSH_KEY_LOC
bash src/parallel_setup/gen_embs_servers.sh $SSH_KEY_LOC $NUM_SERVERS
bash src/parallel_setup/assign_embs_server.sh $SSH_KEY_LOC