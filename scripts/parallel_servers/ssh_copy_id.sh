#1: ssh key location

FILENAME="servers.txt"

servers=$(cat $FILENAME)

for LINE in $servers
do
    echo "Moving files" $LINE
    ssh-copy-id -i $1 fdlazure@$LINE
done
wait
echo "Finished copying ssh ids"