import hashlib

def generate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def sign_vote(voter_id, party_id, timestamp, secret='private_key'):
    raw_data = f"{voter_id}-{party_id}-{timestamp}"
    ballot_hash = generate_hash(raw_data)
    signature = generate_hash(ballot_hash + secret)
    return ballot_hash, signature

