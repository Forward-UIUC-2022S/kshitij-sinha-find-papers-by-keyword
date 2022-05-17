# Argument 1: server key location

FILENAME="servers.txt"

LINES=$(cat $FILENAME)

for LINE in $LINES
do
    echo "Moving files to server " $LINE
    ssh -i $1 fdlazure@$LINE "mkdir -p files"
    scp -i $1 {DigiCertGlobalRootCA.crt.pem,.env,data/PaperIds.pickle,data/golden_words.csv,data/keyword_embs.pickle,data/other_freqs.pickle,data/db_keywords.json} fdlazure@$LINE:~/files &
done
wait
echo "Finished moving all files"