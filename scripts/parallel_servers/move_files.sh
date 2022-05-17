# Argument 1: server key location

FILENAME="servers.txt"

servers=$(cat $FILENAME)

for LINE in $servers
do
    echo "Moving files to server " $LINE
    scp -i $1 {DigiCertGlobalRootCA.crt.pem,.env,data/PaperIds.pickle,data/golden_words.csv,data/keyword_embs.pickle,data/other_freqs.pickle,data/db_keywords.json} fdlazure@$LINE:~ &
done
wait
echo "Finished moving all files"