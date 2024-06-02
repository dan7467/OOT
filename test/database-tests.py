import random as rnd
import db_persistence_layer as pl

def generate_rnd_str(length=10):
  chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  rnd_str = ''.join(rnd.choice(chars) for _ in range(length))
  return rnd_str

def generate_rnd_n(a, b):
    # returns a random integer n such that a <= n < b
    return rnd.randint(a, b-1)

def test_create_user_and_does_user_exist(db):
    n = generate_rnd_n(5,12)
    user_id = "test_user_"+generate_rnd_str(n)
    pl.db_create_user(db, user_id)
    assert pl.does_user_exist(db, user_id)

def test_create_user_and_fetch(db):
    n = generate_rnd_n(5,12)
    user_id = "test_user_"+generate_rnd_str(n)
    pl.db_create_user(db, user_id)
    assert pl.fetch_user_from_db(db, user_id)


def test_create_user_fetch_and_remove(db):
    n = generate_rnd_n(5,12)
    user_id = "test_user_"+generate_rnd_str(n)
    pl.db_create_user(db, user_id)
    pl.db_deep_remove_user(db, user_id)
    assert not pl.does_user_exist(db, user_id)

def test_create_user_add_song_and_fetch_song(db):
    n1 = generate_rnd_n(5,12)
    n2 = generate_rnd_n(5,12)
    user_id = "testUser"+generate_rnd_str(n1)
    song_id = "testSong"+generate_rnd_str(n2)
    user_song_id = user_id + '_' + song_id
    pl.db_add_new_song_for_existing_user(db, user_id, user_song_id)
    assert pl.fetch_song_of_user(db, user_song_id)
def test_create_user_add_song_remove_song_and_fetch_song(db):
    n1 = generate_rnd_n(5,12)
    n2 = generate_rnd_n(5,12)
    user_id = "testUser"+generate_rnd_str(n1)
    song_id = "testSong"+generate_rnd_str(n2)
    user_song_id = user_id + '_' + song_id
    pl.db_add_new_song_for_existing_user(db, user_id, user_song_id)
    pl.db_deep_remove_song_of_user(db, user_id, user_song_id)
    assert not pl.fetch_song_of_user(db, user_song_id)

def test_create_user_add_performance_and_fetch_performance(db):
    n1 = generate_rnd_n(5,12)
    n2 = generate_rnd_n(5,12)
    user_id = "testUser"+generate_rnd_str(n1)
    song_id = "testSong"+generate_rnd_str(n2)
    performance_id = "testPerformance" + generate_rnd_str()
    user_song_id = user_id + '_' + song_id
    times_and_freqs_dict = {'timestamp1': generate_rnd_n(0,600), 'timestamp2': generate_rnd_n(0,600), 'timestamp3': generate_rnd_n(0,600), 'timestamp4': generate_rnd_n(0,600)}
    dtw_lst = [('a', generate_rnd_str()), ('b', generate_rnd_str()), ('c', generate_rnd_str()), ('d', generate_rnd_str())]
    pl.db_add_new_song_for_existing_user(db, user_id, user_song_id)
    pl.db_add_performance_for_existing_user_and_song(db, user_song_id, performance_id, song_id, times_and_freqs_dict, dtw_lst, generate_rnd_n(60,100))
    assert pl.fetch_user_performance(db, performance_id)

def test_create_user_add_performance_remove_performance_and_fetch_performance(db):
    n1 = generate_rnd_n(5,12)
    n2 = generate_rnd_n(5,12)
    user_id = "testUser"+generate_rnd_str(n1)
    song_id = "testSong"+generate_rnd_str(n2)
    performance_id = "testPerformance" + generate_rnd_str()
    user_song_id = user_id + '_' + song_id
    times_and_freqs_dict = {'timestamp1': generate_rnd_n(0,600), 'timestamp2': generate_rnd_n(0,600), 'timestamp3': generate_rnd_n(0,600), 'timestamp4': generate_rnd_n(0,600)}
    dtw_lst = [('a', generate_rnd_str()), ('b', generate_rnd_str()), ('c', generate_rnd_str()), ('d', generate_rnd_str())]
    pl.db_add_new_song_for_existing_user(db, user_id, user_song_id)
    pl.db_add_performance_for_existing_user_and_song(db, user_song_id, performance_id, song_id, times_and_freqs_dict, dtw_lst, generate_rnd_n(60,100))
    pl.db_remove_performance(db, performance_id, user_song_id)
    assert not pl.fetch_user_performance(db, performance_id)

if __name__ == '__main__':
    db = pl.connect_to_db()
    print('\n# Database tests starting...\n')
    print(f'\n# Test_1: User creation\n')
    test_create_user_and_does_user_exist(db)
    print(f'\n# Test_2: User creation\n')
    test_create_user_and_does_user_exist(db)
    print(f'\n# Test_3: User creation\n')
    test_create_user_and_does_user_exist(db)
    print(f'\n# Test_4: User creation and fetching\n')
    test_create_user_and_fetch(db)
    print(f'\n# Test_5: User creation and fetching\n')
    test_create_user_and_fetch(db)
    print(f'\n# Test_6: User creation and fetching\n')
    test_create_user_and_fetch(db)
    print(f'\n# Test_7: User creation, fetching, removal\n')
    test_create_user_fetch_and_remove(db)
    print(f'\n# Test_8: User creation, fetching, removal\n')
    test_create_user_fetch_and_remove(db)
    print(f'\n# Test_9: User creation, fetching, removal\n')
    test_create_user_fetch_and_remove(db)
    print(f'\n# Test_10: Song creation and fetching\n')
    test_create_user_add_song_and_fetch_song(db)
    print(f'\n# Test_11: Song creation and fetching\n')
    test_create_user_add_song_and_fetch_song(db)
    print(f'\n# Test_12: Song creation and fetching\n')
    test_create_user_add_song_and_fetch_song(db)
    print(f'\n# Test_13: Song creation, fetching and removal\n')
    test_create_user_add_song_remove_song_and_fetch_song(db)
    print(f'\n# Test_14: Song creation, fetching and removal\n')
    test_create_user_add_song_remove_song_and_fetch_song(db)
    print(f'\n# Test_15: Song creation, fetching and removal\n')
    test_create_user_add_song_remove_song_and_fetch_song(db)
    print(f'\n# Test_16: Performance creation and fetching\n')
    test_create_user_add_performance_and_fetch_performance(db)
    print(f'\n# Test_17: Performance creation and fetching\n')
    test_create_user_add_performance_and_fetch_performance(db)
    print(f'\n# Test_18: Performance creation and fetching\n')
    test_create_user_add_performance_and_fetch_performance(db)
    print(f'\n# Test_19: Performance creation, fetching and removal\n')
    test_create_user_add_performance_remove_performance_and_fetch_performance(db)
    print(f'\n# Test_20: Performance creation, fetching and removal\n')
    test_create_user_add_performance_remove_performance_and_fetch_performance(db)
    print(f'\n# Test_21: Performance creation, fetching and removal\n')
    test_create_user_add_performance_remove_performance_and_fetch_performance(db)

    print('\n# All database-tests passed!\n')