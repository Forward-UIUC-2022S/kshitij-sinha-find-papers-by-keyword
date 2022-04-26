git clone https://github.com/Forward-UIUC-2022S/kshitij-sinha-find-papers-by-keyword.git find_papers;
cd find_papers;
git checkout id-servers;
python3 -m venv .venv;
source .venv/bin/activate;
pip3 install -r requirements.txt;

# Maybe scp files from local to remove server
scp {DigiCertGlobalRootCA.crt.pem,.env,small_data/PaperIds.pickle} ksinha7@Osprey2.csl.illinois.edu:~/find_papers/