# Argument 1: server password, Argument 2: Number of servers

FILENAME="scripts/id_splitter/servers.txt"

LINES=$(cat $FILENAME)
ID=0

for LINE in $LINES
do
    echo "Beginning generation on server " $LINE
    sshpass -p $1 ssh fdlazure@$LINE "
        cd find_papers
        source .venv/bin/activate;
        mkdir -p;
        python3 src/assign_mag_kwds.py data/golden_words.csv data/keyword_embs.pickle data/other_freqs.pickle mag_data/mag_embs.pickle mag_data/mag_id_to_ind.pickle data/assignments.csv;
    " &
    ID=$((ID+1))
done
wait
echo "Finished assigning keywords"