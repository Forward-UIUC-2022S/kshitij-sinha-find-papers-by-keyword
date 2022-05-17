# Argument 1: server key location

FILENAME="servers.txt"

LINES=$(cat $FILENAME)

for LINE in $LINES
do
    echo "Moving files" $LINE
    ssh -i $1 fdlazure@$LINE "cp -R files/. ." &
done
wait
echo "Finished moving all files"