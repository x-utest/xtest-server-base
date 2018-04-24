echo 'start remove build'
rm -rf build/
echo 'end remove build'
python3 setup.py install
rm -rf build/
