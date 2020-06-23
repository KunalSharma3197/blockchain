
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 20:09:37 2020

@author: test
"""
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
class BlockChain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.Create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
    
    def Create_block(self, proof, previous_hash):
        block = {'index' : len(self.chain) + 1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previous_hash' : previous_hash,
                 'transactions' : self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
              check_proof = True
            else :
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1 
        while block_index < len(chain):
            block = chain[block_index]
            previous_proof = previous_block['proof']
            proof = block['proof']
            if block['previous_hash'] != self.hash(previous_block):
                return False
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
            return True
    def add_transaction(self, sender,  receiver, amount):
        self.transactions.append({'sender' : sender,
                                  'receiver' : receiver,
                                  'amount' : amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200 :
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain) :
                    max_length = length 
                    longest_chain = chain
                if longest_chain:
                    self.chain = longest_chain
                    return True
                return False
        
        
app = Flask(__name__)

node_address = str(uuid4()).replace('-','')

blockchain = BlockChain()

@app.route('/mine_block', methods = ['GET'])

def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_hash = blockchain.hash(previous_block)
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    blockchain.add_transaction(sender = node_address, receiver = 'Papa', amount = 1)
    block = blockchain.Create_block(proof, previous_hash)
    Response = {'message' : 'Congratulation, you just mined a block!',
                'index' : block['index'],
                'timestamp': block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash'],
                'transactions' : block['transactions']}
    
    return jsonify(Response), 200

@app.route('/get_chain', methods = ['GET'])

def get_chain():
    Response = {'chain' : blockchain.chain,
                 'length' : len(blockchain.chain)}
    return jsonify(Response), 200

        
        
@app.route('/is_valid', methods = ['GET'])

def is_valid():
    validity = blockchain.is_chain_valid(blockchain.chain)
    if validity :
        Response = {'message' : 'All good Block Chain is Valid'}
    else :
        Response = {'message' : 'Block Chain is invalid'}
    return jsonify(Response), 200

@app.route('/add_transactions', methods = ['POST'])

def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of transaction are missing!',400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message' : f'This transaction will be added to Block {index}'}
    return jsonify(response), 201 

@app.route('/connect_nodes', methods = ['POST'])

def connect_nodes():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None :
        return 'No node', 400
    for node in nodes:
        blockchain.add_node(node)
    Response = {'message' : 'All the nodes are now connected. The Kunalcoin blockchain now contains: ',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(Response), 201
   
@app.route('/replace_chan', methods = ['GET'])

def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        Response = {'message' : 'Chain is replaced by longest chain',
                    'new_chain': blockchain.chain}
    else :
        Response = {'message' : 'Chain is already the longest one',
                    'actual_chain': blockchain.chain}
    
    return jsonify(Response),200

app.run(host = '0.0.0.0', port = 5003)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        