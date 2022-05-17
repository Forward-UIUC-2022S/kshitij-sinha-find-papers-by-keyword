# Argument 1: server key location

FILENAME="servers.txt"

LINES=$(cat $FILENAME)
ID=0

for LINE in $LINES
do
    echo "Beginning generation on server " $LINE
    ssh -i $1 fdlazure@$LINE "
        cd find_papers
        source .venv/bin/activate;
        mkdir -p mag_data;
        python3 src/generate_parallel_embs.py $2 $ID;
    " &
    ID=$((ID+1))
done
wait
echo "Finished generating embeddings"