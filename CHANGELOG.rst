===========================
Community SAP Release Notes
===========================

.. contents:: Topics


v1.2.0
======

Release Summary
---------------

This is the minor release of the ``community.sap_libs`` collection.
This changelog contains changes to the modules and plugins in this collection
that have been made after the previous release.

Bugfixes
--------

- syp_system_facts - fix a typo in the usage example which lead to an error if it used as supposed.

New Modules
-----------

- sap_pyrfc - This module executes rfc functions.

v1.1.0
======

Release Summary
---------------

This is the minor release of the ``community.sap_libs`` collection.
This changelog contains all changes to the modules and plugins in this collection
that have been made after the previous release.

New Modules
-----------

System
~~~~~~

- sapcontrol - Manages SAPCONTROL

v1.0.0
======

Release Summary
---------------

This is the minor release of the ``community.sap`` collection. It is the initial relase for the ``community.sap`` collection

New Modules
-----------

Database
~~~~~~~~

saphana
^^^^^^^

- hana_query - Execute SQL on HANA

Files
~~~~~

- sapcar_extract - Manages SAP SAPCAR archives

Identity
~~~~~~~~

- sap_company - This module will manage a company entities in a SAP S4HANA environment
- sap_user - This module will manage a user entities in a SAP S4/HANA environment

System
~~~~~~

- sap_snote - This module will upload and (de)implements C(SNOTES) in a SAP S4HANA environment.
- sap_system_facts - Gathers SAP facts in a host
- sap_task_list_execute - Perform SAP Task list execution
