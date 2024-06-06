# ------------------------------ Installations (bash!): ---------------------------------------------------------------------------------------

# pip install pymongo


# ------------------------------ Imports (python): -------------------------------------------------------------------


import random
from pymongo import MongoClient
from pymongo.server_api import ServerApi
# from bson import ObjectId


# ------------------------------ Init connection to DB: --------------------------------------------------------------


def connect_to_db():
    uri = "mongodb+srv://ootUser:RA6IdLBdYVb9eBvh@cluster1outoftune.suznj28.mongodb.net/?retryWrites=true&w=majority&appName=cluster1outOfTune&ssl=true&tls=true&tlsAllowInvalidCertificates=true"
    # Dan: here we create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Dan: here we send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("\n### CONNECTED: Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    return client.oot_database


# ------------------------------ CREATE Functions: -------------------------------------------------------------------


def db_create_user(db, user_id):
    try:
        # Dan: this object is for the users-table (which is inside the OOT_database, which is inside the OOT_Cluster, which is inside MongoDB)
        users = db.users
        print('\n### UPLOADING: starting upload to users ...')
        users.insert_one({'_id': user_id, "user_songs": []})
        print('\n### CREATED: succesfuly created ', user_id, 'in mongoDB!')
    except:
        print("User exists")



def db_add_new_song_for_existing_user(db, user_id, user_song_id):
    # Dan: this object is for the users-table (which is inside the OOT_database, which is inside the OOT_Cluster, which is inside MongoDB)
    users = db.users
    # Dan: this object is for the songs_of_user-table
    songs_of_user = db.songs_of_user
    # Dan: here we update a new song which the user sang, in db -
    #print('\n### UPDATING: starting update to users ...')
    #users.update_one({'_id': user_id}, {"$set": {"user_songs": [user_song_id]}})
    users.update_one({'_id': user_id}, {"$push": {"user_songs": user_song_id}})
    #print('\n### UPDATED: succesfuly updated ', user_id, ' with ', user_song_id, 'in mongoDB!')
    #print('\n### UPLOADING: starting upload to songs-of-user ...')
    songs_of_user.insert_one({'_id': user_song_id, "user_performances_id_list": []})
    #print('\n### CREATED: succesfuly created song', user_song_id, 'in mongoDB!')


def db_add_performance_for_existing_user_and_song(db, performance_dtw_id, performance_id, song_name,
                                                  times_and_freqs_dict, dtw_lst, score):
    user_performances = db.user_performances
    songs_of_user = db.songs_of_user
    #print('\n### UPDATING: starting update to users ...')
    songs_of_user.update_one({'_id': performance_dtw_id},
                             {"$push": {"user_performances_id_list": {"$each": [performance_id]}}})
    # print('\n### UPDATED: succesfuly updated ', user_id, ' with ', user_song_id, 'with id:', performance_id,
    #       'in mongoDB!')
    # Dan: this object is for the user-performances-table
    #print('\n### UPLOADING: starting upload to user_performances ...')
    user_performances_dtw_assigned_ID_in_db = user_performances.insert_one(
        {'_id': performance_id, 'song_name': song_name, "performance_notes_dict": times_and_freqs_dict,
         "dtw_lst": dtw_lst, "score": score})
    #print('\n### CREATED: succesfuly created ', performance_dtw_id, 'in mongoDB!')

def generate_random_id(length=10):
  chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  rnd_str = ''.join(random.choice(chars) for _ in range(length))
  return rnd_str


# ------------------------------ FETCH_one Functions: ---------------------------------------------------------------------------------------


def fetch_user_from_db(db, user_id):
    # Dan: this object is for the users-table (which is inside the OOT_database, which is inside the OOT_Cluster, which is inside MongoDB)
    users = db.users
    # Dan: here we fetch a user from the 'users' collection
    #print('\n### FETCHING: Fetching ID #', user_id, ' from table users ...')
    fetched_data = users.find_one({"_id": user_id})
    #print('\n### FETCHED: successfuly fetched the following - ', fetched_data)
    return fetched_data


def fetch_song_of_user(db, user_song_id):
    # Dan: this object is for the songs_of_user-table
    songs_of_user = db.songs_of_user
    # Dan: here we fetch a user_performance from the 'user_performances' collection
    #print('\n### FETCHING: Fetching', user_song_id, 'from  table songs_of_user ...')
    fetched_data = songs_of_user.find_one({"_id": user_song_id})
    #print('\n### FETCHED: successfuly fetched the following - ', fetched_data)
    return fetched_data


def fetch_user_performance(db, performance_id):
    # Dan: this object is for the user-performances-table (which is inside the OOT_database, which is inside the OOT_Cluster, which is inside MongoDB)
    user_performances = db.user_performances
    # Dan: here we fetch a user_performance from the 'user_performances' collection
    #print('\n### FETCHING: Fetching ID #', performance_id, ' from  table user_performances ...')
    fetched_data = user_performances.find_one({"_id": performance_id})
    #print('\n### FETCHED: successfuly fetched the following - ', fetched_data)
    return fetched_data

def does_user_exist(db, user_id):
  #print('\n### FETCHING: Fetching ID #', user_id, ' from table users ...')
  fetched_data = db.users.find_one({"_id": user_id})
  if fetched_data:
    #print('\n### FETCHED: user',user_id,'exists in db!')
    return True
  #print('\n### DID NOT FETCH: user',user_id,"doesn't exists in db... :(")
  return False


# ------------------------------ FETCH_all Functions: ---------------------------------------------------------------------------------------


def fetch_every_song_sang_by_user(db, user_id):
    songs_of_user = db.songs_of_user
    #print('\n### FETCHING: Fetching every song sang by', user_id, '...')
    fetched_data = list(songs_of_user.find({"_id": {"$regex": '_' + user_id}}))
    #print('\n### FETCHED: successfuly fetched every song which was sang by', user_id, ':\n', fetched_data)
    return fetched_data


def fetch_every_user_performance(db, song_name, user_id):
    user_performances = db.user_performances
    fetch_id = song_name + '_' + user_id
    songs_of_user = fetch_song_of_user(db, fetch_id)
    performances_ids = songs_of_user['user_performances_id_list']
    fetched_data = []
    #print('\n### FETCHING: Fetching every performance of', song_name, 'sang by', user_id, '...')
    for performance_id in performances_ids:
        fetched_data.append(user_performances.find_one({"_id": performance_id}))
    #print('\n### FETCHED: successfuly fetched every performance for', song_name, 'sang by', user_id, ':\n',
    #      fetched_data)
    return fetched_data


# ------------------------------ REMOVE Functions: ---------------------------------------------------------------------------------------


def db_remove_performance(db, performance_id, song_of_user_id):
    res = db.user_performances.delete_many({"_id": performance_id})
    #print(f"\n### REMOVED performance {performance_id}!")
    # remove performance_id from performance_ids (in songs_of_user table):
    db.songs_of_user.update_one({'_id':song_of_user_id} ,{"$pull" : {"user_performances_id_list": performance_id}})
    #print(f"\n### REMOVED performance_id {performance_id} from document {song_of_user_id} in table songs_of_user!")
    
def db_deep_remove_song_of_user(db, song_name, user_id):
    # (deep-deletion: it doesn't only remove the song_of_user, but also all of it's matching user_performances)
    # first, remove every performance the song_of_user from db:
    user_performances = db.user_performances
    usersong_id = song_name
    songs_of_user = fetch_song_of_user(db,usersong_id)
    if songs_of_user is not None and len(songs_of_user['user_performances_id_list']) > 0:
      performances_ids = songs_of_user['user_performances_id_list']
      #print('\n### REMOVING: First, removing every performance of',song_name,'sang by',user_id,'...')
      removed_performances_counter = 0
      for performance_id in performances_ids:
        #print(f'\n### REMOVING #{removed_performances_counter}, with id {performance_id}...')
        db_remove_performance(db, performance_id, usersong_id)
        removed_performances_counter += 1
    # then, remove the actual song_of_user from db:
    res = db.songs_of_user.delete_many({"_id": usersong_id})
    #print(f"\n### REMOVED user_song {song_name} by {user_id}, and all of it's performances!")
    # remove song from user_songs (in users table):
    db.users.update_one({'_id':user_id} ,{"$pull" : {"user_songs": song_name}})
    # print(f"\n### REMOVED song {song_name} from document {user_id} in users!")

def db_deep_remove_user(db,user_id):
    # (deep-deletion: it doesn't only remove the user, but also all of it's matching songs_of_user, and all of their user_performances)
    # first, remove every song_of_user from db (and all of it's performances):
    user_songs = list(db.songs_of_user.find({"_id": {"$regex" : '_'+user_id}}))
    #print('\n### REMOVING: Starting to remove every song',user_id,'has sang...')
    for user_song in user_songs:
      db_deep_remove_song_of_user(db, user_song['_id'], user_id)
    # secondly, remove the user itself:  
    db.users.delete_many({"_id": user_id})
    #print(f"\n### REMOVED user {user_id}, and all of it's songs and performances!")

    
# ------------------------------ EXAMPLES OF USAGE: ---------------------------------------------------------------------------------------

# some mock data
# user_id = "some_user923984"
# performance_id = generate_random_id()
# song_name = "Hallelujah"
# user_song_id = song_name + '_' + user_id
# times_and_freqs_dict = {'timestamp1': 'freq1', 'timestamp2': 'freq2', 'timestamp3': 'freq3', 'timestamp4': 'freq4'}
# dtw_lst = [('a', '_a'), ('b', '_b'), ('c', '_c'), ('d', '_d')]

# # 0. INIT DB instance (uncomment to use):

# db = connect_to_db()

# # 1. CREATING examples (uncomment to use):

# # --- creating a new user in db:
# db_create_user(db, user_id)
# # --- adding a song for a user (not a performance yet!):
# db_add_new_song_for_existing_user(db, user_id, user_song_id)
# # --- adding a performance for a song for a user:
# db_add_performance_for_existing_user_and_song(db, user_song_id, performance_id, song_name, times_and_freqs_dict, dtw_lst, 95)

# # 2. FETCHING examples (uncomment to use):

# # --- fetch user:
# fetch_user_from_db(db, user_id)
# # --- fetch a specific user_song:
# fetch_song_of_user(db, user_song_id)
# # --- fetch EVERY user_song (for user_id):
# fetch_every_song_sang_by_user(db,user_id)
# # --- fetch a specific user_performance:
# fetch_user_performance(db, performance_id)
# # --- fetch EVERY user_performance (for song_name, user_id):
# fetch_every_user_performance(db, song_name, user_id)

# # 3. REMOVING examples (uncomment to use):

# # --- Remove a single performance:
# db_remove_performance(db, performance_id)
# # --- DEEP-Remove song_of_user (meaning: also remove all of the song's performances)
# db_deep_remove_song_of_user(db, user_song_id, user_id) # note: user_song_id == song_name+'_'+user_id
# # --- DEEP-Remove user (meaning: also remove from db all of it's songs_of_user, and all of their song_performances)
# db_deep_remove_user(db, user_id)

# # 4. MORE:

# # --- check if user exists:
# does_user_exist(db, user_id)
