echo "Notice: You can access up-to-date docs at https://toppy.rtfd.io/ now."
python3 -m pip install -Ur docs/requirements.txt --user
cd docs
make html
python3 -m http.server -d ./_build/html
