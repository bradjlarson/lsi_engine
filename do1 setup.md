//This installs numpy, scipy, ipython, gensim, crm114, a python wrapper for crm114, vim, git, nltk, scikit-learn, and grabs the code I've already written

sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
apt-get install python-setuptools
easy_install pip
pip install gensim
pip install simserver
apt-get crm114
mkdir python
git clone https://github.com/samdeane/code-snippets.git
cp code-snippets/python/crm.py crm.py
rm -rf code-snippets
apt-get install vim
apt-get install git
git clone https://github.com/bradjlarson/lsi_engine.git
pip install -U pyyaml nltk
pip install -U scikit-learn
pip install pattern
