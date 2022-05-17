#1: ssh key location

FILENAME="servers.txt"

LINES=$(cat $FILENAME)

for LINE in $LINES
do
    echo "Moving files" $LINE
    ssh-copy-id -i $1 fdlazure@$LINE
done
wait
echo "Finished copying ssh ids"