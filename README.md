## Basic Layout
The app is composed of seven components, each with a unique purpose towards the goal of mocking a metadata store in memory. First, is the `__init__ ` file, which allows Python to package the application as a single, cohesive bundle. This file can be left empty, but I've used it to define my Flask application.

The Flask application can itself be found in routes.py, where the two routes for the two primary functions of the app (read and write) exist. 


### Writes/uploads
The `upload` route takes a YAML file in the body of the request, which means requests made through cURL can be formatted like
`curl -X POST -F 'data=@tests/test.yaml' localhost:5000/upload`

Once the legitimacy of the request is verified (by ensuring that the request contains a non-empty file ending in .yaml or .yml), the router sends the file to a "handler" defined in `handler.py`. The handler is responsible for handling input, which means it's responsible for processing user input, verifying the input, and acting upon it. In the case of a write, that means first converting the YAML into a python dictionary. Next comes the verification process, which is defined in a separate component to keep the design as modular as possible, `verifications.py`. The first verification performs a recursive search in the dictionary to ensure that all `REQUIRED_FIELDS` are present, are nested as required, and are correctly defined as lists or not. Next, a set of `custom_verifications` are performed, where developers on this server can add verifications for each field that may be present/required in the input. If any of these checks fail, the write fails.

Once the input is verified, the handler writes the object to its `storage` object, an instance of the `Storage` class defined in `storage.py`.

To manage items in this fake database, I took a cue from actual databases and added various optimizations to improve performance for queries on specific attributes that I thought would frequently be queried by a user of this database given the initial set of attributes each object would have. There are three kinds of indices/performance enhancers I added, all of which are defined in `indices.py` -- an "equals" index, which maps values for an attribute to the apps that have an exact match for that attribute, a "contains" index, which maps every word/whitespace-separated-string across the entire database for that attribute to the apps that contain that word, and then an "order", which maintains a list of the apps sorted according to the attribute specified, which has O(log(n)) access for equality on those attributes but also for queries where the user wishes to see all apps with a value greater or less than the input value (rather than needing to check every single application). The write to these orders uses a binary search to find the index where items should be written to. The use case that inspired this was for a user who may want to see all apps past a certain version. 

The indices don't contain the entire app, but rather, references to them in the form of an `id`, which is assigned to each app as it's written to storage through the `counter` variable. This `id` is the index of the application in the "master" list, which is the foundational structure of this database -- just a list of all the applications that have been added. After the indices have been processed, the dictionary created from the original YAML is added to master at index `counter`, which then gets incremented for the next app.

### Reads
Queries are passed into the `/read/QUERY` route and are formatted as `attribute operation value`, resulting in cURLs that look like:
`curl -X GET localhost:5000/get/version%20GREATER_THAN%201.0.1` where the `%20`s are just URL-encoded spaces. After the function defined wuth the route verifies that there is indeed a query present, it passes the query to the same `handler` that was used to handle writes. This was intentional, as I wanted to maintain a single `storage` object for both reads and writes, which meant that both reads and writes would have to go into the same `handler` to be able to access the same instance of `storage`. 

Once the handler receives the query, it uses functions in `verifications.py` to perform a basic verification, which at the moment just consists of making sure that the query is structured correctly and that the operation being performed is legal/one of the allowed operations.

I had originally intended to allow for compound queries, but I didn't get the chance to impement them fully due to the timeframe provided (more on that below). Nonetheless, the intention was for the handler to be able to process multiple queries, the first step of which would be to split each query by "AND"s and "OR"s. If I had completed this implementation, I would want to do some sort of recursive splitting of queries and process those queries one by one, so that if I had a query that looked like 
`(version EQUALS 0.1 AND maintainer.name EQUALS jaiveer) OR (version EQUALS 0.2 AND maintainer.name EQUALS jaiveer2)`, the recursive splitter would find the intersection of apps where version equals 0.1 and name is jaiveer and then union that with the intersection of apps where the version is 0.2 and the maintainer's name is jaiveer2. 

Nonetheless, after verification, once the handler has broken down the query into subqueries, the results of all the subqueries are unioned together (treating all the subqueries as being joined by ORs, since again, I didn't finish that). 

As for processing the queries, that is once again delegated by the handler to the storage, since the storage is what has the data that the read is looking for. First, the query is broken down into attribute, operation, and query, and the function corresponding to the operation is called on the attribute and the value using `self.__getattribute__(operation)(attribute, value)`.

Each operation first checks if there is an index built for that operation for that attribute (so an equals/order for `equals`, an order for `greater than`/`less than`, and a "contains" for `contains`). If so, it queries the index for all matching apps, and returns. Otherwise, if there is no index, it performs a recursive search for that operation (or for its inverse and returns all the other elements, so for instance, not equals just calls equals and then returns the indices of all apps that weren't in the output of equals, which defeats the purpose of optimizing for Big-Oh notation, but is practically pretty fast, plus, saved me writing code... probably a better way to do it than the brute force-y way that I did) on the master list and returns all matching items. 


## Why flask?
- Graceful error handling built in (won't crash server)
- Quick to get something up and running
- Restart/debug functionality built in so I don't have to press `ctrl`+`c` every time I fix a typo (which happens more than I'd like to admit)



## General Design Decisions
My design was primarily informed by the principle that I wanted to make it as easy as possible to add new fields to applications' metadata whether those fields were required or not. This principle informed how I managed writes, reads, and searches.

For writes, attribute-specific verifications and indices are all defined by the developer. As a result, users still have the option to include additional fields in their YAMLs -- they just won't be verified or checked in any way. Instead, they'll just be included as part of the dictionary that gets written to the master list. If the situation changes though and all apps require some new attribute, it becomes easy to require this new attribute in all future writes by adding the attribute to the list of required attributes and then adding a function to verify the attribute (if this is necessary at all) to the `custom_verifications()` function. Throughout this process, the `storage` object sees no changes -- those all instead take place on the side of verifications. Similarly, if developers wish to add an index for any new attribute, they can just add that to the list of indexed attributes and construct the index for whichever operation they want. Once again, no code in `storage` would have to change to include this change.

This carries on into the reads/searches. I intentionally excluded any check/verification on the attributes that users include in their queries in because I wanted to make it easy for them to query on attributes that aren't a part of any specific/limiting list. Once again, if a user chooses to include a new attribute in their YAML and then query for it, the recursive searches will look for all values that match that attribute. If the attribute exists at multiple levels, like the `spec` attribute for Kubernetes resources, the searches will only return values for the attribute at the exact path that the user specifies. If no such attribute exists at that path, the recursive searcher will throw a KeyError and return a blank list, resolving the case where one sub-object may have certain fields while another sub-object of the same intended type does not. This is all to make sure that we leave the flexibility to the user to specify how they want to organize their data as long as they include what we require. Again, the `storage` code wouldn't have to change for this, since the recursive searchers (defined in `recursive-searchers.py`) would take care of the logic of checking the entire object -- storage just sees a request to go look for that attribute, and the outcome of looking for that attribute. If a field were to be indexed but not required, though, `storage` once again would not have to change, since it already looks in its `index` to see if the attribute being queried for has an index, and if it does, performs standard logic based on the required structure for each index.



As for which indices I initially created, I had the following:
`title_contains`, `version_order`, `maintainers.email_equals`, `company_equals`, `website_equals`, `source_equals`, `license_equals`, `description_contains`

I made `contains` indices for title and description, since I imagine users would be more interested in titles or descriptions that CONTAIN certain words rather than exact matches for titles/descriptions. Once again, though, they still can perform that query if necessary.
As was described above, I made an `order` index for versions because versions are something that have a clear/natural order to them, and to allow for improved performance when users would query for equality or comparison.
Next, I made an index for maintainer email but not name. I figured names could be repeated, and if someone wanted to uniquely identify a developer, they'd be better off using the email address anyway. Users can still query by name, if they wanted to see ALL apps made by "John Smith" or even better, all apps with a maintainer whose name contained "John". 
I then made an `EQUALS` index for company, wbesite, source, and license, since those are all attributes where users would likely be interested in exact values when they query for them.



## Things I Would Have Liked to Build 
- (quite obviously) Concurrency. I haven't written concurrent/multithreaded code since my junior year of college, and while I remember being pretty comfortable with it, I didn't think I would be able to pick it up quickly enough for this exercise. I was considering building everything on top of Spark + stored everything in a Spark dataframe to allow for some degree of concurrency in the searches, but that would have removed a lot of my ability to demonstrate design choices/decisions just for the sake of showing I'm basically competent at a framework. Nonetheless, I haven't written multithreaded code as part of my job/internships, but I truly do look forward to the possibility of adding it back to my arsenal.

- More tests, comprehensive tests, unit tests (my code was tested manually during construction by manual inputs into the server and seeing if it worked the way I wanted)

- Several opportunities to remedy repeated code --> code to perform verifications, could just have one generic checkType function, but wanted
to build in a tempalte to be able to add more sophisticated verifications if necessary for each title
- Same idea for adding to indices -- could have generic function to add app id to value for all the 'equals' or 'contains' indices... would have required some more reflection-esque tactics but would've saved a decent amount of code

- One thing I didn't get to finish - processing/testing multiple queries --> I added logic to split on ands/ors and process multiple queries,
but would need to figure out logic to differentiate between "AND" and "OR" --> right now treating everything as an or, plus no way to support embedded/complex queries like mentioned above... so would've liked to add that

- Duplicate checking? Would probably check existing repo/name/version before writing but then do something to just overwrite
the old one, but also duplicate fields -- say someone has two "maintainers" fields -- haven't checked what would happen there/built in any logic to handle it, I don't think...
- Mock some sort of auth requirement to secure the datastore 
- Some sort of specialized query to return everything/logic to allow for that - could be as simple as a get request on `/` which would just return all of master, but didn't build it out