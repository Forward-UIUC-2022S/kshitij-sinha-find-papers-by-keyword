# Argument 1: server key location

FILENAME="servers.txt"

servers=$(cat $FILENAME)

for LINE in $servers
do
    ssh -i $1 fdlazure@$LINE "
        rm gen_embs_server.sh other_freqs.pickle DigiCertGlobalRootCA.crt.pem golden_words.csv setup_server.sh PaperIds.pickle keyword_embs.pickle db_keywords.json; 
        rm -rf find_papers
    " &
done
wait
echo "Finished cleaning servers"