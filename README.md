# cheshire3-tests
Test Configurations for Cheshire3

## Creation Instructions


* We assume a cheshire user with /home/cheshire/ as their home directory
* Create a path ~/tests where all of the test databases will live
* Create a directory for the artifical fixture data ~/tests/test_data_alphabet
* Put the artificial data in that directory

### PostGreSQL Test

* mkdir ~/tests/postgres
* cd ~/tests/postgres
* cheshire3-init -d db_test_pgsql -t "Test PostgreSQL"

* Replace ~/tests/postgres/.cheshire3/config.xml with the PostgreSQL test configuration file provided
* __If you don't have the same path, you'll need to change line 5 of the config.xml__

* cheshire3-load -d db_test_pgsql -t rec ../test_data_alphabet/data.xml 
* (This should load the records)

* cheshire3-search -d db_test_pgsql a
* (There should be five hits, records 0,1,2,3,4)

* python ./run.py --query z
* (There should be 5 hits, note the resultSetid, which will start at 0)

* python ./run.py --fetch 0
* (There should still be 5 hits, and it should remember that you searched for z)

__Note__ that the postgresql indexStore is very inefficient, and currently does not work for me at all.  I estimate 1 hour to fix it for simple indexes without proximity, vectors or anything else fancy, and during that time would be able to estimate further work required, if any.

