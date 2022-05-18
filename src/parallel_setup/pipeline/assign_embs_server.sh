# Argument 1: ssh key location

FILENAME="servers.txt"

servers=$(cat $FILENAME)
ID=0

for LINE in $servers
do
    echo "Beginning assigning keywords on server " $LINE
    ssh -i $1 fdlazure@$LINE "
        cd find_papers
        source .venv/bin/activate;
        python3 src/assign_mag_kwds.py data/golden_words.csv data/keyword_embs.pickle data/other_freqs.pickle mag_data/mag_embs.pickle mag_data/mag_id_to_ind.pickle data/db_keywords.json data/assignments.csv;
    " &
    ID=$((ID+1))
done
wait
echo "Finished assigning keywords"
echo "Copying moving papers to assignments/"

mkdir -p assignments
for LINE in $servers
do
    echo "scp-ing files from server" $LINE
    scp -i $1 fdlazure@$LINE:find_papers/data/assignments.csv assignments/$LINE.csv
    ID=$((ID+1))
done