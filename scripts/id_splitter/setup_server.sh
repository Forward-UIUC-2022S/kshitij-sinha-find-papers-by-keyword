git clone https://github.com/Forward-UIUC-2022S/kshitij-sinha-find-papers-by-keyword.git find_papers;

mkdir find_papers/data

mv DigiCertGlobalRootCA.crt.pem .env find_papers;
mv keyword_embs.pickle other_freqs.pickle golden_words.csv PaperIds.pickle find_papers/data;

cd find_papers;
git checkout id-servers;
python3 -m venv .venv;
source .venv/bin/activate;
pip3 install -r requirements.txt;