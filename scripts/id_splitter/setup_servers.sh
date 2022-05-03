# Argument 1: server password

FILENAME="scripts/id_splitter/servers.txt"

LINES=$(cat $FILENAME)

for LINE in $LINES
do
    sshpass -p $1 ssh fdlazure@$LINE "bash setup_server.sh"
done