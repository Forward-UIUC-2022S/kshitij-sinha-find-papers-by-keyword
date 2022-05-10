# Argument 1: server password

FILENAME="servers.txt"

LINES=$(cat $FILENAME)

for LINE in $LINES
do
    echo "Moving files" $LINE
    sshpass -p $1 ssh fdlazure@$LINE "cp -R files/. ." &
done
wait
echo "Finished moving all files"