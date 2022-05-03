FILENAME="data/servers.txt"

LINES=$(cat $FILENAME)

for LINE in $LINES
do
    scp {DigiCertGlobalRootCA.crt.pem,.env,data/PaperIds.pickle,scripts/id_splitter/gen_embs_server.sh,scripts/id_splitter/setup_server.sh,data/golden_words.csv,data/keyword_embs.pickle,data/other_freqs.pickle} fdlazure@$LINE:~
done