# Argument 1: server key location

FILENAME="servers.txt"

servers=$(cat $FILENAME)

for LINE in $servers
do
    echo "Moving files" $LINE
    ssh -i $1 fdlazure@$LINE "cp -R files/. ." &
done
wait
echo "Finished moving all files"