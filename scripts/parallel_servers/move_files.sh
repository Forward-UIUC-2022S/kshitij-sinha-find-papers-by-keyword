# Argument 1: server password

FILENAME="servers.txt"

LINES=$(cat $FILENAME)

for LINE in $LINES
do
    echo "Moving files to server " $LINE
    sshpass -p $1 scp {DigiCertGlobalRootCA.crt.pem,.env,data/PaperIds.pickle,scripts/id_splitter/gen_embs_server.sh,data/golden_words.csv,data/keyword_embs.pickle,data/other_freqs.pickle,data/db_keywords.json} fdlazure@$LINE:~ &
done
wait
echo "Finished moving all files"