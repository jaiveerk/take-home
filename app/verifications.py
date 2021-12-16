# functions to verify input 
REQUIRED_FIELDS = {'title': {}, 'version': {}, 'maintainers[]': {'name': {}, 'email': {}}, 'company': {}, 'website': {}, 'source': {}, 'license': {}, 'description': {}}
ALLOWED_OPERATIONS = set(['EQUALS', 'NOT_EQUALS', 'GREATER_THAN', 'GREATER_THAN_OR_EQUAL', 'LESS_THAN', 'LESS_THAN_OR_EQUAL', 'CONTAINS', 'NOT_CONTAINS'])

# Verify reads/queries
def verify_queries(queries):
    status = True
    reason = ""

    for query in queries:
        components = query.split()

        # now we need see if middle term is in our set of operations
        if components[1] not in ALLOWED_OPERATIONS:
            status = False
            reason += 'invalid operation detected, must be one of ' + str(ALLOWED_OPERATIONS) + f', found {components[1]} instead'

    return status, reason

# Verify writes

def verify_write(input):
    return recursive_verify(REQUIRED_FIELDS, input)

# recursively verify fields
def recursive_verify(required_fields, input):
    valid = True
    reason = ""

    for field in required_fields:
        formatted_field = field.replace("[]", "")
        if formatted_field not in input:
            return False, "missing field " + formatted_field
        if len(required_fields[field]) == 0: # no subfields
            continue

        # otherwise, we've got subobjects

        # does it have a list of subobjects?
        if not field.endswith('[]'): 
            if isinstance(input[field], list): # make sure input is not a list
                return False, "Field " + field + " should not be a list"
            recursive_response = recursive_verify(required_fields[field], input[field])
            valid = valid and recursive_response[0]
            reason = reason + " " + recursive_response[1]
        
        # it's a list of subobjects
        else: 
            if not isinstance(input[formatted_field], list): # make sure input is a list
                return False, "Field " + formatted_field + " must be a list"
            for item in input[formatted_field]:
                recursive_response = recursive_verify(required_fields[field], item)
                valid = valid and recursive_response[0]
                reason = reason + " " + recursive_response[1]

    return valid, reason


# custom verifications (like email, version, etc)
def custom_verify(input):
    valid = True
    reason = ""


    title_verification = verify_title(input)
    valid = valid and title_verification[0]
    reason = reason + title_verification[1]

    version_verification = verify_version(input)
    valid = valid and version_verification[0]
    reason = reason + version_verification[1]

    maintainer_verification = verify_maintainers(input)
    valid = valid and maintainer_verification[0]
    reason = reason + maintainer_verification[1]

    company_verification = verify_company(input)
    valid = valid and company_verification[0]
    reason = reason + company_verification[1]

    website_verification = verify_website(input)
    valid = valid and website_verification[0]
    reason = reason + website_verification[1]

    source_verification = verify_source(input)
    valid = valid and source_verification[0]
    reason = reason + source_verification[1]
    
    license_verification = verify_license(input)
    valid = valid and license_verification[0]
    reason = reason + license_verification[1]

    description_verification = verify_description(input)
    valid = valid and description_verification[0]
    reason = reason + description_verification[1]

    return valid, reason

def verify_title(input_dict):
    if not isinstance(input_dict['title'], str): # I hate checking if(boolean) return boolean, but wanted to include reason
        return False, "Title must be a string"
    return True, ""

def verify_version(input_dict):
    for digit in input_dict['version'].split("."):
        if not digit.isnumeric() or int(digit) < 0:
            return False, "Version must be a number"
    return True, ""

def verify_maintainers(input_dict): 
    valid = True
    reason = ""

    for entry in input_dict['maintainers']:
        if not isinstance(entry['name'], str):
            valid = False
            reason += " Maintainer name must be string"
        
        typeCheck = isinstance(entry['email'], str)
        atCheck = '@' in entry['email'] 
        websiteCheck = entry['email'].endswith(".com") or entry['email'].endswith(".net") or entry['email'].endswith(".edu")
        if not typeCheck or not atCheck or not websiteCheck:
            valid = False
            reason += " Invalid email for maintainer " + entry['name']

    return valid, reason

def verify_company(input_dict):
    # potentially look into some database of recognized companies depending on the use case?
    if not isinstance(input_dict['company'], str): 
        return False, "Company must be a string"
    return True, ""

def verify_website(input_dict):
    # would probably just source a list of all domains that exist and check those for domain_check
    try:
        type_check = isinstance(input_dict['website'], str)
        http_check = input_dict['website'].startswith('http')
        slashSplit = input_dict['website'].split('/')
        domain = slashSplit[2]

        domain_check = domain.endswith('.com') or domain.endswith('.net') or domain.endswith('.gov') or domain.endswith('edu') or domain.endswith('io')
        if not type_check or not http_check or not domain_check: 
            return False, "Invalid website detected"
        return True, ""
    
    except Exception as e:
        return False, "Invalid website detected" # could be caused by index out of bounds or issues with the split

def verify_source(input_dict):
    type_check = isinstance(input_dict['source'], str)
    git_url_check = input_dict['source'].startswith('git@') or input_dict['source'].startswith('git://') or input_dict['source'].endswith('.git') or 'github.com' in input_dict['source']

    if not type_check or not git_url_check:
        return False, "Source/repo is invalid"
    
    return True, ""



def verify_license(input_dict):
    # would prbably want to have a finite set of licenses to check here
    if not isinstance(input_dict['license'], str):
        return False, "License must be a string"
    return True, ""

def verify_description(input_dict):
    if not isinstance(input_dict['description'], str):
        return False, "Description must be a string"
    return True, ""  