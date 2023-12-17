'''
Block-Aviate: A Blockchain-ledger for a Weaviate Database
Created by Jason Weeks
'''
# Importing modules
import datetime      # To keep track of time, as each block has its own timestamp (exact date and time at which the block is created)
import json          # For encoding the blocks before hashing them
import hashlib       # For finding hashes for the blocks
import weaviate
import timeit

file_name = "curChain.json"

# Initial blockchain implementation found here: https://github.com/krvaibhaw/blockchain/tree/main

# Building the blockchain architecture

class Blockchain:

    def __init__(self):
        
        # List of chains (to cryptographically link the blocks)
        self.chain = []
        
        # Imports current chain to instance
        with open(file_name, mode='r', encoding='utf-8') as f:
            for line in f:
                block_json = json.loads(line)
                self.chain.append(block_json)
        
        # Creating the Genesis Block if no entries in BC
        if not self.chain:
            self.createblock(proof = 1, prevhash = "0", crud_id="-1")
        

    def createblock(self, proof, prevhash, crud_id):
        # Returns if block already exists (usually genesis block); uses prevhash since it's unique
        if any(x['prevhash'] == prevhash for x in self.chain):
            return
        # Defining the structure of our block
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'prevhash': prevhash,
                 'crud_id': crud_id}    # crud_id: which operation was performed; 0 - create, 1 - read, 2 - update, 3 - delete

        # Establishing a cryptographic link
        self.chain.append(block)
        
        # Exports block to file
        with open(file_name, mode='a', encoding='utf-8') as f:
            f.write(json.dumps(block) + "\n")
        return block

    def getprevblock(self):
        return self.chain[-1]
    
    def proofofwork(self, prevproof):
        newproof = 1
        checkproof = False

        # Defining crypto puzzle for the miners and iterating until able to mine it 
        while checkproof is False:
            op = hashlib.sha256(str(newproof**2 - prevproof**5).encode()).hexdigest()
            
            if op[:5] == "00000":
                checkproof = True
            else:
                newproof += 1
        
        return newproof

    def hash(self, block):
        encodedblock = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encodedblock).hexdigest()

    def ischainvalid(self, chain):
        prevblock = chain[0]   # Initilized to Genesis block
        blockindex = 1         # Initilized to Next block

        while blockindex < len(chain):

            # First Check : For each block check if the previous hash field is equal to the hash of the previous block
            #               i.e. to verify the cryptographic link
            
            currentblock = chain[blockindex]
            if currentblock['prevhash'] != self.hash(prevblock):
                return False

            # Second Check : To check if the proof of work for each block is valid according to problem defined in proofofwork() function
            #                i.e. to check if the correct block is mined or not

            prevproof = prevblock['proof']
            currentproof = currentblock['proof']
            op = hashlib.sha256(str(currentproof**2 - prevproof**5).encode()).hexdigest()
            
            if op[:5] != "00000":
                return True

            prevblock = currentblock
            blockindex += 1

        return True

# Creating a blockchain based on architecture defined
blockchain = Blockchain()

# Method for adding blocks to BC
def addBlock(crud_id):
    prevblock = blockchain.getprevblock()
    prevproof = prevblock['proof']
    proof = blockchain.proofofwork(prevproof)
    prevhash = blockchain.hash(prevblock)
    blockchain.createblock(proof, prevhash, crud_id)

#################################################################################################

# Initializing Weaviate DB here
client = weaviate.Client(
    url = "http://localhost:8080",  # Replace with your endpoint
)


class_obj = { 
    "class": "GlobalCarbonBudget",
    "vectorizer": "text2vec-contextionary",
    "moduleConfig": {
        "text2vec-contextionary": {
            "vectorizeClassName": True
        }    
    }
}

if not client.schema.exists(class_name=class_obj["class"]): # Checks if current class_obj class already exists within DB. If yes, skip insertion, otherwise insert the object
    client.schema.create_class(class_obj) # Creates class based on this
    
    json_file = open('./InputData/global-carbon-budget.json')
    data = json.load(json_file);
    
    client.batch.configure(batch_size=30, num_workers=2)  # Configure batch
    with client.batch as batch:  # Initialize a batch process 
    # Imports data from .json file to VDB; each group of insertions given a block in BC
        for (i, d) in enumerate(data):  # Batch import data
            print(f"importing entry: {i+1}")
            properties = {
                "year": d["Year"],
                "fossilFuelandIndustry": d["Fossil-Fuel-And-Industry"],
                "landUseChangeEmissions": d["Land-Use-Change-Emissions"],
                "atmosphericGrowth": d["Atmospheric-Growth"],
                "oceanSink": d["Ocean-Sink"],
                "landSink": d["Land-Sink"],
                "budgetImbalance": d["Budget-Imbalance"],
            }
            batch.add_data_object(
                data_object=properties,
                class_name="GlobalCarbonBudget",
            )
            if i % 10 == 0:
                addBlock(0)
        # end for
    #end with

    json_file.close()

def Query():    # A method used to test querying 
    print("Query: Print all entries in GlobalCarbonBudget in ascending order by year.")
    response = (
        client.query
        .get("GlobalCarbonBudget",
             ["year",
              "fossilFuelandIndustry",
              "landUseChangeEmissions",
              "atmosphericGrowth",
              "oceanSink",
              "landSink",
              "budgetImbalance"])
        .with_sort({
            "path": ["year"],
            "order": "asc",
        })
        .do()
    )
    addBlock(1)
    print(json.dumps(response, indent=4))
    """
    with open("GCBData.json", "w") as write:
        json.dump(response, write, indent=4)"""
   
def Insert(n):    # A method used to test object insertion
    json_file = open('./InputData/global-carbon-budget20.json')
    data = json.load(json_file);
    
    client.batch.configure(batch_size=30, num_workers=2)  # Configure batch
    with client.batch as batch:  # Initialize a batch process 
    # Imports data from .json file to VDB; each group of insertions given a block in BC
        for (i, d) in enumerate(data):  # Batch import data
            print(f"importing entry: {i+1}")
            properties = {
                "year": d["Year"],
                "fossilFuelandIndustry": d["Fossil-Fuel-And-Industry"],
                "landUseChangeEmissions": d["Land-Use-Change-Emissions"],
                "atmosphericGrowth": d["Atmospheric-Growth"],
                "oceanSink": d["Ocean-Sink"],
                "landSink": d["Land-Sink"],
                "budgetImbalance": d["Budget-Imbalance"],
            }
            batch.add_data_object(
                data_object=properties,
                class_name="GlobalCarbonBudget",
            )
            if i % n == 0:
                addBlock(0)
        # end for
    #end with

    json_file.close()

''' # Leftover queries
print("Query: Print all entries in GlobalCarbonBudget in ascending order by year.")
response = (
    client.query
    .get("GlobalCarbonBudget",
         ["year",
          "fossilFuelandIndustry",
          "landUseChangeEmissions",
          "atmosphericGrowth",
          "oceanSink",
          "landSink",
          "budgetImbalance"])
    .with_sort({
        "path": ["year"],
        "order": "asc",
    })
    .do()
)
addBlock(1)
print(json.dumps(response, indent=4))

with open("GCBData.json", "w") as write:
    json.dump(response, write, indent=4)
    
================================================================================================================

print("Query: Years where the land sink and ocean sink are both greater than 1.5 in ascending order by year.")
response = (
    client.query
    .get("GlobalCarbonBudget",
         ["year",
          "fossilFuelandIndustry",
          "landUseChangeEmissions",
          "atmosphericGrowth",
          "oceanSink",
          "landSink",
          "budgetImbalance"])
    .with_sort({
        "path": ["year"],
        "order": "asc",
    })
    .with_where({
        "operator": "And",
        "operands": [
            {
                "path": ["landSink"],
                "operator": "GreaterThan",
                "valueNumber": "1.5"
            },
            {
                "path": ["oceanSink"],
                "operator": "GreaterThan",
                "valueNumber": "1.5"
            }
        ]
    })
    .do()
)
addBlock(1)
print(json.dumps(response, indent=4))

with open("queryOut.json", "w") as write:
    json.dump(response, write, indent=4)
'''

