import hashlib

def sign_vote(aadhar_number, party_id, timestamp, secret):
    """
    Generate ballot hash and government signature.
    """
    # Ballot hash: combine voter + party + timestamp
    ballot_data = f"{aadhar_number}-{party_id}-{timestamp}"
    ballot_hash = hashlib.sha256(ballot_data.encode()).hexdigest()

    # Government signature: combine with secret key
    signature_data = f"{ballot_hash}-{secret}"
    gov_signature = hashlib.sha256(signature_data.encode()).hexdigest()

    return ballot_hash, gov_signature