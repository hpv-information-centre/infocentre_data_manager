.. _`semantic_types`: 

Semantic types
===============

As a part of the validation system, this package includes a plugin subsystem to define semantic types for data variables. These types help refine the meaning and validity rules of a particular variable for a more strict validation procedure. For example, an ISO variable can be defined as a three-letter string corresponding to the UN iso codes for existing regions.

Each type must be implemented as a class inheriting from *SemanticType* and implementing the following methods:

* **check**: Checks if a string passed as parameter is a valid value for the type. It also accepts optional parameters in case they were necessary for some implementations.
* **help_info**: Returns a string with the description of the type for help purposes.