import yaml
from flask import jsonify
from app import verifications, storage
import re

class Handler:

    def __init__(self):
        self.storage = storage.Storage()

    def file_to_dict(self, file):
        # load it into dict
        parsed_yaml=yaml.safe_load(file)
        verified = verifications.verify_write(parsed_yaml)

        if not verified[0]:
            return jsonify({'success': 'false', 'reason': verified[1]})

        # verify its inputs
        custom_verifications = verifications.custom_verify(parsed_yaml)
        if not custom_verifications[0]:
            return jsonify({'success': 'false', 'reason': custom_verifications[1]}) # jsons rather than exceptions to combine reasons


        # if all good, put it into storage, return with status from that -> shouldn't be failure to do so since it's in memory, so 
        # fine with not keeping track of the status of it --> failure at this point likely indicates system failure, which
        # gets caught in main try/catch anyway --> potentially some way to catch that happening? Like if it fails to write to indices
        # or something
        self.storage.write(parsed_yaml)

        return jsonify({'success': 'true'})

    def process_query(self, query):
        # going to want to first verify the query/parse it out here
        subqueries = [item.strip() for item in re.split('\bAND\b|\bOR\b', query)]

        verification_status = verifications.verify_queries(subqueries)

        if not verification_status[0]:
            return jsonify({'success': 'false', 'reason': verification_status[1]}) # returning json rather than throwing exception to combine issues
        
        # otherwise, we're good to begin processing
        apps = []
        for subquery in subqueries:
            apps.extend(self.storage.read(subquery))

        return jsonify({'success': 'true', 'apps': apps})

