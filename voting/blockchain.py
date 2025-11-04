import hashlib, json, time

class Block:
    def __init__(self, index, previous_hash, transactions, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = time.time()
        self.nonce = nonce

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    difficulty = 2
    def __init__(self):
        self.chain = []
        self.unconfirmed_votes = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, "0", [], 0)
        genesis.hash = genesis.compute_hash()
        self.chain.append(genesis)

    def add_vote(self, vote_data):
        self.unconfirmed_votes.append(vote_data)

    def mine(self):
        if not self.unconfirmed_votes:
            return False
        last_block = self.chain[-1]
        new_block = Block(index=last_block.index + 1,
                          previous_hash=last_block.compute_hash(),
                          transactions=self.unconfirmed_votes)
        while not new_block.compute_hash().startswith('0' * Blockchain.difficulty):
            new_block.nonce += 1
        new_block.hash = new_block.compute_hash()
        self.chain.append(new_block)
        self.unconfirmed_votes = []
        return new_block.index