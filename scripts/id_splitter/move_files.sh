# Argument 1: server password

FILENAME="scripts/id_splitter/servers.txt"

LINES=$(cat $FILENAME)

for LINE in $LINES
do
    echo $LINE
    sshpass -p $1 scp {DigiCertGlobalRootCA.crt.pem,.env,data/PaperIds.pickle,scripts/id_splitter/gen_embs_server.sh,data/golden_words.csv,data/keyword_embs.pickle,data/other_freqs.pickle} fdlazure@$LINE:~ &
done
wait
echo "Finished moving all files"