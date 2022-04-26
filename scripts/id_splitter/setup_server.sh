git clone https://github.com/Forward-UIUC-2022S/kshitij-sinha-find-papers-by-keyword.git find_papers;
mv DigiCertGlobalRootCA.crt.pem .env find_papers;

cd find_papers;
git checkout id-servers;
python3 -m venv .venv;
source .venv/bin/activate;
pip3 install -r requirements.txt;
mkdir data;

mv ../PaperIds.pickle data;