uri = "mongodb+srv://ootUser:RA6IdLBdYVb9eBvh@cluster1outoftune.suznj28.mongodb.net/?retryWrites=true&w=majority&appName=cluster1outOfTune&ssl=true&tls=true&tlsAllowInvalidCertificates=true"

# Dan: here we create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Dan: here we send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Dan: below is some made up test-data - ALL 3 ARE NEEDED!! can't use only 1 or 2 DTW of them:

# Dan: in case you didn't remember, DTW is an object that wraps a regular object, so that it's in the right format for the database.

# Dan: this is an object for USER_DTW:
a = user_application_state_DTW(userId="anotherTestID2139478239", state_id="1", state_value="active")

# Dan: this is an object for userPERFORMANCE_DTW:
b = userPerformanceDTW("user1_testtt", "test1PerformanceId", "95", "yesterday",[])

# Dan: this is an object for NOTES_DICT_DTW (meaning - the long boring dict {time1: freq1, time2: freq2, ...})
c = performanceNotesDictDTW("test1PerformanceId","yesterday","1440","60")

# Dan: here we connect the NOTES_DICT_DTW into the userPERFORMANCE_DTW:
b.add_performance(c)

# Dan: and here we connect the userPERFORMANCE_DTW into the USER_DTW:
a.addUserPerformance(b)

# Dan: this line is needed to wrap the USER_DTW into the correct mongoDB form:
state_dict = a.to_dict()

# Dan: this object is for the OOT_Database (which is inside the OOT_Cluster, which is inside MongoDB)
db = client.oot_database

# Dan: this object is for the users-table (which is inside the OOT_database, which is inside the OOT_Cluster, which is inside MongoDB)
users = db.users

# Dan: and here we (finally...) upload to db -
print('starting upload ...')
users.insert_one({"user_upload_test1": state_dict})

print('succesfuly added ', a.userId, 'to mongoDB!!!')