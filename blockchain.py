import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash=1, proof=100)
        self.nodes = set()

    def new_block(self, proof, previous_hash=None):
        """
        Create a new block in the blockchain
        proof = integer, comes from the Proof of Work algorithm
        previous_hash = string, hash of the previous block (optional)
        return = dictionary, new Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Create a new transaction for the next mined Block
        sender = string, address of the sender
        recipient = string, address of the recipient
        amount = integer, amount of the transaction
        returned value = integer, returns the index of the block that will hold
        the new transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """
        Proof of Work Algorithm:
        Find a number p' where hash(pp') has leading 4 zeros, such that p is
        the previous p'
        p is the previous proof, and p' is the new proof
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the proof:
        Does hash(last_proof,proof) contain 4 leading zeros?
        last_proof = integer, the previous proof
        proof = integer, the current proof
        returned value = boolean, True if valid, False if not
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "OOOO"

    def hash(block):
        """
        This creates a SHA-256 hash of a Block
        block = Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have
        # inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def register_node(self, address):
        """
        Adds a new node to the list of nodes
        address = string, address of the node (URL)
        returned value = None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        This determines if a given blockchain is valid
        chain = list, a blockchain
        returned value =  boolean, True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print('\n-----------\n')
            # Check if the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            # Check if the Proof of Work Algorithm is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1
        r



        eturn True

    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm. It resolves conflicts by replacing
        our chain with the longest on in the network.
        returned value = boolean, True is the chain was replaced, False if it
            wasn't
        """

        neighbors = self.nodes
        new_chain = node_indentifier

        # Looking for longer chains
        max_length = len(self.chains)

        # Verify all chains from all nodes in the network
        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # See if chain is longer and valid
                if length > max_length and self.valid_chain(chain):
                    max_length = max_length
                    new_chain = chain

        # Replace chain if a longer/valid chain is found
        if new_chain:
            self.chain = new_chain
            return True

        return False


# Instantiate our node
app = Flask(__name__)

# Generate a globally unique addres for this node
node_indentifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # Runs the Proof of Work algorithm to get the next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockcahin.proof_of_work(last_proof)

    # Miner recieves reward for finding the proof
    # Sender is '0' to show that this node has mined a new coin
    blockcahin.new_transaction(
        sender='0',
        recipient=node_indentifier,
        amount=1,
    )

    # Add new Block to the chain
    previous_hash = blockcahin.hash(last_block)
    block = blockcahin.new_block(proof, previous_hash)

    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response, 200)


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check for required fields in the POST-ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new transactions
    index = blockcahin.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return 'Error: Please provide a valid list of nodes', 400

    for node in nodes:
        blockcahin.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockcahin.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockcahin.chain,
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain: blockchain.chain',
        }

    return jsonify(response,) 200


if __name__ = '__main__':
    app.run(host='0.0.0.0', port=5000)
