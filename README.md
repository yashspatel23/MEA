# Arb

#### Development Setup:
```sh
# dev box
cd dev_box
./bin/init.sh  # install backend services
./bin/start.sh  # start services 
./bin/stop.sh  # stop services

# initialize databases
source conf/env_dev
pip install -r requirements.txt 
export FLASK_APP=arb/manage/cmd.py && flask setup

# dev server
python wsgi.py
```


#### To deploy:
0. Set up virtual environment if desired.
1. Install all project dependencies `sudo pip install -r requirements.txt`.
2. Configure Exchange credentials - Copy the `config_sample.py` file as `config.py` and add user credentials.
3. Run the application: `python arb/main.py`


*Required versions: Python version: 2.7.13 / OpenSSL 1.0.2l*

*Note: When running the project, if you receive the error `ImportError: No module named config`, add the base directory to PYTHONPATH in `.bash_profile`.* 

---

#### Supported Exchanges:
1. GDAX
2. CEX


#### Code validation and testing
```sh
# single test module
nose2 --config conf/nose2.cfg arb_tests.core.models.test_fixers


# run all tests
nose2 --config conf/nose2.cfg

# pre-configured validations
fab polish:ci
```

#### Notebook
```sh
# Start Notebook Server
source conf_credentialed/sensitive_env-jupyter && jupyter notebook

# Check Signals
- execute the two cells in order under the heading: Chart Signals

```
