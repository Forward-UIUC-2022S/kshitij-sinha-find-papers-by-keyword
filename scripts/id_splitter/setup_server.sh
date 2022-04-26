git clone https://github.com/Forward-UIUC-2022S/kshitij-sinha-find-papers-by-keyword.git find_papers;
cd find_papers;
git checkout id-servers;
python3 -m venv .venv;
source .venv/bin/activate;
pip3 install -r requirements.txt;
mkdir data

# Maybe scp files from local to remove server
scp {DigiCertGlobalRootCA.crt.pem,.en} ksinha7@Osprey2.csl.illinois.edu:~/find_papers/
scp data/PaperIds.pickle ksinha7@Osprey2.csl.illinois.edu:~/find_papers/data/