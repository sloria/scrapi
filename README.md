scrapi
======

```master``` build status: [![Build Status](https://travis-ci.org/CenterForOpenScience/scrapi.svg?branch=master)](https://travis-ci.org/CenterForOpenScience/scrapi)


```develop``` build status: [![Build Status](https://travis-ci.org/CenterForOpenScience/scrapi.svg?branch=develop)](https://travis-ci.org/CenterForOpenScience/scrapi)


[![Coverage Status](https://coveralls.io/repos/CenterForOpenScience/scrapi/badge.svg?branch=develop)](https://coveralls.io/r/CenterForOpenScience/scrapi?branch=develop)
[![Code Climate](https://codeclimate.com/github/CenterForOpenScience/scrapi/badges/gpa.svg)](https://codeclimate.com/github/CenterForOpenScience/scrapi)

## Getting started

- To run absolutely everyting, you will need to:
    - Install requirements
    - Install Elasticsearch
    - Install Cassandra, or Postgres, or both (optional)
    - Install RabbitMQ (optional)
- You do not have to install RabbitMQ if you're only running the harvesters locally.
- Both Cassandra and Postgres aren't really necessary, you can choose which one you'd like, or use both. If you install neither, you can use local storage instead. In your settings, you'll specify a CANONICAL_PROCESSOR, just make sure that one is installed.


### Requirements

- Create and enter virtual environment for scrapi, and go to the top level project directory. From there, run

```bash
$ pip install -r requirements.txt
```
Or, if you'd like some nicer testing and debugging utilities in addition to the core requirements, run
```bash
$ pip install -r dev-requirements.txt
```

This will also install the core requirements like normal.

### Installing Elasticsearch

_Note: Elasticsearch requires JDK 7._

#### Mac OSX

```bash
$ brew install homebrew/versions/elasticsearch17
```

#### Ubuntu

1. Download and install the Public Signing Key.
   ```bash
   $ wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -
   ```

2. Add the ElasticSearch repository to yout /etc/apt/sources.list.
   ```bash
   $ sudo add-apt-repository "deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main"
   ```

3. Install the package
   ```bash
   $ sudo apt-get update
   $ sudo apt-get install elasticsearch
```

#### Running

```bash
$ elasticsearch
```


### Installing Postgres

Postgres is required only if "postgres" is specified in your settings, or if RECORD_HTTP_TRANSACTIONS is set to ```True```.

#### Mac OSX

```bash
$ brew install postgresql
$ ln -sfv /usr/local/homebrew/opt/postgresql/*.plist ~/Library/LaunchAgents
$ launchctl load ~/Library/LaunchAgents/homebrew.mxcl.postgresql.plist
```

#### Ubuntu

```bash
$ sudo apt-get update
$ sudo apt-get install postgresql
$ service postgresql start
```

#### Running

Inside your scrapi checkout:

```bash
$ createdb scrapi
$ invoke apidb
```


### Installing Cassandra

Cassandra is required only if "cassandra" is specified in your settings, or if RECORD_HTTP_TRANSACTIONS is set to ```True```.

_Note: Cassandra requires JDK 7._

#### Mac OSX

```bash
$ brew install cassandra
```

#### Ubuntu

1. Check which version of Java is installed by running the following command:
   ```bash
   $ java -version
   ```
   Use the latest version of Oracle Java 7 on all nodes.

2. Add the DataStax Community repository to the /etc/apt/sources.list.d/cassandra.sources.list
   ```bash
   $ echo "deb http://debian.datastax.com/community stable main" | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list
   ```

3.  Add the DataStax repository key to your aptitude trusted keys.
    ```bash
    $ curl -L http://debian.datastax.com/debian/repo_key | sudo apt-key add -
    ```

4. Install the package.
   ```bash
   $ sudo apt-get update
   $ sudo apt-get install cassandra
   ```

#### Running

```bash
$ cassandra
```


Or, if you'd like your cassandra session to be bound to your current session, run:
```bash
$ cassandra -f
```

and you should be good to go.


### RabbitMQ (optional)

_Note, if you're developing locally, you do not have to run RabbitMQ!_

#### Mac OSX

```bash
$ brew install rabbitmq
```

#### Ubuntu

```bash
$ sudo apt-get install rabbitmq-server
```


### Settings

You will need to have a local copy of the settings. Copy local-dist.py into your own version of local.py:

```bash
cp scrapi/settings/local-dist.py scrapi/settings/local.py
```

Copy over the api settings:

```bash
cp api/api/settings/local-dist.py api/api/settings/local.py
```

If you installed Cassandra, Postgres, and Elasticsearch earlier, you will want add something like the following configuration to your local.py, based on the databases you have:

```python
RECORD_HTTP_TRANSACTIONS = True  # Only if cassandra or postgres are installed

RAW_PROCESSING = ['cassandra', 'postgres']
NORMALIZED_PROCESSING = ['cassandra', 'postgres', 'elasticsearch']
CANONICAL_PROCESSOR = 'postgres'
RESPONSE_PROCESSOR = 'postgres'
```

For raw and normalized processing, add the databases you have installed. Only add elasticsearch to normalized processing, as it does not have a raw processing module.

```RAW_PROCESSING``` and ```NORMALIZED_PROCESSING``` are both lists, so you can add as many processors as you wish. ```CANONICAL_PROCESSOR``` and ```RESPONSE_PROCESSOR``` both are single processors only.

_note: Cassandra processing will soon be phased out, so we recommend using Postgres for your processing needs. Either one will work for now!_

If you'd like to use local storage, you will want to make sure your local.py has the following configuration:

```python
RECORD_HTTP_TRANSACTIONS = False

NORMALIZED_PROCESSING = ['storage']
RAW_PROCESSING = ['storage']
```

This will save all harvested/normalized files to the directory ```archive/<source>/<document identifier>```

_note: Be careful with this, as if you harvest too many documents with the storage module enabled, you could start experiencing inode errors_

If you'd like to be able to run all harvesters, you'll need to [register for a PLOS API key](http://api.plos.org/registration/), a [Harvard Dataverse API Key](https://dataverse.harvard.edu/dataverseuser.xhtml?editMode=CREATE&redirectPage=%2Fdataverse.xhtml), and a [Springer API Key](https://dev.springer.com/signup).

Add your API keys to the following line to your local.py file:
```
PLOS_API_KEY = 'your-api-key-here'
HARVARD_DATAVERSE_API_KEY = 'your-api-key-here'
SPRINGER_API_KEY = 'your-api-key-here'
```

### Running the scheduler (optional)

- from the top-level project directory run:

```bash
$ invoke beat
```

to start the scheduler, and

```bash
$ invoke worker
```

to start the worker.


### Harvesters
Run all harvesters with

```bash
$ invoke harvesters
```

or, just one with

```bash
$ invoke harvester harvester-name
```

For testing local development, running the ```mit``` harvester is recommended.

Note: harvester-name is the same as the defined harvester "short name".

Invoke a harvester for a certain start date with the ```--start``` or ```-s```argument. Invoke a harvester for a certain end date with the ```--end``` or ```-e```argument.

For example, to run a harvester between the dates of March 14th and March 16th 2015, run:

```bash
$ invoke harvester harvester-name --start 2015-03-14 --end 2015-03-16
```

Either --start or --end can also be used on their own. Not supplying arguments will default to starting the number of days specified in ```settings.DAYS_BACK``` and ending on the current date.

If --end is given with no --start, start will default to the number of days specified in ```settings.DAYS_BACK``` before the given end date.


### Automated OAI PMH Harvester Creation
Writing a harvester for inclusion with scrAPI?  If the provider makes their metadata available using the OAI-PMH standard, then [autooai](https://github.com/erinspace/autooai) is a utility that will do most of the work for you.


### Working with the OSF

To configure scrapi to work in a local OSF dev environment:

1. Ensure `'elasticsearch'` is in the `NORMALIZED_PROCESSING` list in `scrapi/settings/local.py`
1. Run at least one harvester
1. Configure the `share_v2` alias
1. Generate the provider map

#### Aliases

Multiple SHARE indices may be used by the OSF. By default, OSF uses the ```share_v2``` index. Activate this alias by running:

```bash
$ inv alias share share_v2
```

Note that aliases must be activated before the provider map is generated.

#### Provider Map

```bash
$ inv alias share share_v2
$ inv provider_map 
```

#### Delete the Elasticsearch index

To remove both the ```share``` and ```share_v2``` indices from elasticsearch:

```bash
$ curl -XDELETE 'localhost:9200/share*'
```

### Testing

- To run the tests for the project, just type

```bash
$ invoke test
```

and all of the tests in the 'tests/' directory will be run.


### Pitfalls

#### Installing with anaconda
If you're using anaconda on your system at all, using pip to install all requirements from scratch from requirements.txt and dev-requirements.txt results in an Import Error when invoking tests or harvesters.

Example:

ImportError: dlopen(/Users/username/.virtualenvs/scrapi2/lib/python2.7/site-packages/lxml/etree.so, 2): Library not loaded: libxml2.2.dylib
  Referenced from: /Users/username/.virtualenvs/scrapi2/lib/python2.7/site-packages/lxml/etree.so
  Reason: Incompatible library version: etree.so requires version 12.0.0 or later, but libxml2.2.dylib provides version 10.0.0

To fix:
- run ```pip uninstall lxml```
- remove the anaconda/bin from your system path in your bash_profile
- reinstall requirements as usual

Answer found in [this stack overflow question and answer](http://stackoverflow.com/questions/23172384/lxml-runtime-error-reason-incompatible-library-version-etree-so-requires-vers)

### Institutions!
Scrapi supports the addition of institutions in a separate index (` institutions `). Unlike data stored in the ` share ` indices, institution's metadata is updated
much less frequently, meaning that simple parsers can be used to manually load data from providers instead of using scheduled harvesters.

Currently, data from [GRID](https://grid.ac/) and [IPEDS](https://nces.ed.gov/ipeds/) is supported:
- GRID: Provides data on international research facilities. The currently used dataset is ` grid_2015_11_05.json `, which can be found [here](https://grid.ac/downloads) or, for the full dataset, [here](http://files.figshare.com/2409936/grid_2015_11_05.json).  To use this dataset
    move the file to '/institutions/', or override the file path and/or name on ` tasks.py `. This can be individually loaded using the function ` grid() ` in ` tasks.py `.
- IPEDS: Provides data on secondary education institutions in the US. The currently used dataset is ` hd2014.csv `, which can be found [here](https://nces.ed.gov/ipeds/Home/UseTheData), by clicking on
    Survey Data -> Complete data files -> 2014 -> Institutional Characteristics -> Directory information, or can be downloaded directly [here](https://nces.ed.gov/ipeds/datacenter/data/HD2014.zip). This will give you a file named `HD2014.zip`, which can be unzipped into `hd2014.csv` by running ` unzip HD2014.zip `. To use this dataset
    move the file to '/institutions/', or override the file path and/or name on ` tasks.py `. This can be individually loaded using the function ` ipeds() ` in ` tasks.py `.

Running ` invoke institutions ` will properly load up institution data into elastic search provided the datasets are provided.
