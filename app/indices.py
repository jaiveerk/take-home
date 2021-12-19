import string

class Index:
    INDEXED_ATTRS = ['title_contains', 'version_order', 'maintainers.email_equals', 'company_equals', 'website_equals', 'source_equals', 'license_equals', 'description_contains']

    punctuation_remover = str.maketrans('', '', string.punctuation)


    # assume that we want to take the space to optimize on EVERY variable for queries
    title_contains_index = {}
    version_order = []
    maintainers_email_equals_index = {} # might need some logic for the WHERE maintainers are multiple... for now, assign each maintainer to have all their App IDs
    company_equals_index = {}
    website_equals_index = {}
    source_equals_index = {}
    license_equals_index = {}
    description_contains_index = {} 

    def process(self, input):
        self.add_to_title_contains_index(input)
        self.add_to_versions(input)
        self.add_to_maintainers_index(input)
        self.add_to_company_equals_index(input)
        self.add_to_website_equals_index(input)
        self.add_to_source_equals_index(input)
        self.add_to_license_equals_index(input)
        self.add_to_description_contains_index(input)
    
    def add_to_title_contains_index(self, input):
        # clean up words --> lowercase, without punctuation
        words = set([word.lower().translate(self.punctuation_remover) for word in input['title'].split()])

        # process each word
        for word in words:
            if not word in self.title_contains_index:
                self.title_contains_index[word] = []
            self.title_contains_index[word].append(input['id'])
    
    def add_to_versions(self, input):
        index_to_add = self.get_ordered_index('version', input['version'])
        self.version_order.insert(index_to_add, (input['version'], input['id']))
        # print(self.version_order)

    def get_ordered_index(self, attr, value): # aka binary search
        order = self.__getattribute__(attr + '_order')
        if len(order) == 0:
            return 0

        left_pointer = 0
        right_pointer = len(order)-1
        
        while left_pointer <= right_pointer:
            mid_pointer = left_pointer + int((right_pointer - left_pointer) / 2)
            if order[mid_pointer][0] == value:
                return mid_pointer
   
            if value < order[mid_pointer][0]:
                right_pointer = mid_pointer - 1
            else:
                left_pointer = mid_pointer + 1

        return left_pointer

    

    def add_to_maintainers_index(self, input):
        for object in input['maintainers']: 
            email = object['email']
            if not email in self.maintainers_email_equals_index:
                self.maintainers_email_equals_index[email] = []
            
            self.maintainers_email_equals_index[email].append(input['id'])
    
    def add_to_company_equals_index(self, input):
        company = input['company'].lower() # company name's punctuation could be valuable

        if not company in self.company_equals_index:
            self.company_equals_index[company] = []
        
        self.company_equals_index[company].append(input['id'])

    def add_to_website_equals_index(self, input):
        website = input['website'].lower()

        if not website in self.website_equals_index:
            self.website_equals_index[website] = []
        
        self.website_equals_index[website].append(input['id'])
    
    def add_to_source_equals_index(self, input):
        source = input['source'].lower()

        if not source in self.source_equals_index:
            self.source_equals_index[source] = []
        
        self.source_equals_index[source].append(input['id'])

    def add_to_license_equals_index(self, input):
        license = input['license'].lower()

        if not license in self.license_equals_index:
            self.license_equals_index[license] = []
        
        self.license_equals_index[license].append(input['id'])

    def add_to_description_contains_index(self, input):
        # clean up words --> lowercase, without punctuation
        words = set([word.lower().translate(self.punctuation_remover) for word in input['description'].split()])

        # process each word
        for word in words:
            if not word in self.description_contains_index:
                self.description_contains_index[word] = []
            self.description_contains_index[word].append(input['id'])
        