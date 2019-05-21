.. _`data_validation`: 

Data validation
===============

To ensure data is correct before committing to the production database, this package includes a data validation plugin subsystem, implementing each kind of desired validation easily and independently of the rest.

The implemented validators should be implemented as classes inheriting from *DataValidator* with a *validate* method. This method accepts as parameter the data dictionary loaded by a data codec (see :ref:`codecs`) as well as optional arguments that can be defined for each validator. The return value should be a dictionary with three keys:

* *info*: List of strings with messages that can be considered informational.
* *warnings*: List of strings with warning messages, representing non-critical potential mistakes that should be checked before committing data.
* *errors*: List of strings with error messages, representing critical mistakes that make further handling of this data not possible.

If there are error messages the data should not be saved in the production database. In any case, new data should be reviewed with these messages in mind to anticipate future problems.