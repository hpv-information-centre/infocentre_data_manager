.. _`codecs`: 

Data codecs
===============

The codec modules will load or store the HPV Information Centre data tables and its corresponding references via a particular interface (excel files, SQL, ...). By using these, scientific data can be easily translated between different formats. For a more convenient conversion between formats, the *convert* method is available (see API reference).


Intermediate data representation
---------------------------------

A python dictionary with the following structure should be built by each codec's load method. Besides these, other values can be added but with no guarantees that other codecs will consider them and therefore the information can potentially be lost.

* **general**: A single row dataframe with the following columns:
   * **table_name**: The table name. If the name contains '_m*_' the corresponding number will be extracted as the data module.
   * **contents**: A description of the table contents.
   * **data_manager**: The person/people responsible for the table maintenance.
   * **comments**: Comments about the table.
* **variables**: A dataframe with the following columns:
   * **variable**: Name of the variable, used as identifier.
   * **description**: Description of the variable.
   * **type**: Semantic type of the variable (will be used by type validators, see :ref:`data_validation`).
* **data**: A dataframe with the actual scientific data. Its columns should match those defined in the **variables** dictionary.
* **sources**: A dataframe with the sources associated with the data. Its columns should be:
   * **iso**: ISO3 code of the region associated with that source. A ``-99`` value indicates that the source applies to all regions.
   * **strata_variable**: Name of the variable to apply the *strata* filter (see **strata_value** below).
   * **strata_value**: Value of the **strata_variable** of the data rows associated with that source. If both *strata* keys are ``-9999`` the source is not filtered using this method.
   * **applyto_variable**: Data column associated with the source. If this value is ``-9999`` the source is associated with the whole row.
   * **value**: Text of the source.
* **notes**: A dataframe with the notes associated with the data. Its columns follow the same structure as **sources**.
* **methods**: A dataframe with the methods associated with the data. Its columns follow the same structure as **sources**.
* **years**: A dataframe with the estimate years associated with the data. Its columns follow the same structure as **sources**.
* **dates**: A dataframe with relevant date information about the data. It has four values:
   * **date_accessed**: When the source data was accessed by the data managers.
   * **date_closing**: When the source data was valid.
   * **date_published**: When the source data was published in a HPV Information Centre report or other publication.
   * **date_delivery**: When the source data was delivered and updated to the HPV Information Centre database.