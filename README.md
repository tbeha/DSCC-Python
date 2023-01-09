# DSCC-Python
Python Libraries for Data Services Cloud Console (DSCC)

Revisions:
    v0.2    01/09/2023  the libraries are not yet fully tested! Use at your own risk!
                        As a consequence, the documentation is very basic.  

The whole Library is partioned into multiple classes:

    class DSCC                          - the base class
        class Audit(DSCC)               - Audit data, Events, issues
        class StorageSystem(DSCC)       - General Storage System operations  
        class Alletra6k(DSCC)           - Alletra 6k / Nimble specific command set
        class Alletra9k(DSCC)           - Alletra 9k / Primera specific command set
        class HCI(DSCC)                 - HCI command set
        class BRaaS(DSCC)               - BRaaS command set
        class ApplicationDashboar(DSCC) - Application Dashboard
        class User(DSCC)                - User commands
        class DualAuthorization(DSCC)   - Dual Authorization command set
        class FileServer(DSCC)          -   Fileserver command set
    class DsccError(Exception)          - DSCC class exception handling
