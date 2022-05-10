# Argument 1: server password (in single quotes)

FILENAME="scripts/id_splitter/servers.txt"

LINES=$(cat $FILENAME)

for LINE in $LINES
do
    sshpass -p $1 ssh fdlazure@$LINE "
        rm gen_embs_server.sh other_freqs.pickle DigiCertGlobalRootCA.crt.pem golden_words.csv setup_server.sh PaperIds.pickle keyword_embs.pickle db_keywords.json; 
        rm -rf find_papers
    " &
done
wait
echo "Finished cleaning servers"