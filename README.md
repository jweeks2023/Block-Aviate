# Block-Aviate
A vector DB using Weaviate with a blockchain ledger.
## Prerequisites
- Python 3.0 minimum
- Docker
- These python packages:
  - Datetime
  - Json
  - Hashlib
  - Weaviate
  - Requests
## How to Use
1. Create the following docker container using the following command:
```{bash}
$ docker-compose up -d
```
2. Both containers should be running. To verify, go to [http://localhost:8080](http://localhost:8080), which should show some details about the currently running vector DB.
3. Run `blockaviate.py`. This will fill the vector DB on it's first run with the test data. Further runs of the program will only repeat the queries at the bottom of the file.
4. Results of query should be printed to console and output to `queryOut.json`. You can verify the contents of the VDB by going to [http://localhost:8080/v1/objects?class=GlobalCarbonBudget&limit=60&sort=year&order=asc](http://localhost:8080/v1/objects?class=GlobalCarbonBudget&limit=60&sort=year&order=asc) or by looking at `GCBData.json`.
## Details on `blockaviate.py`
### Blockchain
- Adapted from [this blockchain implementation](github.com/krvaibhaw/blockchain/tree/main).
- Added `crud_id`, which tracks what kind of action was performed
  - 0 - Added objects to the DB (currently it's per 10 objects inserted)
  - 1 - Queried the DB
  - 2 - Updated/Modified an entry in the DB
  - 3 - Deleted an object/schema from the DB
- History stored locally in .json file `curChain.json`.
  - While not technically functioning as a blockchain, since it isn't distributed, it functions enough to work as a proof-of-concept. This could be changed by storing data in a volume in Docker.
 
### Weaviate
- Built using Weaviate's VDB system
- When creating a new class, block is added
- Once class is created, a sample query is run and another block is added
- Not Added: Updates or deletions
  - While not present in my sample code, these should also be tracked within the blockchain
